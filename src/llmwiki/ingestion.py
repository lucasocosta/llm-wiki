"""Ingestion engine: extract Trechos, compute the work queue, stamp writes.

The queue is *computed* by comparing the declared Sources with the state of the
wiki, never persisted, so ingestion is resumable on any machine and two people
ingesting in parallel produce no merge conflict in a derived state file
(ADR 0002, ticket 05). A Trecho is "done" when its hash already appears in the
``trechos`` provenance of some page in the wiki.

The write-page *tool* stamps the contribution — ``generated`` (an ISO date),
``generated_by``, and the contributing Trecho hash — because the CLI, not the
worker, knows which Trecho is being processed. If the record depended on the
model remembering, one omission would make the page look clean forever (spec).
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field, replace
from pathlib import Path

from llmwiki.extract import (
    ExtractionError,
    extract_markdown,
    extract_text,
)
from llmwiki.manifest import Manifest, Source
from llmwiki.okf.page import RESERVED_FILES, Page, read_page, write_page
from llmwiki.reference import ensure_reference
from llmwiki.provenance import code_file_version, validate_code_pin
from llmwiki.trecho import Trecho, limit_trechos

GENERATED_BY = "llm-wiki"
# Minimum extracted characters per page/Trecho below which a Source is refused
# (ticket 07). Overridable per call; the default is a low, conservative floor.
MIN_CHARS_PER_UNIT = 20

# The Source types this engine can turn into Trechos.
INGESTIBLE_TYPES = ("markdown", "text", "pdf", "code")


class IngestionError(Exception):
    pass


@dataclass
class WorkItem:
    """What the CLI hands the worker: the extracted Trecho plus a shortlist."""

    trecho: Trecho
    shortlist: list[dict] = field(default_factory=list)

    def to_payload(self) -> dict:
        return {
            "source_id": self.trecho.source_id,
            "trecho_hash": self.trecho.hash,
            "trecho_index": self.trecho.index,
            "anchor": self.trecho.anchor,
            "text": self.trecho.text,
            "shortlist": self.shortlist,
        }


def _source_path(manifest: Manifest, source: Source) -> Path:
    return (manifest.sources_path / source.location).resolve()


def _source_hash_and_relpath(manifest: Manifest, source: Source) -> tuple[str, str]:
    """Return (content_hash, rel_path) for a Source's mirror provenance.

    Single-file Sources hash their original bytes. Code Sources
    have no single content hash; their provenance key is the commit SHA
    (handled by the caller), so this returns an empty hash and the code path.
    """
    import hashlib

    if source.type == "code":
        base = code_base_path(manifest, source)
        try:
            rel_path = base.relative_to(manifest.root.resolve()).as_posix()
        except ValueError:
            rel_path = str(base)  # external checkout outside the repo
        return "", rel_path

    path = _source_path(manifest, source)
    if not path.exists():
        raise IngestionError(f"source file not found for {source.id!r}: {path}")
    rel_path = path.relative_to(manifest.root.resolve()).as_posix()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest, rel_path


def extract_source(manifest: Manifest, source: Source) -> list[Trecho]:
    """Keep natural boundaries, subdividing only units above the wiki budget."""
    return limit_trechos(_extract_natural_source(manifest, source), manifest.max_trecho_chars)


def _extract_natural_source(manifest: Manifest, source: Source) -> list[Trecho]:
    """Extract the Trechos for one Source, applying the extractor for its type."""
    if source.type == "markdown":
        text = _source_path(manifest, source).read_text(encoding="utf-8")
        trechos = extract_markdown(source.id, text)
    elif source.type == "text":
        text = _source_path(manifest, source).read_text(encoding="utf-8")
        trechos = extract_text(source.id, text)
    elif source.type == "pdf":
        from llmwiki.extract import extract_pdf

        trechos = extract_pdf(source.id, _source_path(manifest, source))
        return trechos  # extract_pdf enforces its own per-page minimum
    elif source.type == "code":
        return extract_code_source(manifest, source)
    else:
        raise IngestionError(
            f"source {source.id!r} has type {source.type!r} not handled here"
        )
    _reject_thin(source, trechos)
    return trechos


def code_base_path(manifest: Manifest, source: Source) -> Path:
    """Where a code Source's files live.

    External code (declared with a repository + commit) is pinned by SHA and
    read in place, never copied into the repo (ticket 08): its ``location`` is
    an absolute or repo-relative path to the checkout. Local code lives under
    the sources directory.
    """
    loc = Path(source.location)
    if source.repository:
        # External: location is a path to the pinned checkout.
        return loc if loc.is_absolute() else (manifest.root / loc).resolve()
    return (manifest.sources_path / source.location).resolve()


def scan_code(manifest: Manifest, source: Source):
    """Scan a code Source against its allowlist. Returns a CodeScan."""
    from llmwiki.code import scan_code_source

    base = code_base_path(manifest, source)
    if not base.exists():
        raise IngestionError(f"code source path not found for {source.id!r}: {base}")
    scan = scan_code_source(base, source.allowlist)
    if source.repository:
        try:
            validate_code_pin(base, source.commit, scan.included)
        except ValueError as exc:
            raise IngestionError(f"source {source.id!r}: {exc}") from exc
    return scan


def extract_code_source(manifest: Manifest, source: Source) -> list[Trecho]:
    from llmwiki.code import extract_code_file, order_leaves_first

    scan = scan_code(manifest, source)
    base = code_base_path(manifest, source)
    ordered = order_leaves_first(base, scan.included)
    trechos: list[Trecho] = []
    for i, path in enumerate(ordered):
        trecho = extract_code_file(source.id, path, i)
        trechos.append(replace(trecho, source_path=path.relative_to(base).as_posix()))
    return trechos


def _reject_thin(source: Source, trechos: list[Trecho], minimum: int = MIN_CHARS_PER_UNIT) -> None:
    for t in trechos:
        if len(t.text.strip()) < minimum:
            raise ExtractionError(
                f"source {source.location!r} produced too little text "
                f"(Trecho {t.index} has {len(t.text.strip())} chars, "
                f"minimum {minimum}); refusing"
            )


def done_trecho_hashes(bundle_root: Path) -> set[str]:
    """Every Trecho hash already stamped on a page in the wiki."""
    done: set[str] = set()
    for page_file in _iter_concept_pages(bundle_root):
        page = read_page(page_file)
        for h in page.frontmatter.get("trechos", []) or []:
            done.add(h)
    return done


def _iter_concept_pages(bundle_root: Path):
    if not bundle_root.exists():
        return
    for path in sorted(bundle_root.rglob("*.md")):
        if path.name in RESERVED_FILES:
            continue
        yield path


def known_concept_ids(bundle_root: Path) -> set[str]:
    """Every concept id currently present in the wiki (for the no-dead-link rule).

    Includes the page being written when called after the write; callers that
    validate a new page add its id explicitly.
    """
    from llmwiki.okf.page import concept_id_from_path

    ids: set[str] = set()
    for page_file in _iter_concept_pages(bundle_root):
        ids.add(concept_id_from_path(page_file, bundle_root))
    return ids


def compute_queue(manifest: Manifest) -> list[Trecho]:
    """Compute the ordered work queue by comparing Sources with the wiki.

    A Trecho is enqueued when its hash is not yet stamped on any page. Order is
    by source declaration order, then by Trecho index — deterministic so a clone
    on another machine produces the same queue.
    """
    done = done_trecho_hashes(manifest.bundle_path)
    queue: list[Trecho] = []
    for source in manifest.sources:
        if source.type not in INGESTIBLE_TYPES:
            continue
        for t in extract_source(manifest, source):
            if t.hash not in done:
                queue.append(t)
    return queue


def next_work_item(manifest: Manifest, shortlist_size: int = 5) -> WorkItem | None:
    """Compute the next work item, or None if the queue is empty."""
    queue = compute_queue(manifest)
    if not queue:
        return None
    trecho = queue[0]
    from llmwiki.shortlist import build_shortlist

    shortlist = build_shortlist(manifest.bundle_path, trecho, limit=shortlist_size)
    return WorkItem(trecho=trecho, shortlist=shortlist)


def preserve_contributions(page: Page, previous: Page | None) -> None:
    """Tool-owned history comes from disk, never from a worker's draft."""
    for key in ("trechos", "source_ids", "consolidated_trechos", "source_versions"):
        page.frontmatter.pop(key, None)
        if previous is not None and key in previous.frontmatter:
            page.frontmatter[key] = previous.frontmatter[key]


