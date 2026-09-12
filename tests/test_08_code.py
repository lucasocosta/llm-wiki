"""Ticket 08: code Sources — allowlist, symbol Anchor, commit SHA."""

from __future__ import annotations


def _code_tree(wiki):
    # A code Source under sources/, with a mix of allowed and excluded paths.
    wiki.write_source("proj/app/core.py", "def run():\n    return 1\n\nclass Engine:\n    pass\n")
    wiki.write_source("proj/app/util.py", "def helper():\n    return 2\n")
    wiki.write_source("proj/tests/test_core.py", "def test_run():\n    assert True\n")
    wiki.write_source("proj/migrations/0001.py", "SQL = 'create table'\n")


def test_allowlist_is_per_source_and_unlisted_paths_not_ingested(cli, wiki):
    _code_tree(wiki)
    wiki.write_manifest(
        sources=[
            {
                "id": "proj",
                "type": "code",
                "location": "proj",
                "allowlist": ["app"],
            }
        ]
    )
    items = cli("ingest", "queue").json
    # Only files under app/ are ingested; tests/ and migrations/ are excluded.
    assert len(items) == 2
    assert all(t["source_id"] == "proj" for t in items)


def test_report_counts_files_excluded_by_allowlist(cli, wiki):
    _code_tree(wiki)
    wiki.write_manifest(
        sources=[
            {"id": "proj", "type": "code", "location": "proj", "allowlist": ["app"]}
        ]
    )
    report = cli("ingest", "report").json
    src = report["sources"][0]
    assert src["included_files"] == 2
    # test_core.py and 0001.py are the two excluded files.
    assert src["excluded_by_allowlist"] == 2


def test_anchor_is_qualified_symbol_not_line_number(cli, wiki):
    _code_tree(wiki)
    wiki.write_manifest(
        sources=[
            {"id": "proj", "type": "code", "location": "proj", "allowlist": ["app"]}
        ]
    )
    items = cli("ingest", "queue").json
    anchors = {t["anchor"] for t in items}
    # core.py's first symbol is run(); util.py's is helper().
    assert "symbol:run" in anchors
    assert "symbol:helper" in anchors
    # No anchor is a line number.
    assert all(not a.startswith("line:") for a in anchors)


def test_source_mirror_stores_commit_sha(cli, wiki, tmp_path):
    _code_tree(wiki)
    wiki.write_manifest(
        sources=[
            {
                "id": "proj",
                "type": "code",
                "location": "proj",
                "allowlist": ["app"],
                "commit": "abc123def456",
            }
        ]
    )
    item = cli("ingest", "next").json
    cf = tmp_path / "p.md"
    cf.write_text("---\ntype: Topic\ntitle: Run\n---\n\nbody\n", encoding="utf-8")
    r = cli(
        "ingest", "write-page",
        "--page-id", "run",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--anchor", item["anchor"],
        "--content-file", str(cf),
    )
    assert r.exit_code == 0, r.stderr
    from llmwiki.okf.page import read_page

    ref = read_page(wiki.page_path("references/proj.md"))
    prov = ref.frontmatter["source_provenance"]
    assert prov["source_type"] == "code"
    assert prov["commit"] == "abc123def456"


def test_external_code_pinned_by_sha_not_copied(cli, wiki, tmp_path):
    # External checkout lives outside the repo; the manifest points at it with a
    # commit. Nothing is copied into the bundle or the sources dir.
    external = tmp_path / "external_repo"
    (external / "pkg").mkdir(parents=True)
    (external / "pkg" / "mod.py").write_text("def entry():\n    return 0\n", encoding="utf-8")

    wiki.write_manifest(
        sources=[
            {
                "id": "ext",
                "type": "code",
                "location": str(external),
                "allowlist": ["pkg"],
                "repository": "https://example.com/ext.git",
                "commit": "deadbeef",
            }
        ]
    )
    items = cli("ingest", "queue").json
    assert len(items) == 1
    assert items[0]["anchor"] == "symbol:entry"
    # The external code was not copied into sources/ or wiki/.
    assert not (wiki.sources / "ext").exists()
    assert not (wiki.bundle / "pkg").exists()
