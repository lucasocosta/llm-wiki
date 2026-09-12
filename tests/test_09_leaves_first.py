"""Ticket 09: leaves-first order over the import graph."""

from __future__ import annotations


def _import_tree(wiki, extra=""):
    # leaf.py imports nothing; mid.py imports leaf; top.py imports mid.
    wiki.write_source("proj/leaf.py", "def base():\n    return 1\n")
    wiki.write_source("proj/mid.py", "import leaf\n\ndef middle():\n    return leaf.base()\n")
    wiki.write_source("proj/top.py", "import mid\n\ndef top():\n    return mid.middle()\n")
    if extra:
        wiki.write_source("proj/extra.py", extra)
    wiki.write_manifest(
        sources=[{"id": "proj", "type": "code", "location": "proj", "allowlist": ["."]}]
    )


def _order(cli):
    items = cli("ingest", "queue").json
    # Map anchors back to file identity via symbol names.
    return [t["anchor"] for t in items]


def test_queue_ordered_leaves_to_root(cli, wiki):
    _import_tree(wiki)
    anchors = _order(cli)
    # leaf's symbol 'base' before mid's 'middle' before top's 'top'.
    assert anchors.index("symbol:base") < anchors.index("symbol:middle")
    assert anchors.index("symbol:middle") < anchors.index("symbol:top")


def test_import_free_file_before_importers(cli, wiki):
    _import_tree(wiki)
    anchors = _order(cli)
    assert anchors[0] == "symbol:base"  # leaf imports nothing → first


def test_import_cycle_does_not_hang_or_duplicate(cli, wiki):
    # a imports b, b imports a — a cycle.
    wiki.write_source("proj/a.py", "import b\n\ndef fa():\n    return 1\n")
    wiki.write_source("proj/b.py", "import a\n\ndef fb():\n    return 2\n")
    wiki.write_manifest(
        sources=[{"id": "proj", "type": "code", "location": "proj", "allowlist": ["."]}]
    )
    items = cli("ingest", "queue").json
    anchors = [t["anchor"] for t in items]
    # Both files appear exactly once; the run terminates (no hang).
    assert sorted(anchors) == ["symbol:fa", "symbol:fb"]
    assert len(anchors) == len(set(anchors))


def test_high_level_module_finds_imported_concepts_in_shortlist(cli, wiki, tmp_path):
    _import_tree(wiki)
    # Ingest leaf first, writing a page whose text will match mid's import.
    leaf_item = cli("ingest", "next").json
    assert leaf_item["anchor"] == "symbol:base"
    cf = tmp_path / "leaf.md"
    cf.write_text(
        "---\ntype: Topic\ntitle: base\ndescription: The base function returning one.\n"
        "tags: [leaf, base]\n---\n\n# base\n\nReturns one. def base leaf module.\n",
        encoding="utf-8",
    )
    cli(
        "ingest", "write-page",
        "--page-id", "base",
        "--source-id", leaf_item["source_id"],
        "--trecho-hash", leaf_item["trecho_hash"],
        "--anchor", leaf_item["anchor"],
        "--content-file", str(cf),
    )
    # Next item is mid.py, which imports leaf; its shortlist should surface base.
    mid_item = cli("ingest", "next").json
    assert mid_item["anchor"] == "symbol:middle"
    ids = [c["id"] for c in mid_item["shortlist"]]
    assert "base" in ids