def stamp_write(
    manifest: Manifest,
    *,
    page_id: str,
    page: Page,
    source_id: str,
    trecho_hash: str,
    now: _dt.date | None = None,
) -> Path:
    """Write a worker-authored page, stamping provenance the worker can't forget.

    The single stamping path used by every write. Sets ``generated`` (date) and
    ``generated_by``, appends ``trecho_hash`` to ``trechos`` (deduplicated),
    records the contributing ``source_id`` (for staleness), then ensures the
    Source Mirror exists. The caller passes the Trecho hash from the work item;
    code is revalidated against the delivered hash to identify the contributing
    files and reject changed external checkouts. Identity (``type``) is the caller's responsibility (spec §28).
    """
    bundle = manifest.bundle_path
    page_path = bundle / f"{page_id}.md"
    previous = read_page(page_path) if page_path.exists() else None
    preserve_contributions(page, previous)

    page.frontmatter["id"] = page_id
    page.frontmatter["generated"] = (now or _dt.date.today()).isoformat()
    page.frontmatter["generated_by"] = GENERATED_BY

    existing = list(page.frontmatter.get("trechos", []) or [])
    if trecho_hash not in existing:
        existing.append(trecho_hash)
    page.frontmatter["trechos"] = existing
    src_ids = set(page.frontmatter.get("source_ids", []) or [])
    src_ids.add(source_id)
    page.frontmatter["source_ids"] = sorted(src_ids)

    source = manifest.source(source_id)
    src_hash, rel_path = _source_hash_and_relpath(manifest, source)
    versions = dict(page.frontmatter.get("source_versions", {}))
    version = {"type": source.type, "path": rel_path}
    if source.type == "code":
        matches = [t for t in extract_source(manifest, source) if t.hash == trecho_hash]
        if not matches:
            raise IngestionError(f"source {source.id!r}: Trecho is no longer present; request the current work item")
        files = dict(versions.get(source_id, {}).get("files", {}))
        for trecho in matches:
            files[trecho.source_path] = code_file_version(code_base_path(manifest, source) / trecho.source_path)
        version["files"] = files
    else:
        version["content_hash"] = src_hash
    versions[source_id] = version
    page.frontmatter["source_versions"] = versions

    write_page(page_path, page)

    # Updating the shared mirror never refreshes another page's derivation.
    ensure_reference(
        bundle,
        source_id=source.id,
        source_type=source.type,
        rel_path=rel_path,
        source_hash=src_hash,
        commit=source.commit if source.repository else None,
        version=version,
    )
    return page_path
