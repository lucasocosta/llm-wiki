"""Tickets from the evaluation map (`.scratch/avaliacao-teste-llm-wiki/`).

02 draft pages · 03 multi-Trecho thematic consolidation · 04 error messages ·
05 usage accounting · 07 unreadable files · 08 repo-relative code location ·
01 extractor internalized.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# --- Ticket 01: extractor no longer a library-public API -------------------


def test_extractor_is_module_private():
    import llmwiki.ingestion as ingestion

    assert not hasattr(ingestion, "extract_source")
    assert hasattr(ingestion, "_extract_source")


# --- Ticket 03: write-page accepts several --trecho-hash flags ------------


def test_write_page_accumulates_multiple_trecho_hashes(cli, wiki):
    wiki.write_source("doc01.md", "# A\n\n" + "texto a. " * 40 + "\n\n# B\n\n" + "texto b. " * 40)
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])
    queue = cli("ingest", "queue").json
    h = [t["trecho_hash"] for t in queue][:2]
    assert len(h) == 2
    draft = wiki.root / "draft.md"
    draft.write_text("---\ntype: Topic\n---\n\n# Temas\n\nA e B juntos.\n")
    r = cli("ingest", "write-page", "--page-id", "temas", "--source-id", "md",
            "--trecho-hash", h[0], "--trecho-hash", h[1], "--content-file", str(draft))
    assert r.exit_code == 0, r.stderr
    page = cli("read-page", "temas").json
    assert sorted(page["frontmatter"]["trechos"]) == sorted(h)
    # Both are now covered: nothing pending remains.
    assert cli("ingest", "queue").json == []


def test_single_hash_writes_still_work(cli, wiki, worker):
    # Markdown source emphasizing multi-flag did not break the canonical path.
    wiki.write_source("doc01.md", "# A\n\n" + "texto. " * 40)
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])
    item = cli("ingest", "next").json
    r = worker(item, "uma")
    assert r.exit_code == 0, r.stderr
    assert cli("ingest", "queue").json == []


# --- Ticket 02: draft pages may carry pending links ----------------------


def test_draft_page_accepts_broken_link_and_lint_lists_it(cli, wiki):
    wiki.write_source("doc01.md", "# A\n\n" + "texto. " * 40)
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])
    item = cli("ingest", "next").json
    draft = wiki.root / "draft.md"
    draft.write_text(
        "---\ntype: Topic\ndraft: true\n---\n\nVer [futuro](futuro-que-nao-existe.md).\n"
    )
    r = cli("ingest", "write-page", "--page-id", "pendente",
            "--source-id", item["source_id"], "--trecho-hash", item["trecho_hash"],
            "--content-file", str(draft))
    assert r.exit_code == 0, r.stderr
    lint = cli("graph", "lint").json
    assert lint["draft_pages"] == ["pendente"]


def test_dropping_draft_revalidates_links(cli, wiki):
    wiki.write_source("doc01.md", "# A\n\n" + "texto. " * 40)
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])
    item = cli("ingest", "next").json
    draft = wiki.root / "draft.md"
    draft.write_text("---\ntype: Topic\ndraft: true\n---\n\nVer [x](inexistente.md).\n")
    r = cli("ingest", "write-page", "--page-id", "pag", "--source-id", item["source_id"],
            "--trecho-hash", item["trecho_hash"], "--content-file", str(draft))
    assert r.exit_code == 0, r.stderr
    # Same page, same broken link, draft flag dropped: refused.
    final = wiki.root / "final.md"
    final.write_text("---\ntype: Topic\n---\n\nVer [x](inexistente.md).\n")
    r = cli("ingest", "write-page", "--page-id", "pag", "--source-id", item["source_id"],
            "--trecho-hash", item["trecho_hash"], "--content-file", str(final))
    assert r.exit_code != 0
    assert "link target does not exist" in (r.stderr or r.stdout)


# --- Ticket 04: frontmatter errors report cause + remedy -----------------


def test_empty_content_file_message(cli, wiki):
    wiki.write_source("doc01.md", "# A\n\n" + "texto. " * 40)
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])
    item = cli("ingest", "next").json
    empty = wiki.root / "empty.md"
    empty.write_text("")
    r = cli("ingest", "write-page", "--page-id", "x", "--source-id", item["source_id"],
            "--trecho-hash", item["trecho_hash"], "--content-file", str(empty))
    assert r.exit_code == 2
    assert "content-file is empty" in (r.stderr or "")


def test_yaml_colon_message_has_remedy(cli, wiki):
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])
    wiki.write_source("doc01.md", "# A\n\n" + "texto. " * 40)
    bad = wiki.root / "bad.md"
    bad.write_text("---\ntitle: Sem: aspas aqui\ntype: Topic\n---\n\nCorpo.\n")
    r = cli("ingest", "write-page", "--page-id", "y", "--source-id", "md",
            "--trecho-hash", "0" * 64, "--content-file", str(bad))
    assert r.exit_code == 2
    assert "quote the value" in (r.stderr or "")
    assert "yaml.scanner" not in (r.stdout or "")


# --- Ticket 07: unreadable files are excluded with justification ---------


def test_binary_files_excluded_unreadable_and_reported(cli, wiki):
    wiki.write_source("app/core.py", "def run():\n    return 1\n")
    bin_path = wiki.sources / "app/cached.pyc"
    bin_path.write_bytes(b"\xcb\xfe\xed\xfa")
    wiki.write_manifest(sources=[{"id": "proj", "type": "code", "location": "app", "allowlist": ["."]}])
    report = cli("ingest", "report").json
    src = report["sources"][0]
    assert src["included_files"] == 1
    assert src["excluded_unreadable"] == 1
    # The queue still works and does not crash.
    items = cli("ingest", "queue").json
    assert len(items) == 1


def test_pycache_skipped_entirely(cli, wiki, worker):
    wiki.write_source("app/core.py", "def run():\n    return 1\n")
    cache = wiki.sources / "app/__pycache__"
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "core.py").write_text("stale reference bytes", encoding="utf-8")
    wiki.write_manifest(sources=[{"id": "proj", "type": "code", "location": "app", "allowlist": ["."]}])
    queue = cli("ingest", "queue")
    assert queue.exit_code == 0, queue.stderr
    assert len(queue.json) == 1
    result = cli("ingest", "next")
    assert result.exit_code == 0, result.stderr
    assert result.json["text"] == "def run():\n    return 1\n"
    assert result.json["trecho_hash"] == queue.json[0]["trecho_hash"]
    written = worker(result.json, "core")
    assert written.exit_code == 0, written.stderr
    assert cli("ingest", "next").json == {"work_item": None}


# --- Ticket 08: repo-relative location for local code Sources ------------


def test_repo_relative_code_location(cli, wiki):
    wiki.write_source("doc01.md", "# X\n\n" + "texto. " * 30)
    wiki.root.mkdir(exist_ok=True)
    proj = wiki.root / "projlib"
    proj.mkdir(exist_ok=True)
    (proj / "m.py").write_text("def feature():\n    return 2\n", encoding="utf-8")
    wiki.write_manifest(
        sources=[{"id": "code", "type": "code", "location": "projlib", "allowlist": ["."]}]
    )
    items = cli("ingest", "queue").json
    assert len(items) >= 1
    assert all(t["source_id"] == "code" for t in items)


# --- Ticket 05: usage accounting -----------------------------------------


def test_usage_recorded_and_summarized_in_report(cli, wiki):
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])
    wiki.write_source("doc01.md", "# A\n\n" + "texto. " * 40)
    cli("search", "texto")
    item = cli("ingest", "next").json
    item = cli("ingest", "next").json  # next twice on purpose: also twice recorded
    report = cli("ingest", "report").json
    usage = report.get("usage")
    assert usage is not None
    assert usage["total_chars"] > 0
    assert usage["by_command"]["next"] >= 1
    assert usage["by_command"]["search"] > 0
