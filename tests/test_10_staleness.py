"""Ticket 10: staleness from persisted provenance through the CLI."""


def _ingest_markdown_page(cli, wiki, worker):
    wiki.write_manifest(sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}])
    wiki.write_source("notes.md", "# Alpha\n\nOriginal content about alpha.\n")
    assert worker(cli("ingest", "next").json, "alpha").exit_code == 0


def test_file_derived_page_stale_when_content_hash_changes(cli, wiki, worker):
    _ingest_markdown_page(cli, wiki, worker)
    assert cli("stale", "report").json["stale"] == []
    wiki.write_source("notes.md", "# Alpha\n\nEDITED content about alpha.\n")
    report = cli("stale", "report").json["stale"]
    assert [r["id"] for r in report] == ["alpha", "references/notes"]
    assert report[0]["changed"][0]["kind"] == "content_hash"


def test_code_derived_page_stale_when_commit_changes(cli, wiki, worker, git):
    module = wiki.write_source("proj/mod.py", "def entry():\n    return 0\n")
    wiki.write_manifest(sources=[{"id": "proj", "type": "code", "location": "proj", "allowlist": ["."]}])
    git(wiki.root, "init", "-q")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Initial source")
    before = git(wiki.root, "rev-parse", "HEAD")
    assert worker(cli("ingest", "next").json, "entry").exit_code == 0
    assert cli("stale", "report").json["stale"] == []
    module.write_text("def entry():\n    return 1\n")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Changed source")
    report = cli("stale", "report").json["stale"]
    assert [r["id"] for r in report] == ["entry", "references/proj"]
    change = report[0]["changed"][0]
    assert change["kind"] == "commit"
    assert change["was"] == before
    assert change["now"] == git(wiki.root, "rev-parse", "HEAD")


def test_reader_of_stale_page_warned_with_content(cli, wiki, worker):
    _ingest_markdown_page(cli, wiki, worker)
    wiki.write_source("notes.md", "# Alpha\n\nEDITED content again.\n")
    payload = cli("read-page", "alpha").json
    assert payload["body"]
    assert payload["stale"]["stale"] is True


def test_page_without_verifiable_provenance_not_reported(cli, wiki):
    wiki.write_manifest()
    (wiki.bundle / "manual.md").write_text("---\ntype: Topic\ntitle: Manual\n---\nManual knowledge.\n")
    assert cli("stale", "report").json["stale"] == []
    assert cli("read-page", "manual").json["stale"] is None


def test_mirror_with_provenance_is_checked_regardless_of_type(cli, wiki, worker):
    _ingest_markdown_page(cli, wiki, worker)
    wiki.write_source("notes.md", "# Alpha\n\nChanged source content.\n")
    report = cli("read-page", "references/notes").json["stale"]
    assert report["stale"] is True
