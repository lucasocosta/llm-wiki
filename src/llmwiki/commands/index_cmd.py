"""``regenerate-index``: (re)build every index.md from page frontmatter (§8)."""

from __future__ import annotations

import argparse
from pathlib import Path

from llmwiki.manifest import load_manifest
from llmwiki.okf.index import generate_index_files


def register(sub: "argparse._SubParsersAction") -> None:
    p = sub.add_parser(
        "regenerate-index",
        help="regenerate index.md files from page frontmatter (no LLM)",
    )
    p.set_defaults(func=cmd_regenerate_index)


def cmd_regenerate_index(args: argparse.Namespace, root: Path) -> int:
    manifest = load_manifest(root)
    bundle = manifest.bundle_path
    bundle.mkdir(parents=True, exist_ok=True)
    written = generate_index_files(bundle, language=manifest.language)
    for path in written:
        print(path.relative_to(bundle).as_posix())
    return 0
