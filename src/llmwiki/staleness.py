"""Compare each page's derivation versions with its current Sources.

An updated shared mirror cannot refresh a conceptual page's provenance.
Unknown historical versions remain explicitly unverifiable.
"""

from __future__ import annotations

import hashlib

from llmwiki.manifest import Manifest
from llmwiki.okf.page import Page
from llmwiki.provenance import code_file_version


def staleness_report(manifest: Manifest, *, page_id: str, page: Page) -> dict | None:
    versions = page.frontmatter.get("source_versions", {})
    source_ids = set(page.frontmatter.get("source_ids", []) or []) | set(versions)
    for entry in page.frontmatter.get("sources", []) or []:
        if isinstance(entry, dict) and entry.get("source_id"):
            source_ids.add(entry["source_id"])
    if page_id.startswith("references/") and page.frontmatter.get("source_provenance"):
        sid = page_id.removeprefix("references/")
        versions = {sid: page.frontmatter["source_provenance"]}
        source_ids = {sid}
    if not source_ids:
        return None

    changed = []
    unverifiable = []
    for sid in sorted(source_ids):
        version = versions.get(sid)
        if not version:
            unverifiable.append({"source_id": sid, "reason": "no derivation version recorded on this page"})
            continue
        source_path = manifest.root / version.get("path", "")
        if version.get("type", version.get("source_type")) == "code":
            files = version.get("files", {})
            if not files:
                unverifiable.append({"source_id": sid, "reason": "no per-file code revision recorded"})
            for relative, previous in files.items():
                current = code_file_version(source_path / relative)
                identity = {"source_id": sid, "path": relative}
                if not previous.get("commit") or not current.get("commit"):
                    unverifiable.append({**identity, "reason": previous.get("unverifiable") or current.get("unverifiable") or "no recorded commit"})
                elif previous["commit"] != current["commit"]:
                    changed.append({**identity, "kind": "commit", "was": previous["commit"], "now": current["commit"]})
                if previous.get("content_hash") and current.get("content_hash") and previous["content_hash"] != current["content_hash"] and not current.get("commit"):
                    changed.append({**identity, "kind": "content_hash", "was": previous["content_hash"], "now": current["content_hash"]})
        elif source_path.is_file() and version.get("content_hash"):
            current_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
            if current_hash != version["content_hash"]:
                changed.append({"source_id": sid, "kind": "content_hash", "was": version["content_hash"], "now": current_hash})
        else:
            unverifiable.append({"source_id": sid, "reason": "source file or recorded content hash is missing"})

    result = {"stale": bool(changed), "changed": changed}
    if unverifiable:
        result["unverifiable"] = unverifiable
        if not changed:
            result["stale"] = None
    return result
