"""Review regressions, exercised through the CLI against temporary Bundles."""

from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize("changed_file", ["a.py", "b.py"])
def test_identical_code_files_keep_all_derivation_versions(cli, wiki, worker, git, changed_file):
    wiki.write_manifest(sources=[{"id": "code", "type": "code", "location": "app", "allowlist": ["."]}])
    for name in ("a.py", "b.py"):
        wiki.write_source(f"app/{name}", "def feature():\n    return 1\n")
    git(wiki.root, "init", "-q")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Identical sources")
    item = cli("ingest", "next").json
    result = worker(item, "feature")
    assert result.exit_code == 0, result.stderr
    page = cli("read-page", "feature").json
    assert set(page["frontmatter"]["source_versions"]["code"]["files"]) == {"a.py", "b.py"}
    assert cli("ingest", "queue").json == []
    (wiki.sources / "app" / changed_file).write_text("def feature():\n    return 2\n")
    git(wiki.root, "add", "sources")
    git(wiki.root, "commit", "-qm", "Changed contributing file")
    stale = cli("read-page", "feature").json["stale"]
    assert stale["stale"] is True
    assert {change["path"] for change in stale["changed"]} == {changed_file}
    assert "feature" in [page["id"] for page in cli("stale", "report").json["stale"]]


@pytest.mark.parametrize("kind", ["text", "markdown", "pdf"])
def test_foreign_trecho_is_refused_without_writing_any_bundle_state(cli, wiki, kind):
    location = "paper.pdf" if kind == "pdf" else "notes.md"
    wiki.write_manifest(sources=[
        {"id": "notes", "type": kind, "location": location},
        {"id": "other", "type": "text", "location": "other.txt"},
    ])
    if kind == "pdf":
        wiki.copy_source(location, Path(__file__).parent / "fixtures/text.pdf")
    else:
        prefix = "# Notes\n\n" if kind == "markdown" else ""
        wiki.write_source(location, prefix + "Enough material from the declared Source.\n")
    wiki.write_source("other.txt", "Different material from an unrelated Source.\n")
    queued = cli("ingest", "queue")
    assert queued.exit_code == 0, queued.stderr
    queue = queued.json
    own_hash = next(t["trecho_hash"] for t in queue if t["source_id"] == "notes")
    foreign_hash = next(t["trecho_hash"] for t in queue if t["source_id"] == "other")
    draft = wiki.root / "draft.md"
    draft.write_text("---\ntype: Topic\n---\nKnowledge from both Sources.\n")
    result = cli("ingest", "write-page", "--page-id", "both", "--source-id", "notes",
                 "--trecho-hash", own_hash, "--trecho-hash", foreign_hash,
                 "--content-file", str(draft))
    assert result.exit_code != 0
    assert "notes" in result.stderr and "Trecho" in result.stderr
    assert not list(wiki.bundle.rglob("*.md"))
    assert cli("ingest", "queue").json == queue


@pytest.mark.parametrize("kind", ["text", "markdown"])
def test_replaced_source_cannot_stamp_an_old_trecho_as_current(cli, wiki, worker, kind):
    wiki.write_manifest(sources=[{"id": "notes", "type": kind, "location": "notes.md"}])
    prefix = "# Notes\n\n" if kind == "markdown" else ""
    source = wiki.write_source("notes.md", prefix + "An explanation from the initial version.\n")
    delivered = cli("ingest", "next")
    assert delivered.exit_code == 0, delivered.stderr
    item = delivered.json
    assert worker(item, "notes").exit_code == 0
    before = {p: p.read_bytes() for p in wiki.bundle.rglob("*.md")}
    source.write_text(prefix + "A completely different explanation in the new version.\n")
    result = worker(item, "notes")
    assert result.exit_code != 0
    assert "Trecho" in result.stderr
    assert {p: p.read_bytes() for p in wiki.bundle.rglob("*.md")} == before
    assert cli("read-page", "notes").json["stale"]["stale"] is True


@pytest.mark.parametrize("mode", ["ingest", "consolidate"])
@pytest.mark.parametrize("conflict", [False, True])
def test_citation_details_survive_in_both_write_modes(cli, wiki, worker, mode, conflict):
    wiki.write_manifest(sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}])
    wiki.write_source("notes.md", "# Notes\n\nAn explanation with enough material to ingest.\n")
    item = cli("ingest", "next").json
    original = {"id": "n", "anchor": "Chapter 2", "uri": "references/notes.md",
                "details": {"edition": "first"}}
    body = "# Knowledge\n\nAn explanation with a citation[^n].\n"
    assert worker(item, "knowledge", body=body, metadata={"sources": [original]}).exit_code == 0
    before = {p: p.read_bytes() for p in wiki.bundle.rglob("*.md")}
    entry = {"id": "n", "description": "Additional citation metadata"}
    if conflict:
        entry["anchor"] = "Chapter 9"
    draft = wiki.root / "draft.md"
    draft.write_text("---\n" + yaml.safe_dump({"type": "Topic", "sources": [entry]}) + "---\n" + body)
    args = [mode, "write-page", "--page-id", "knowledge", "--content-file", str(draft)]
    if mode == "ingest":
        args.extend(["--source-id", "notes", "--trecho-hash", item["trecho_hash"]])
    result = cli(*args)
    if conflict:
        assert result.exit_code == 2
        assert "anchor" in result.stderr and "invariant 1" in result.stderr
        assert {p: p.read_bytes() for p in wiki.bundle.rglob("*.md")} == before
    else:
        assert result.exit_code == 0, result.stderr
        sources = cli("read-page", "knowledge").json["frontmatter"]["sources"]
        assert sources == [{**original, "description": "Additional citation metadata"}]


@pytest.mark.parametrize("bundle_dir", ["wiki", "docs/wiki"])
def test_usage_report_uses_manifest_root_with_directory_option(cli, wiki, bundle_dir):
    wiki.write_manifest(bundle_dir=bundle_dir)
    result = cli("-C", wiki.root.name, "search", "knowledge", cwd=wiki.root.parent)
    assert result.exit_code == 0, result.stderr
    report = cli("-C", wiki.root.name, "ingest", "report", cwd=wiki.root.parent)
    assert report.exit_code == 0, report.stderr
    assert report.json["usage"] == {
        "events": 1,
        "total_chars": len(result.stdout.rstrip("\n")),
        "by_command": {"search": len(result.stdout.rstrip("\n"))},
    }
