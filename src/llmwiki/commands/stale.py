"""Staleness command: ``stale report`` — list stale pages by hash/SHA. Ticket 10."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llmwiki.commands import CommandError
from llmwiki.manifest import ManifestError, load_manifest
from llmwiki.okf.page import RESERVED_FILES, concept_id_from_path, read_page
from llmwiki.staleness import staleness_report


def register(sub: "argparse._SubParsersAction") -> None:
    p = sub.add_parser("stale", help="report Páginas Obsoletas (by content hash / commit SHA)")
    ssub = p.add_subparsers(dest="stale_command", required=True)
    r = ssub.add_parser("report", help="list stale pages and what changed")
    r.set_defaults(func=cmd_report)


def cmd_report(args: argparse.Namespace, root: Path) -> int:
    try:
        manifest = load_manifest(root)
    except ManifestError as exc:
        raise CommandError(str(exc))
    bundle = manifest.bundle_path
    stale = []
    unverifiable = []
    if bundle.exists():
        for page_file in sorted(bundle.rglob("*.md")):
            if page_file.name in RESERVED_FILES:
                continue
            page = read_page(page_file, require_type=False)
            cid = concept_id_from_path(page_file, bundle)
            report = staleness_report(manifest, page_id=cid, page=page)
            if report is None:
                continue  # not verifiable → reported neither stale nor current
            if report["stale"]:
                stale.append({"id": cid, "changed": report["changed"]})
            if report.get("unverifiable"):
                unverifiable.append({"id": cid, "reasons": report["unverifiable"]})
    print(json.dumps({"stale": stale, "unverifiable": unverifiable}))
    return 0
