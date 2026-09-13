"""Ticket 14: log.md as a readable history."""

from __future__ import annotations

import datetime as _dt
import re


def _ingest_two(cli, wiki, tmp_path):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source(
        "notes.md",
        "# Alpha\n\nEnough content about alpha to pass.\n\n# Beta\n\nEnough about beta too.\n",
    )
    for pid in ("alpha", "beta"):
        item = cli("ingest", "next").json
        cf = tmp_path / f"{pid}.md"
        cf.write_text(f"---\ntype: Topic\ntitle: {pid}\n---\n\nbody\n", encoding="utf-8")
        cli(
            "ingest", "write-page",
            "--page-id", pid,
            "--source-id", item["source_id"],
            "--trecho-hash", item["trecho_hash"],
            "--content-file", str(cf),
        )


def test_log_has_iso_date_headers(cli, wiki, tmp_path):
    _ingest_two(cli, wiki, tmp_path)
    log = (wiki.bundle / "log.md").read_text(encoding="utf-8")
    today = _dt.date.today().isoformat()
    assert f"## {today}" in log


def test_log_parseable_by_unix_tools(cli, wiki, tmp_path):
    _ingest_two(cli, wiki, tmp_path)
    log = (wiki.bundle / "log.md").read_text(encoding="utf-8")
    # grep '^## ' yields date headers; each is a valid ISO date.
    headers = [ln[3:].strip() for ln in log.splitlines() if ln.startswith("## ")]
    assert headers
    for h in headers:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", h)


def test_newest_date_first(cli, wiki, tmp_path):
    _ingest_two(cli, wiki, tmp_path)
    # Prepare genuine persisted history, then append through an ingestion command.
    (wiki.bundle / "log.md").write_text("# Log\n\n## 2000-01-01\n\n- 12:00:00 historical event\n")
    wiki.write_manifest(
        sources=[
            {"id": "notes", "type": "markdown", "location": "notes.md"},
            {"id": "more", "type": "markdown", "location": "more.md"},
        ]
    )
    wiki.write_source(
        "more.md",
        "# Gamma\n\nPlenty of content about gamma here.\n\n# Delta\n\nPlenty about delta too.\n",
    )
    for pid in ("gamma", "delta"):
        item = cli("ingest", "next").json
        cf = tmp_path / f"{pid}.md"
        cf.write_text(f"---\ntype: Topic\ntitle: {pid}\n---\n\nbody\n", encoding="utf-8")
        cli(
            "ingest", "write-page",
            "--page-id", pid,
            "--source-id", item["source_id"],
            "--trecho-hash", item["trecho_hash"],
            "--content-file", str(cf),
        )
    log = (wiki.bundle / "log.md").read_text(encoding="utf-8")
    headers = [ln[3:].strip() for ln in log.splitlines() if ln.startswith("## ")]
    assert headers == sorted(headers, reverse=True)


def test_deleting_log_does_not_affect_queue_dirty_staleness(cli, wiki, tmp_path):
    _ingest_two(cli, wiki, tmp_path)
    queue_before = cli("ingest", "queue").json
    dirty_before = cli("consolidate", "list").json
    stale_before = cli("stale", "report").json

    (wiki.bundle / "log.md").unlink()

    assert cli("ingest", "queue").json == queue_before
    assert cli("consolidate", "list").json == dirty_before
    assert cli("stale", "report").json == stale_before


def test_log_is_reserved_not_a_concept(cli, wiki, tmp_path):
    _ingest_two(cli, wiki, tmp_path)
    # log.md is never indexed as a concept: it doesn't appear in search or graph.
    ids_in_graph = cli("graph", "orphans").json
    assert "log" not in ids_in_graph
    # And search never returns it.
    hits = cli("search", "write-page alpha beta").json
    assert all(h["id"] != "log" for h in hits)
    # index.md doesn't list log.md as an item either.
    index = (wiki.bundle / "index.md").read_text(encoding="utf-8")
    assert "log.md" not in index
