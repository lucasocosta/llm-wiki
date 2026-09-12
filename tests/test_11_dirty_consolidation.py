"""Ticket 11: Página Suja and the consolidation pass."""

from __future__ import annotations

from llmwiki.okf.page import Page, read_page, write_page


def _wiki(wiki):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source("notes.md", "# X\n\nThis is enough content about X to pass the minimum.\n")


def test_page_touched_by_one_trecho_not_dirty(cli, wiki):
    _wiki(wiki)
    write_page(
        wiki.page_path("a.md"),
        Page(frontmatter={"type": "Topic", "title": "A", "trechos": ["h1"]}, body="# A\n\nx\n"),
    )
    assert cli("consolidate", "list").json == []


def test_never_consolidated_page_touched_by_many_is_dirty(cli, wiki):
    _wiki(wiki)
    write_page(
        wiki.page_path("a.md"),
        Page(
            frontmatter={"type": "Topic", "title": "A", "trechos": ["h1", "h2"]},
            body="# A\n\nx\n",
        ),
    )
    assert cli("consolidate", "list").json == ["a"]


def test_consolidation_records_trechos_and_page_no_longer_dirty(cli, wiki, tmp_path):
    _wiki(wiki)
    write_page(
        wiki.page_path("a.md"),
        Page(
            frontmatter={
                "type": "Topic",
                "id": "a",
                "title": "A",
                "trechos": ["h1", "h2"],
                "sources": [{"id": "s1"}, {"id": "s2"}],
            },
            body="# A\n\nfirst[^s1]. second[^s2].\n",
        ),
    )
    assert cli("consolidate", "list").json == ["a"]

    # Consolidate: reshape prose into one voice, keeping both citations.
    cf = tmp_path / "a.md"
    cf.write_text(
        "---\ntype: Topic\ntitle: A\n---\n\n# A\n\nunified voice[^s1][^s2].\n",
        encoding="utf-8",
    )
    r = cli("consolidate", "write-page", "--page-id", "a", "--content-file", str(cf))
    assert r.exit_code == 0, r.stderr

    page = read_page(wiki.page_path("a.md"))
    assert set(page.frontmatter["consolidated_trechos"]) == {"h1", "h2"}
    # No longer dirty.
    assert cli("consolidate", "list").json == []


def test_consolidation_rereads_only_the_page_not_sources(cli, wiki, tmp_path):
    _wiki(wiki)
    write_page(
        wiki.page_path("a.md"),
        Page(
            frontmatter={"type": "Topic", "id": "a", "title": "A", "trechos": ["h1", "h2"]},
            body="# A\n\ntext\n",
        ),
    )
    # Delete the Source file entirely — consolidation must still succeed,
    # proving it does not reopen the Source.
    (wiki.sources / "notes.md").unlink()
    cf = tmp_path / "a.md"
    cf.write_text("---\ntype: Topic\ntitle: A\n---\n\n# A\n\ntext\n", encoding="utf-8")
    r = cli("consolidate", "write-page", "--page-id", "a", "--content-file", str(cf))
    assert r.exit_code == 0, r.stderr


def test_pass_never_fires_during_ingestion(cli, wiki, tmp_path):
    # There is no consolidation subcommand under 'ingest'; consolidation is a
    # separate, opt-in, curator command.
    _wiki(wiki)
    r = cli("ingest", "consolidate")
    assert r.exit_code != 0  # unknown ingest subcommand
    # And a normal ingestion write does not set consolidated_trechos.
    item = cli("ingest", "next").json
    cf = tmp_path / "p.md"
    cf.write_text("---\ntype: Topic\ntitle: X\n---\n\nbody\n", encoding="utf-8")
    cli(
        "ingest", "write-page",
        "--page-id", "x",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--content-file", str(cf),
    )
    page = read_page(wiki.page_path("x.md"))
    assert "consolidated_trechos" not in page.frontmatter
