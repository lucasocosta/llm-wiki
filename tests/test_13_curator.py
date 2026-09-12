"""Ticket 13: curator escapes — remove provenance, move page."""

from __future__ import annotations

from llmwiki.okf.page import Page, read_page, write_page


def test_remove_source_entry_by_explicit_command(cli, wiki):
    wiki.write_manifest()
    write_page(
        wiki.page_path("a.md"),
        Page(
            frontmatter={
                "type": "Topic",
                "id": "a",
                "title": "A",
                "sources": [{"id": "s1"}, {"id": "s2"}],
            },
            body="# A\n\ntext[^s1].\n",
        ),
    )
    r = cli("sources", "remove-source-entry", "--page-id", "a", "--source-entry-id", "s2")
    assert r.exit_code == 0, r.stderr
    page = read_page(wiki.page_path("a.md"))
    ids = [s["id"] for s in page.frontmatter["sources"]]
    assert ids == ["s1"]


def test_move_page_updates_referrers_and_broken_links_empty(cli, wiki):
    wiki.write_manifest()
    write_page(
        wiki.page_path("old.md"),
        Page(frontmatter={"type": "Topic", "id": "old", "title": "Old"}, body="# Old\n\nx\n"),
    )
    write_page(
        wiki.page_path("ref.md"),
        Page(
            frontmatter={"type": "Topic", "id": "ref", "title": "Ref"},
            body="# Ref\n\nsee [Old](old.md).\n",
        ),
    )
    r = cli("sources", "move-page", "--from", "old", "--to", "new")
    assert r.exit_code == 0, r.stderr
    # The page moved.
    assert not wiki.page_path("old.md").exists()
    assert wiki.page_path("new.md").exists()
    # The referrer was updated.
    ref = read_page(wiki.page_path("ref.md"))
    assert "new.md" in ref.body
    assert "old.md" not in ref.body
    # Broken-links report is empty.
    assert cli("graph", "broken-links").json == []


def test_neither_command_reachable_by_worker(cli, wiki):
    wiki.write_manifest()
    # The worker namespace is 'ingest'. The escapes live under 'sources'.
    assert cli("ingest", "remove-source-entry").exit_code != 0
    assert cli("ingest", "move-page").exit_code != 0


def test_guard_still_enforces_after_escape(cli, wiki, tmp_path):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source("notes.md", "# Alpha\n\nEnough content about alpha here to pass.\n")
    write_page(
        wiki.page_path("alpha.md"),
        Page(
            frontmatter={"type": "Topic", "id": "alpha", "title": "Alpha", "sources": [{"id": "s1"}, {"id": "s2"}]},
            body="# Alpha\n\n## Keep\n\ntext[^s1][^s2].\n",
        ),
    )
    # Curator removes a provenance entry.
    cli("sources", "remove-source-entry", "--page-id", "alpha", "--source-entry-id", "s2")

    # A subsequent common (ingestion) write that drops a header is STILL refused.
    cf = tmp_path / "w.md"
    cf.write_text(
        "---\ntype: Topic\ntitle: Alpha\nsources:\n- id: s1\n---\n\n# Alpha\n\ntext[^s1].\n",
        encoding="utf-8",
    )
    r = cli(
        "ingest", "write-page",
        "--page-id", "alpha",
        "--source-id", "notes",
        "--trecho-hash", "hX",
        "--content-file", str(cf),
    )
    assert r.exit_code == 2
    assert "invariant 2" in r.stderr  # the "Keep" header was dropped
