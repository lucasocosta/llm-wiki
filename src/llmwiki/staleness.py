"""Staleness: a page is a Página Obsoleta when its Source changed after derivation.

Exact, not calendar-based (ADR 0001): a page derived from a file compares the
content hash; a page derived from code compares the commit SHA. The check is
triggered by the *presence of provenance*, not by ``type``: ``type`` describes
what the page is to a reader, not how it is maintained (ticket 10). A page
without verifiable provenance is reported neither stale nor current.
"""

from __future__ import annotations

from pathlib import Path

from llmwiki.manifest import Manifest
from llmwiki.okf.page import Page, read_page
from llmwiki.reference import content_hash


def _referenced_source_ids(page: Page) -> list[str]:
    """Source ids this page draws provenance from.

    Prefers the tool-stamped ``source_ids`` (ticket 10); falls back to any
    ``source_id``/``id`` recorded inside ``sources`` entries.
    """
    stamped = page.frontmatter.get("source_ids")
    if stamped:
        return [str(s) for s in stamped]
    ids = []
    for entry in page.frontmatter.get("sources", []) or []:
        if isinstance(entry, dict):
            sid = entry.get("source_id") or entry.get("id")
            if sid:
                ids.append(str(sid))
    return ids


def _provenance_of(manifest: Manifest, source_id: str) -> dict | None:
    """Read the Source Mirror's provenance for a Source id, if it exists."""
    ref_path = manifest.bundle_path / "references" / f"{source_id}.md"
    if not ref_path.exists():
        return None
    ref = read_page(ref_path, require_type=False)
    prov = ref.frontmatter.get("source_provenance")
    return prov if isinstance(prov, dict) else None


def staleness_report(manifest: Manifest, *, page_id: str, page: Page) -> dict | None:
    """Return a staleness report for a page, or None if not verifiable.

    The report is ``{"stale": bool, "changed": [...]}``. It is computed by
    comparing the provenance recorded on the page's Source Mirror(s) against the
    current Source on disk.
    """
    source_ids = _referenced_source_ids(page)
    if not source_ids:
        return None

    changed: list[dict] = []
    verifiable = False
    for sid in source_ids:
        prov = _provenance_of(manifest, sid)
        if not prov:
            continue
        source_path = manifest.root / prov.get("path", "")
        if not source_path.exists():
            continue
        verifiable = True
        try:
            source = manifest.source(sid)
        except Exception:
            source = None

        # Code sources compare commit SHA; file sources compare content hash.
        if source is not None and source.type == "code" and prov.get("commit"):
            if source.commit and source.commit != prov.get("commit"):
                changed.append(
                    {"source_id": sid, "kind": "commit",
                     "was": prov.get("commit"), "now": source.commit}
                )
        else:
            import hashlib

            if source is not None and source.type == "pdf":
                current = hashlib.sha256(source_path.read_bytes()).hexdigest()
            else:
                current = content_hash(source_path.read_text(encoding="utf-8"))
            if current != prov.get("content_hash"):
                changed.append(
                    {"source_id": sid, "kind": "content_hash",
                     "was": prov.get("content_hash"), "now": current}
                )

    if not verifiable:
        return None
    return {"stale": bool(changed), "changed": changed}
