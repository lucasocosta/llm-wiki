"""Ingestion commands: ``ingest next`` and ``ingest write-page``.

These are the two deterministic halves of the ingestion contract:
``next`` hands the worker a work item (Trecho + shortlist); ``write-page`` takes
the page the worker wrote and stamps provenance the worker cannot forget. The
worker reaches only these plus ``search`` and ``read-page`` — never a curator
command (ticket 06/13).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from llmwiki.commands import CommandError
from llmwiki.extract import ExtractionError
from llmwiki.guard import GuardError, Mode, check_write
from llmwiki.ingestion import (
    IngestionError,
    compute_queue,
    next_work_item,
    stamp_write,
)
from llmwiki.log import append_log
from llmwiki.manifest import ManifestError, load_manifest, validate_trecho_budget
from llmwiki.okf.index import generate_index_files
from llmwiki.okf.page import PageError, Page, parse_page, read_page


def register(sub: "argparse._SubParsersAction") -> None:
    p = sub.add_parser("ingest", help="deterministic ingestion of Sources")
    isub = p.add_subparsers(dest="ingest_command", required=True)

    n = isub.add_parser("next", help="emit the next work item as JSON")
    n.add_argument("--shortlist-size", type=int, default=5)
    n.set_defaults(func=cmd_next)

    q = isub.add_parser("queue", help="emit the whole computed queue as JSON")
    q.set_defaults(func=cmd_queue)

    r = isub.add_parser("report", help="ingestion report: per-source counts, allowlist exclusions")
    r.set_defaults(func=cmd_report)

    w = isub.add_parser("write-page", help="write a worker-authored page (stamps provenance)")
    w.add_argument("--page-id", required=True)
    w.add_argument("--source-id", required=True)
    w.add_argument("--trecho-hash", required=True)
    w.add_argument("--trecho-index", type=int, default=0)
    w.add_argument("--anchor", default="")
    w.add_argument(
        "--content-file",
        help="path to the page the worker wrote (frontmatter+body); '-' for stdin",
        required=True,
    )
    w.set_defaults(func=cmd_write_page)
    for command in (n, q, w):
        command.add_argument("--max-trecho-chars", type=int, help="override the manifest's Unicode character budget per Trecho")


def _load(root: Path, args: argparse.Namespace):
    try:
        manifest = load_manifest(root)
        override = getattr(args, "max_trecho_chars", None)
        if override is not None:
            manifest.max_trecho_chars = validate_trecho_budget(override)
        return manifest
    except ManifestError as exc:
        raise CommandError(str(exc))


def cmd_next(args: argparse.Namespace, root: Path) -> int:
    manifest = _load(root, args)
    try:
        item = next_work_item(manifest, shortlist_size=args.shortlist_size)
    except (IngestionError, ExtractionError) as exc:
        raise CommandError(str(exc))
    if item is None:
        print(json.dumps({"work_item": None}))
        return 0
    print(json.dumps(item.to_payload()))
    return 0


def cmd_queue(args: argparse.Namespace, root: Path) -> int:
    manifest = _load(root, args)
    try:
        queue = compute_queue(manifest)
    except (IngestionError, ExtractionError) as exc:
        raise CommandError(str(exc))
    payload = [
        {
            "source_id": t.source_id,
            "trecho_hash": t.hash,
            "trecho_index": t.index,
            "anchor": t.anchor,
        }
        for t in queue
    ]
    print(json.dumps(payload))
    return 0


def _read_content(content_file: str) -> str:
    if content_file == "-":
        return sys.stdin.read()
    return Path(content_file).read_text(encoding="utf-8")


def cmd_report(args: argparse.Namespace, root: Path) -> int:
    manifest = _load(root, args)
    from llmwiki.ingestion import scan_code

    per_source = []
    for source in manifest.sources:
        entry = {"source_id": source.id, "type": source.type}
        if source.type == "code":
            try:
                scan = scan_code(manifest, source)
                entry["included_files"] = len(scan.included)
                entry["excluded_by_allowlist"] = scan.excluded_count
            except (IngestionError, ExtractionError) as exc:
                entry["error"] = str(exc)
        per_source.append(entry)
    print(json.dumps({"sources": per_source}))
    return 0


def cmd_write_page(args: argparse.Namespace, root: Path) -> int:
    manifest = _load(root, args)
    raw = _read_content(args.content_file)
    try:
        # The worker may or may not include frontmatter; parse leniently.
        try:
            page = parse_page(raw, require_type=False)
        except PageError:
            page = Page(frontmatter={}, body=raw)
    except PageError as exc:
        raise CommandError(str(exc))

    bundle = manifest.bundle_path
    page_path = bundle / f"{args.page_id}.md"
    old_page = read_page(page_path, require_type=False) if page_path.exists() else None

    # Spec §28: refuse writing a page whose frontmatter has no `type`. The tool
    # fills provenance (generated, trechos), but the worker must declare type —
    # provenance must not depend on the model, and identity must not either. When
    # augmenting an existing page a missing type is inherited (identity preserved).
    if not page.frontmatter.get("type"):
        if old_page is not None and old_page.frontmatter.get("type"):
            page.frontmatter["type"] = old_page.frontmatter["type"]
        else:
            raise CommandError(
                "frontmatter must include a 'type' key (e.g. Topic); refusing",
                exit_code=2,
            )
    page.frontmatter["id"] = args.page_id

    from llmwiki.ingestion import known_concept_ids

    known = known_concept_ids(bundle)
    known.add(args.page_id)  # self-links and the page itself are allowed
    try:
        check_write(
            manifest,
            page_id=args.page_id,
            old=old_page,
            new=page,
            mode=Mode.INGESTION,
            known_ids=known,
        )
    except GuardError as exc:
        raise CommandError(str(exc), exit_code=2)

    # The tool preserves prior contributions and verifies code provenance
    # before stamping the delivered Trecho.
    try:
        path = stamp_write(
            manifest,
            page_id=args.page_id,
            page=page,
            source_id=args.source_id,
            trecho_hash=args.trecho_hash,
        )
    except IngestionError as exc:
        raise CommandError(str(exc))

    generate_index_files(bundle, language=manifest.language)
    append_log(bundle, f"write-page {args.page_id} <- trecho {args.trecho_hash[:12]}")
    print(path.relative_to(bundle).as_posix())
    return 0
