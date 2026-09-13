def test_local_code_tracks_only_contributing_files(cli, wiki, worker, git):
    wiki.write_manifest(sources=[{"id": "proj", "type": "code", "location": "proj", "allowlist": ["."]}])
    module = wiki.write_source("proj/mod.py", "def entry():\n    return 1\n")
    other = wiki.write_source("proj/other.py", "def unrelated():\n    return 2\n")
    git(wiki.root, "init", "-q")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Initial sources")
    original = git(wiki.root, "rev-parse", "HEAD")
    item = cli("ingest", "next").json
    assert item["anchor"] == "symbol:entry"
    assert worker(item, "entry").exit_code == 0
    page = cli("read-page", "entry").json
    assert page["stale"]["stale"] is False
    files = page["frontmatter"]["source_versions"]["proj"]["files"]
    assert set(files) == {"mod.py"}
    assert files["mod.py"]["commit"] == original
    mirror = cli("read-page", "references/proj").json["frontmatter"]["source_provenance"]
    assert mirror["files"]["mod.py"]["commit"] == original
    other.write_text("def unrelated():\n    return 3\n")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Unrelated change")
    assert cli("read-page", "entry").json["stale"]["stale"] is False
    second = cli("ingest", "next").json
    assert worker(second, "entry").exit_code == 0
    assert set(cli("read-page", "entry").json["frontmatter"]["source_versions"]["proj"]["files"]) == {"mod.py", "other.py"}
    module.write_text("def entry():\n    return 4\n")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Changed contributing file")
    change = cli("read-page", "entry").json["stale"]["changed"][0]
    assert change["kind"] == "commit"
    assert change["was"] == original
    assert change["now"] == git(wiki.root, "rev-parse", "HEAD")
    assert "entry" in [p["id"] for p in cli("stale", "report").json["stale"]]


def test_uncommitted_local_code_is_explicitly_unverifiable(cli, wiki, worker):
    wiki.write_manifest(sources=[{"id": "proj", "type": "code", "location": "proj", "allowlist": ["."]}])
    wiki.write_source("proj/mod.py", "def entry():\n    return 1\n")
    assert worker(cli("ingest", "next").json, "entry").exit_code == 0
    result = cli("read-page", "entry")
    assert result.exit_code == 0, result.stderr
    assert result.json["stale"]["stale"] is None
    assert result.json["stale"]["unverifiable"]
    assert "entry" in [p["id"] for p in cli("stale", "report").json["unverifiable"]]


def test_dirty_local_file_is_not_attributed_to_head(cli, wiki, worker, git):
    wiki.write_manifest(sources=[{"id": "proj", "type": "code", "location": "proj", "allowlist": ["."]}])
    module = wiki.write_source("proj/mod.py", "def entry():\n    return 1\n")
    git(wiki.root, "init", "-q")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Initial")
    module.write_text("def entry():\n    return 2\n")
    assert worker(cli("ingest", "next").json, "entry").exit_code == 0
    page = cli("read-page", "entry").json
    assert page["stale"]["stale"] is None
    assert not page["frontmatter"]["source_versions"]["proj"]["files"]["mod.py"].get("commit")
