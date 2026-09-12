"""Query commands: ``read-page`` (search is added in ticket 03).

Reading is whole-page: the caller doesn't need to know what sections a page has
before asking (spec). A page opened while stale is flagged with the content so
the reader can qualify the answer (ticket 10).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llmwiki.commands import CommandError
from llmwiki.manifest import ManifestError, load_manifest
from llmwiki.okf.page import PageError, read_page


def register(sub: "argparse._SubParsersAction") -> None:
    p = sub.add_parser("read-page", help="read a whole page (frontmatter + body)")
    p.add_argument("page_id", help="concept id, e.g. 'concurrency' or 'references/paper'")
    p.set_defaults(func=cmd_read_page)

    s = sub.add_parser("search", help="lexical search; returns metadata winners, never bodies")
    s.add_argument("query", help="the search query")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--type", dest="type_filter", default=None, help="filter by page type")
    s.add_argument(
        "--tag",
        dest="tags",
        action="append",
        default=None,
        help="filter by tag (repeatable; all must match)",
    )
    s.add_argument(
        "--snippet",
        action="store_true",
        help="include a snippet of the matched text (off by default)",
    )
    s.set_defaults(func=cmd_search)


def cmd_search(args: argparse.Namespace, root: Path) -> int:
    try:
        manifest = load_manifest(root)
    except ManifestError as exc:
        raise CommandError(str(exc))
    from llmwiki.search import search_index

    results = search_index(
        manifest.bundle_path,
        query=args.query,
        limit=args.limit,
        type_filter=args.type_filter,
        tags_filter=args.tags,
        snippet=args.snippet,
    )
    print(json.dumps(results))
    return 0


def cmd_read_page(args: argparse.Namespace, root: Path) -> int:
    try:
        manifest = load_manifest(root)
    except ManifestError as exc:
        raise CommandError(str(exc))
    page_path = manifest.bundle_path / f"{args.page_id}.md"
    if not page_path.exists():
        raise CommandError(f"page not found: {args.page_id}", exit_code=3)
    try:
        page = read_page(page_path, require_type=False)
    except PageError as exc:
        raise CommandError(str(exc))

    from llmwiki.staleness import staleness_report

    stale = staleness_report(manifest, page_id=args.page_id, page=page)
    payload = {
        "id": args.page_id,
        "frontmatter": page.frontmatter,
        "body": page.body,
        "stale": stale,
    }
    print(json.dumps(payload, default=str))
    return 0
