"""Graph and lint: inspect the wiki as a graph of links (ticket 12).

Everything here is a property of the link graph or of page size — computable
without judgement. Contradiction detection (understanding what two pages
*claim*) is deliberately out of scope. A long page is *warned*, never refused:
refusing would force the worker to truncate knowledge to fit (spec).
"""

from __future__ import annotations

import re
from pathlib import Path

from llmwiki.links import resolve_link
from llmwiki.okf.page import RESERVED_FILES, concept_id_from_path, read_page

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.MULTILINE)

# Default page-length warning threshold (characters). Overridable per call.
DEFAULT_LONG_PAGE_CHARS = 8000


def _iter_concept_pages(bundle_root: Path) -> list[Path]:
    if not Path(bundle_root).exists():
        return []
    return sorted(
        p for p in Path(bundle_root).rglob("*.md") if p.name not in RESERVED_FILES
    )


def build_graph(bundle_root: Path) -> dict[str, list[str]]:
    """Map each concept id to the list of concept ids it links to (edges out)."""
    bundle_root = Path(bundle_root)
    edges: dict[str, list[str]] = {}
    for page_file in _iter_concept_pages(bundle_root):
        cid = concept_id_from_path(page_file, bundle_root)
        page = read_page(page_file, require_type=False)
        out = []
        for target in _LINK_RE.findall(page.body or ""):
            resolved = resolve_link(cid, target)
            if resolved is not None:
                out.append(resolved)
        edges[cid] = out
    return edges


def backlinks(bundle_root: Path, page_id: str) -> list[str]:
    """Concept ids that link *to* ``page_id``, sorted."""
    edges = build_graph(bundle_root)
    return sorted(src for src, outs in edges.items() if page_id in outs)


def orphans(bundle_root: Path) -> list[str]:
    """Pages with no incoming edge, excluding index.md (already excluded)."""
    edges = build_graph(bundle_root)
    incoming: set[str] = set()
    for outs in edges.values():
        incoming.update(outs)
    return sorted(cid for cid in edges if cid not in incoming)


def broken_links(bundle_root: Path) -> list[dict]:
    """Links whose resolved target is not a page in the wiki."""
    edges = build_graph(bundle_root)
    existing = set(edges)
    broken = []
    for src, outs in edges.items():
        for target in outs:
            if target not in existing:
                broken.append({"from": src, "to": target})
    return broken


def long_pages(
    bundle_root: Path, threshold: int = DEFAULT_LONG_PAGE_CHARS
) -> list[dict]:
    """Pages above the size threshold, each with its headers (to suggest cuts)."""
    bundle_root = Path(bundle_root)
    out = []
    for page_file in _iter_concept_pages(bundle_root):
        page = read_page(page_file, require_type=False)
        size = len(page.body or "")
        if size > threshold:
            headers = [m.group(2) for m in _HEADER_RE.finditer(page.body or "")]
            out.append(
                {
                    "id": concept_id_from_path(page_file, bundle_root),
                    "chars": size,
                    "headers": headers,
                }
            )
    return out
