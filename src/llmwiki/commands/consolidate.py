"""Consolidation commands: ``consolidate list`` and ``consolidate write-page``.

The consolidation pass is opt-in and separate from ingestion (spec, ticket 11):
consolidating during ingestion would force deciding coherence before all
Sources are in hand. Its unit is the Página Suja, and it *rereads only the
page*, never the Sources.

``consolidate write-page`` runs in **consolidation mode**: the guard swaps
invariants 2, 5 and 6 for the single "citations preserved" invariant, freeing
merging sections, shrinking, and pruning duplicate links. On finish it records
the current set of contributing Trechos, so the page is no longer dirty
(ticket 11). This command is a curator operation, unreachable by the worker.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from llmwiki.commands import CommandError
from llmwiki.guard import GuardError, Mode, check_write
from llmwiki.manifest import ManifestError, load_manifest
from llmwiki.okf.index import generate_index_files
from llmwiki.okf.page import Page, PageError, parse_page, read_page, write_page


def register(sub: "argparse._SubParsersAction") -> None:
    p = sub.add_parser("consolidate", help="curator: reconcile dirty pages into one voice")
    csub = p.add_subparsers(dest="consolidate_command", required=True)

    ls = csub.add_parser("list", help="list the dirty pages")
    ls.set_defaults(func=cmd_list_dirty)

    w = csub.add_parser("write-page", help="write a consolidated page (consolidation mode)")
    w.add_argument("--page-id", required=True)
    w.add_argument("--content-file", required=True, help="'-' for stdin")
    w.set_defaults(func=cmd_consolidate_write)


def _load(root: Path):
    try:
        return load_manifest(root)
    except ManifestError as exc:
        raise CommandError(str(exc))


def cmd_list_dirty(args: argparse.Namespace, root: Path) -> int:
    manifest = _load(root)
    from llmwiki.dirty import dirty_pages

    print(json.dumps(dirty_pages(manifest.bundle_path)))
    return 0


def _read_content(content_file: str) -> str:
    if content_file == "-":
        return sys.stdin.read()
    return Path(content_file).read_text(encoding="utf-8")


def cmd_consolidate_write(args: argparse.Namespace, root: Path) -> int:
    manifest = _load(root)
    bundle = manifest.bundle_path
    page_path = bundle / f"{args.page_id}.md"
    if not page_path.exists():
        raise CommandError(f"page not found: {args.page_id}", exit_code=3)
    old_page = read_page(page_path, require_type=False)

    raw = _read_content(args.content_file)
    try:
        new_page = parse_page(raw, require_type=False)
    except PageError:
        new_page = Page(frontmatter={}, body=raw)
    # Consolidation may reshape prose but not identity.
    new_page.frontmatter.setdefault("type", old_page.frontmatter.get("type", "Topic"))
    new_page.frontmatter["id"] = args.page_id
    # Preserve provenance keys the worker's content may omit.
    for key in ("sources", "trechos", "generated", "generated_by", "source_provenance"):
        if key in old_page.frontmatter and key not in new_page.frontmatter:
            new_page.frontmatter[key] = old_page.frontmatter[key]

    from llmwiki.ingestion import known_concept_ids

    known = known_concept_ids(bundle)
    known.add(args.page_id)
    try:
        check_write(
            manifest,
            page_id=args.page_id,
            old=old_page,
            new=new_page,
            mode=Mode.CONSOLIDATION,
            known_ids=known,
        )
    except GuardError as exc:
        raise CommandError(str(exc), exit_code=2)

    # Record the current contributing Trechos set as the consolidated set, so
    # the page is no longer dirty (ticket 11).
    trechos = list(new_page.frontmatter.get("trechos", []) or [])
    new_page.frontmatter["consolidated_trechos"] = trechos

    write_page(page_path, new_page)
    generate_index_files(bundle, language=manifest.language)
    from llmwiki.log import append_log

    append_log(bundle, f"consolidate {args.page_id} ({len(trechos)} trechos)")
    print(page_path.relative_to(bundle).as_posix())
    return 0
