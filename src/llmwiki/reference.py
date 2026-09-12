"""Source Mirror: a page in ``references/`` that represents a Source 1:1.

Exists for traceability and citation, not to explain (CONTEXT.md glossary). It
carries the relative path to the Source and a content hash so a claim can be
traced back even when the Source is a PDF with no URL, and so staleness can be
detected when the Source changes (ticket 10). For code Sources it also carries
the commit SHA of the file read (ticket 08).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from llmwiki.okf.page import Page, read_page, write_page

REFERENCES_DIR = "references"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def reference_id(source_id: str) -> str:
    return f"{REFERENCES_DIR}/{source_id}"


def reference_path(bundle_root: Path, source_id: str) -> Path:
    return bundle_root / REFERENCES_DIR / f"{source_id}.md"


def ensure_reference(
    bundle_root: Path,
    *,
    source_id: str,
    source_type: str,
    rel_path: str,
    source_text: str | None = None,
    source_hash: str | None = None,
    commit: str | None = None,
) -> Path:
    """Create or update the Source Mirror for a Source. Returns its path.

    The mirror is a ``Reference`` page. ``source_provenance`` holds the relative
    path and content hash (and commit SHA for code), which is the key that
    triggers staleness checks (ticket 10). Pass either ``source_text`` (hashed
    here) or a precomputed ``source_hash`` (for binary Sources such as PDF).
    """
    path = reference_path(bundle_root, source_id)
    if source_hash is None:
        if source_text is None:
            raise ValueError("ensure_reference needs source_text or source_hash")
        source_hash = content_hash(source_text)
    provenance = {
        "source_id": source_id,
        "source_type": source_type,
        "path": rel_path,
        "content_hash": source_hash,
    }
    if commit is not None:
        provenance["commit"] = commit

    if path.exists():
        page = read_page(path)
    else:
        page = Page(frontmatter={}, body="")
    page.frontmatter["type"] = "Reference"
    page.frontmatter.setdefault("title", source_id)
    page.frontmatter.setdefault(
        "description", f"Espelho da Fonte {source_id!r} ({source_type})."
    )
    page.frontmatter["source_provenance"] = provenance
    if not page.body:
        page.body = f"Espelho da Fonte `{source_id}` em `{rel_path}`.\n"
    write_page(path, page)
    return path
