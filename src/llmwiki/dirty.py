"""Página Suja: a page written by more than one reading, not yet reconciled.

Computable without a state file (spec, ticket 11): the write-page tool stamps
each contributing Trecho hash on the page (``trechos``); consolidation records
the set as ``consolidated_trechos`` when it finishes. A page is **dirty** when
its current ``trechos`` set differs from the set recorded at the last
consolidation. A never-consolidated page touched by more than one Trecho is
dirty; touched by exactly one, it is not.
"""

from __future__ import annotations

from pathlib import Path

from llmwiki.okf.page import RESERVED_FILES, concept_id_from_path, read_page


def is_dirty(page) -> bool:
    trechos = set(page.frontmatter.get("trechos", []) or [])
    consolidated = page.frontmatter.get("consolidated_trechos")
    if consolidated is None:
        # Never consolidated: dirty iff more than one Trecho contributed.
        return len(trechos) > 1
    return trechos != set(consolidated)


def dirty_pages(bundle_root: Path) -> list[str]:
    """Return the ids of the wiki's dirty pages, sorted."""
    bundle_root = Path(bundle_root)
    if not bundle_root.exists():
        return []
    out: list[str] = []
    for page_file in sorted(bundle_root.rglob("*.md")):
        if page_file.name in RESERVED_FILES:
            continue
        page = read_page(page_file, require_type=False)
        if is_dirty(page):
            out.append(concept_id_from_path(page_file, bundle_root))
    return sorted(out)
