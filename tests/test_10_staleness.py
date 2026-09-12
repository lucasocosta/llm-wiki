"""Ticket 10: staleness by file content hash and by commit SHA."""

from __future__ import annotations

from llmwiki.okf.page import Page, write_page


def _ingest_markdown_page(cli, wiki, tmp_path):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source("notes.md", "# Alpha\n\nOriginal content about alpha.\n")
    item = cli("ingest", "next").json
    cf = tmp_path / "p.md"
    cf.write_text("---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\nbody\n", encoding="utf-8")
    cli(
        "ingest", "write-page",
        "--page-id", "alpha",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--content-file", str(cf),
    )


def test_file_derived_page_stale_when_content_hash_changes(cli, wiki, tmp_path):
    _ingest_markdown_page(cli, wiki, tmp_path)
    # Not stale yet.
    assert cli("stale", "report").json["stale"] == []
    # Change the Source file.
    wiki.write_source("notes.md", "# Alpha\n\nEDITED content about alpha.\n")
    report = cli("stale", "report").json["stale"]
    assert [r["id"] for r in report] == ["alpha"]
    assert report[0]["changed"][0]["kind"] == "content_hash"


def test_code_derived_page_stale_when_commit_changes(cli, wiki, tmp_path):
    wiki.write_source("proj/mod.py", "def entry():\n    return 0\n")
    wiki.write_manifest(
        sources=[
            {
                "id": "proj",
                "type": "code",
                "location": "proj",
                "allowlist": ["."],
                "commit": "sha-one",
            }
        ]
    )
    item = cli("ingest", "next").json
    cf = tmp_path / "p.md"
    cf.write_text("---\ntype: Topic\ntitle: Entry\n---\n\nbody\n", encoding="utf-8")
    cli(
        "ingest", "write-page",
        "--page-id", "entry",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--anchor", item["anchor"],
        "--content-file", str(cf),
    )
    assert cli("stale", "report").json["stale"] == []
    # Bump the pinned commit in the manifest.
    wiki.write_manifest(
        sources=[
            {
                "id": "proj",
                "type": "code",
                "location": "proj",
                "allowlist": ["."],
                "commit": "sha-two",
            }
        ]
    )
    report = cli("stale", "report").json["stale"]
    assert [r["id"] for r in report] == ["entry"]
    change = report[0]["changed"][0]
    assert change["kind"] == "commit"
    assert change["was"] == "sha-one" and change["now"] == "sha-two"


def test_reader_of_stale_page_warned_with_content(cli, wiki, tmp_path):
    _ingest_markdown_page(cli, wiki, tmp_path)
    wiki.write_source("notes.md", "# Alpha\n\nEDITED again.\n")
    payload = cli("read-page", "alpha").json
    # The reader gets the body AND a staleness warning.
    assert "body" in payload and payload["body"]
    assert payload["stale"] is not None
    assert payload["stale"]["stale"] is True


def test_page_without_verifiable_provenance_not_reported(cli, wiki):
    wiki.write_manifest()
    # A hand-written page with no provenance keys at all.
    write_page(
        wiki.page_path("manual.md"),
        Page(frontmatter={"type": "Topic", "title": "Manual"}, body="# Manual\n\ntext\n"),
    )
    assert cli("stale", "report").json["stale"] == []
    # And reading it reports stale as None (neither stale nor current).
    assert cli("read-page", "manual").json["stale"] is None


def test_staleness_triggered_by_provenance_not_type(cli, wiki, tmp_path):
    # A Reference page (not a Topic) with provenance is still checked.
    _ingest_markdown_page(cli, wiki, tmp_path)
    # The references/notes.md mirror has provenance; edit the source and it
    # should be detectable as stale through the same mechanism.
    from llmwiki.okf.page import read_page
    from llmwiki.staleness import staleness_report
    from llmwiki.manifest import load_manifest

    wiki.write_source("notes.md", "# Alpha\n\nchanged body.\n")
    manifest = load_manifest(wiki.root)
    ref = read_page(wiki.page_path("references/notes.md"))
    # Give the mirror a source_ids link so it references itself for the check.
    ref.frontmatter["source_ids"] = ["notes"]
    report = staleness_report(manifest, page_id="references/notes", page=ref)
    assert report is not None and report["stale"] is True
