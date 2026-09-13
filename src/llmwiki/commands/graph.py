"""Graph and lint commands: backlinks, orphans, broken-links, lint. Ticket 12."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llmwiki.commands import CommandError
from llmwiki.manifest import ManifestError, load_manifest


def register(sub: "argparse._SubParsersAction") -> None:
    p = sub.add_parser("graph", help="inspect the wiki as a link graph, and lint")
    gsub = p.add_subparsers(dest="graph_command", required=True)

    b = gsub.add_parser("backlinks", help="list pages linking to a page")
    b.add_argument("page_id")
    b.set_defaults(func=cmd_backlinks)

    o = gsub.add_parser("orphans", help="pages with no incoming edge (excl. index.md)")
    o.set_defaults(func=cmd_orphans)

    bl = gsub.add_parser("broken-links", help="links whose target does not exist")
    bl.set_defaults(func=cmd_broken_links)

    li = gsub.add_parser("lint", help="warn about long pages, with their headers")
    li.add_argument("--long-page-chars", type=int, default=None)
    li.set_defaults(func=cmd_lint)


def _bundle(root: Path):
    try:
        return load_manifest(root).bundle_path
    except ManifestError as exc:
        raise CommandError(str(exc))


def cmd_backlinks(args: argparse.Namespace, root: Path) -> int:
    from llmwiki.graph import backlinks

    print(json.dumps(backlinks(_bundle(root), args.page_id)))
    return 0


def cmd_orphans(args: argparse.Namespace, root: Path) -> int:
    from llmwiki.graph import orphans

    print(json.dumps(orphans(_bundle(root))))
    return 0


def cmd_broken_links(args: argparse.Namespace, root: Path) -> int:
    from llmwiki.graph import broken_links

    print(json.dumps(broken_links(_bundle(root))))
    return 0


def cmd_lint(args: argparse.Namespace, root: Path) -> int:
    from llmwiki.graph import DEFAULT_LONG_PAGE_CHARS, lint_report

    threshold = args.long_page_chars or DEFAULT_LONG_PAGE_CHARS
    print(json.dumps(lint_report(_bundle(root), threshold)))
    return 0
