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
import re
from pathlib import Path

from llmwiki.commands import CommandError
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


def _rewrite_links(bundle_root: Path, from_id: str, to_id: str) -> None:
    """Rewrite every relative link that resolves to ``from_id`` to point at ``to_id``."""
    import posixpath

    for page_file in sorted(bundle_root.rglob("*.md")):
        if page_file.name in RESERVED_FILES:
            continue
        cid = concept_id_from_path(page_file, bundle_root)
        page = read_page(page_file, require_type=False)
        body = page.body or ""

        def repl(m: re.Match) -> str:
            pre, target, post = m.group(1), m.group(2), m.group(3)
            frag = ""
            base = target
            if "#" in target:
                base, frag = target.split("#", 1)
                frag = "#" + frag
            if not base.endswith(".md") or base.startswith(("http://", "https://", "/")):
                return m.group(0)
            page_dir = posixpath.dirname(cid)
            resolved = posixpath.normpath(posixpath.join(page_dir, base))
            if resolved.endswith(".md"):
                resolved = resolved[: -len(".md")]
            if resolved != from_id:
                return m.group(0)
            # Compute a new relative link from this page to to_id.
            new_rel = posixpath.relpath(f"{to_id}.md", page_dir or ".")
            return f"{pre}{new_rel}{frag}{post}"

        new_body = _LINK_RE.sub(repl, body)
        if new_body != body:
            page.body = new_body
            write_page(page_file, page)


def cmd_move_page(args: argparse.Namespace, root: Path) -> int:
    manifest = _manifest(root)
    bundle = manifest.bundle_path
    src = bundle / f"{args.from_id}.md"
    dst = bundle / f"{args.to_id}.md"
    if not src.exists():
        raise CommandError(f"page not found: {args.from_id}", exit_code=3)
    if dst.exists():
        raise CommandError(f"destination already exists: {args.to_id}", exit_code=2)

    page = read_page(src, require_type=False)
    page.frontmatter["id"] = args.to_id
    dst.parent.mkdir(parents=True, exist_ok=True)
    write_page(dst, page)
    src.unlink()

    _rewrite_links(bundle, args.from_id, args.to_id)
    generate_index_files(bundle, language=manifest.language)
    from llmwiki.log import append_log

    append_log(bundle, f"move-page {args.from_id} -> {args.to_id}")
    print(f"moved {args.from_id} -> {args.to_id}")
    return 0
