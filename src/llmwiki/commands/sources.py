"""Curator escapes (ticket 13): remove a ``sources`` entry, move/rename a page.

These are the two legitimate escapes from the guard, and they are *curator
commands*, not writes: a person runs them, the worker never reaches them. That
separation is what keeps the guard a guard rather than a suggestion — a marker
the worker could set would be a master key. After either escape, the guard still
enforces the six invariants on common writes.

``move-page`` renames a page and updates every referrer in the same operation,
so reorganising the wiki does not produce broken links (spec).
"""

from __future__ import annotations

import argparse
import json
import re
import posixpath
from pathlib import Path

from llmwiki.commands import CommandError
from llmwiki.links import resolve_link
from llmwiki.manifest import ManifestError, load_manifest
from llmwiki.okf.index import generate_index_files
from llmwiki.okf.page import (
    RESERVED_FILES,
    concept_id_from_path,
    read_page,
    write_page,
)

_LINK_RE = re.compile(r"(\[[^\]]*\]\()([^)]+)(\))")


def register(sub: "argparse._SubParsersAction") -> None:
    p = sub.add_parser("sources", help="curator operations on pages and provenance")
    ssub = p.add_subparsers(dest="sources_command", required=True)

    rm = ssub.add_parser(
        "remove-source-entry",
        help="curator: remove a sources entry from a page (the guard's escape)",
    )
    rm.add_argument("--page-id", required=True)
    rm.add_argument("--source-entry-id", required=True)
    rm.set_defaults(func=cmd_remove_source_entry)

    lt = ssub.add_parser(
        "list-trechos",
        help="curator: enumerate the CURRENT Trechos of a Source (also already-stamped ones)",
    )
    lt.add_argument("source_id", help="Fonte id (must be in the manifest)")
    lt.add_argument(
        "--with-text",
        action="store_true",
        help="include the Trecho text in the payload (payload grows in text)",
    )
    lt.set_defaults(func=cmd_list_trechos)

    mv = ssub.add_parser(
        "move-page",
        help="curator: move/rename a page, updating referrers in the same op",
    )
    mv.add_argument("--from", dest="from_id", required=True)
    mv.add_argument("--to", dest="to_id", required=True)
    mv.set_defaults(func=cmd_move_page)


def _manifest(root: Path):
    try:
        return load_manifest(root)
    except ManifestError as exc:
        raise CommandError(str(exc))


def cmd_list_trechos(args: argparse.Namespace, root: Path) -> int:
    """Ticket 15: enumerate all current Trechos for curation/migration.

    ``ingest queue``/``next`` only expose pending Trechos; migration and
    re-stamping need the *current* set (also the stamped ones). This is a
    curator command, and it replaces the internal-extractor workaround the
    migration had to do.
    """
    try:
        manifest = load_manifest(root)
        source = manifest.source(args.source_id)
    except ManifestError as exc:
        raise CommandError(str(exc))
    from llmwiki.ingestion import _extract_source
    from llmwiki.usage import record

    try:
        trechos = _extract_source(manifest, source)
    except Exception as exc:
        raise CommandError(str(exc))
    payload = []
    for t in trechos:
        item = {
            "source_id": t.source_id,
            "trecho_hash": t.hash,
            "trecho_index": t.index,
            "anchor": t.anchor,
        }
        if getattr(t, "source_path", None):
            item["source_path"] = t.source_path
        if args.with_text:
            item["text"] = t.text
        payload.append(item)
    print(json.dumps(payload))
    record(root, "sources list-trechos", len(json.dumps(payload)))
    return 0


def cmd_remove_source_entry(args: argparse.Namespace, root: Path) -> int:
    manifest = _manifest(root)
    page_path = manifest.bundle_path / f"{args.page_id}.md"
    if not page_path.exists():
        raise CommandError(f"page not found: {args.page_id}", exit_code=3)
    page = read_page(page_path, require_type=False)
    sources = list(page.frontmatter.get("sources", []) or [])
    kept = [
        s for s in sources
        if not (isinstance(s, dict) and str(s.get("id")) == args.source_entry_id)
    ]
    if len(kept) == len(sources):
        raise CommandError(
            f"no sources entry with id {args.source_entry_id!r} on {args.page_id}"
        )
    page.frontmatter["sources"] = kept
    write_page(page_path, page)
    from llmwiki.log import append_log

    append_log(manifest.bundle_path, f"remove-source-entry {args.source_entry_id} from {args.page_id}")
    print(f"removed {args.source_entry_id} from {args.page_id}")
    return 0


def _move_and_rewrite_links(bundle_root: Path, from_id: str, to_id: str) -> None:
    """Resolve links at their old locations before writing the moved Bundle."""
    updates = []
    for page_file in sorted(bundle_root.rglob("*.md")):
        if page_file.name in RESERVED_FILES:
            continue
        page = read_page(page_file, require_type=False)
        old_id = concept_id_from_path(page_file, bundle_root)
        new_id = to_id if old_id == from_id else old_id

        def rewrite(match):
            target = match.group(2)
            resolved = resolve_link(old_id, target)
            if resolved is None or (old_id == new_id and resolved != from_id):
                return match.group(0)
            destination = to_id if resolved == from_id else resolved
            relative = posixpath.relpath(f"{destination}.md", posixpath.dirname(new_id) or ".")
            fragment = "#" + target.split("#", 1)[1] if "#" in target else ""
            return f"{match.group(1)}{relative}{fragment}{match.group(3)}"

        body = _LINK_RE.sub(rewrite, page.body)
        if body != page.body or old_id != new_id:
            page.body = body
            if old_id != new_id:
                page.frontmatter["id"] = new_id
            updates.append((bundle_root / f"{new_id}.md", page))
    for destination, page in updates:
        write_page(destination, page)


def cmd_move_page(args: argparse.Namespace, root: Path) -> int:
    manifest = _manifest(root)
    bundle = manifest.bundle_path
    src = bundle / f"{args.from_id}.md"
    dst = bundle / f"{args.to_id}.md"
    if not src.exists():
        raise CommandError(f"page not found: {args.from_id}", exit_code=3)
    if dst.exists():
        raise CommandError(f"destination already exists: {args.to_id}", exit_code=2)

    _move_and_rewrite_links(bundle, args.from_id, args.to_id)
    src.unlink()

    generate_index_files(bundle, language=manifest.language)
    from llmwiki.log import append_log

    append_log(bundle, f"move-page {args.from_id} -> {args.to_id}")
    print(f"moved {args.from_id} -> {args.to_id}")
    return 0
