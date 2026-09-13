import shutil

import yaml


def test_partial_reingestion_preserves_other_page_version(cli, wiki, worker, tmp_path):
    wiki.write_manifest(sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}])
    original = "# Alpha\n\nOriginal knowledge about alpha.\n\n# Beta\n\nOriginal knowledge about beta.\n"
    wiki.write_source("notes.md", original)
    for page_id in ("alpha", "beta"):
        result = worker(cli("ingest", "next").json, page_id)
        assert result.exit_code == 0, result.stderr
    beta_before = (wiki.bundle / "beta.md").read_bytes()
    wiki.write_source("notes.md", original.replace("Original", "Changed"))
    assert {p["id"] for p in cli("stale", "report").json["stale"]} == {"alpha", "beta", "references/notes"}
    assert worker(cli("ingest", "next").json, "alpha").exit_code == 0
    assert (wiki.bundle / "beta.md").read_bytes() == beta_before
    report = cli("stale", "report").json["stale"]
    assert [p["id"] for p in report] == ["beta"]
    assert report[0]["changed"][0]["was"] != report[0]["changed"][0]["now"]
    assert cli("read-page", "beta").json["stale"]["stale"] is True
    clone = tmp_path / "clone"
    shutil.copytree(wiki.bundle, clone / "wiki")
    shutil.copytree(wiki.sources, clone / "sources")
    shutil.copy(wiki.root / "llm-wiki.yml", clone / "llm-wiki.yml")
    assert cli("stale", "report", cwd=clone).json["stale"] == report


def test_unrelated_contribution_does_not_refresh_other_source(cli, wiki, worker):
    wiki.write_manifest(sources=[{"id": s, "type": "text", "location": f"{s}.txt"} for s in ("one", "two")])
    for s in ("one", "two"):
        wiki.write_source(f"{s}.txt", f"Original information contributed by {s}.")
    assert worker(cli("ingest", "next").json, "shared").exit_code == 0
    second = cli("ingest", "next").json
    wiki.write_source("one.txt", "Changed information contributed by one.")
    assert worker(second, "shared").exit_code == 0
    page = cli("read-page", "shared").json
    assert set(page["frontmatter"]["source_versions"]) == {"one", "two"}
    assert [c["source_id"] for c in page["stale"]["changed"]] == ["one"]


def test_legacy_page_does_not_borrow_current_mirror_version(cli, wiki, worker):
    wiki.write_manifest(sources=[{"id": "notes", "type": "text", "location": "notes.txt"}])
    wiki.write_source("notes.txt", "Enough information to extract a real Trecho.")
    assert worker(cli("ingest", "next").json, "new").exit_code == 0
    (wiki.bundle / "legacy.md").write_text("---\n" + yaml.safe_dump({"type": "Topic", "source_ids": ["notes"]}) + "---\nOld knowledge.")
    report = cli("read-page", "legacy").json["stale"]
    assert report["stale"] is None
    assert report["unverifiable"]
