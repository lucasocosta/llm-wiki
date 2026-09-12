"""Ticket 02: tracer bullet — ingest a Markdown, write a page, read it back.

The test plays the worker: it takes the work item the CLI emits and writes the
page an assistant would write, then asserts on disk and stdout.
"""

from __future__ import annotations

import json

from llmwiki.okf.page import read_page


def _markdown_source(wiki):
    wiki.write_manifest(
        sources=[
            {"id": "notes", "type": "markdown", "location": "notes.md", "language": "en"}
        ]
    )
    wiki.write_source(
        "notes.md",
        """
        # Concurrency

        The scheduler runs tasks cooperatively.
        """,
    )


def test_manifest_declares_bundle_sources_language_and_a_markdown_source(cli, wiki):
    _markdown_source(wiki)
    from llmwiki.manifest import load_manifest

    m = load_manifest(wiki.root)
    assert m.bundle_dir == "wiki"
    assert m.sources_dir == "sources"
    assert m.language == "pt-BR"
    assert m.sources[0].type == "markdown"


def test_ingest_next_delivers_work_item_with_extracted_trecho(cli, wiki):
    _markdown_source(wiki)
    result = cli("ingest", "next")
    assert result.exit_code == 0, result.stderr
    item = result.json
    assert item["source_id"] == "notes"
    assert "Concurrency" in item["text"]
    assert item["trecho_hash"]
    # header path is the Anchor for markdown
    assert item["anchor"] == "Concurrency"


def test_worker_write_stamps_generated_and_trecho_even_when_omitted(cli, wiki, tmp_path):
    _markdown_source(wiki)
    item = cli("ingest", "next").json
    # The worker writes a page WITHOUT generated / trechos in the frontmatter.
    content = (
        "---\n"
        "type: Topic\n"
        "title: Concurrency\n"
        "description: How tasks are scheduled.\n"
        "---\n\n"
        "# Concurrency\n\nCooperative scheduling.\n"
    )
    cf = tmp_path / "page.md"
    cf.write_text(content, encoding="utf-8")
    result = cli(
        "ingest", "write-page",
        "--page-id", "concurrency",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--anchor", item["anchor"],
        "--content-file", str(cf),
    )
    assert result.exit_code == 0, result.stderr
    page = read_page(wiki.page_path("concurrency.md"))
    assert page.frontmatter["type"] == "Topic"
    assert page.frontmatter["generated"]  # stamped by the tool
    assert page.frontmatter["generated_by"] == "llm-wiki"
    assert item["trecho_hash"] in page.frontmatter["trechos"]


def test_source_mirror_born_in_references_with_rel_path_and_hash(cli, wiki, tmp_path):
    _markdown_source(wiki)
    item = cli("ingest", "next").json
    cf = tmp_path / "page.md"
    cf.write_text("---\ntype: Topic\ntitle: C\n---\n\nbody\n", encoding="utf-8")
    cli(
        "ingest", "write-page",
        "--page-id", "concurrency",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--content-file", str(cf),
    )
    ref = read_page(wiki.page_path("references/notes.md"))
    assert ref.frontmatter["type"] == "Reference"
    prov = ref.frontmatter["source_provenance"]
    assert prov["path"] == "sources/notes.md"
    assert prov["content_hash"]


def test_read_page_returns_whole_frontmatter_and_body(cli, wiki, tmp_path):
    _markdown_source(wiki)
    item = cli("ingest", "next").json
    cf = tmp_path / "page.md"
    cf.write_text("---\ntype: Topic\ntitle: C\n---\n\n# C\n\nBody paragraph.\n", encoding="utf-8")
    cli(
        "ingest", "write-page",
        "--page-id", "concurrency",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--content-file", str(cf),
    )
    result = cli("read-page", "concurrency")
    assert result.exit_code == 0, result.stderr
    payload = result.json
    assert payload["frontmatter"]["title"] == "C"
    assert "Body paragraph." in payload["body"]


def test_index_lists_the_page_with_its_description(cli, wiki, tmp_path):
    _markdown_source(wiki)
    item = cli("ingest", "next").json
    cf = tmp_path / "page.md"
    cf.write_text(
        "---\ntype: Topic\ntitle: Concurrency\ndescription: Scheduling.\n---\n\nbody\n",
        encoding="utf-8",
    )
    cli(
        "ingest", "write-page",
        "--page-id", "concurrency",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--content-file", str(cf),
    )
    index = (wiki.bundle / "index.md").read_text(encoding="utf-8")
    assert "- [Concurrency](concurrency.md) — Scheduling." in index


def test_links_are_relative_never_leading_slash(cli, wiki, tmp_path):
    _markdown_source(wiki)
    item = cli("ingest", "next").json
    cf = tmp_path / "page.md"
    cf.write_text("---\ntype: Topic\ntitle: C\n---\n\nbody\n", encoding="utf-8")
    cli(
        "ingest", "write-page",
        "--page-id", "concurrency",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--content-file", str(cf),
    )
    index = (wiki.bundle / "index.md").read_text(encoding="utf-8")
    # No link target starts with '/'.
    import re
    for target in re.findall(r"\]\(([^)]+)\)", index):
        assert not target.startswith("/"), target
