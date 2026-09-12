"""Ticket 05: computed queue and resume.

The queue is derived from comparing Sources with the wiki; there is no
persisted state file, so ingestion resumes on any machine and parallel
ingestion produces no merge conflict.
"""

from __future__ import annotations

import shutil


def _multi_trecho_source(wiki):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source(
        "notes.md",
        "# Alpha\n\nAlpha content here.\n\n# Beta\n\nBeta content here.\n\n# Gamma\n\nGamma content.\n",
    )


def _write_item(cli, wiki, tmp_path, item, page_id):
    cf = tmp_path / f"{page_id}.md"
    cf.write_text(f"---\ntype: Topic\ntitle: {page_id}\n---\n\nbody\n", encoding="utf-8")
    return cli(
        "ingest", "write-page",
        "--page-id", page_id,
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--content-file", str(cf),
    )


def test_queue_derived_from_comparison_no_state_file(cli, wiki):
    _multi_trecho_source(wiki)
    q = cli("ingest", "queue").json
    assert len(q) == 3  # three headers → three Trechos
    # No versioned state file appears in the bundle or repo root.
    assert not (wiki.bundle / "queue.json").exists()
    assert not (wiki.root / "state.json").exists()
    # The only derived cache lives under the gitignored .llmwiki/.
    top_level = {p.name for p in wiki.root.iterdir()}
    assert "queue.json" not in top_level


def test_resume_without_reprocessing(cli, wiki, tmp_path):
    _multi_trecho_source(wiki)
    item = cli("ingest", "next").json
    _write_item(cli, wiki, tmp_path, item, "alpha")
    # After writing one page, the queue shrinks by exactly one and the done
    # Trecho is not offered again.
    q = cli("ingest", "queue").json
    assert len(q) == 2
    assert item["trecho_hash"] not in [t["trecho_hash"] for t in q]


def test_in_flight_item_returns_to_queue(cli, wiki):
    _multi_trecho_source(wiki)
    # Ask for the next item but never write it (simulate an interruption).
    first = cli("ingest", "next").json
    # The next call still offers the same item — it went back to the queue.
    again = cli("ingest", "next").json
    assert first["trecho_hash"] == again["trecho_hash"]


def test_same_queue_from_clone_on_another_machine(cli, wiki, tmp_path):
    _multi_trecho_source(wiki)
    item = cli("ingest", "next").json
    _write_item(cli, wiki, tmp_path, item, "alpha")
    original = cli("ingest", "queue").json

    # Clone: copy the whole repo tree to a new location (no .llmwiki cache).
    clone = tmp_path / "clone"
    shutil.copytree(wiki.root, clone, ignore=shutil.ignore_patterns(".llmwiki"))

    from llmwiki.cli import run

    cloned = run(["ingest", "queue"], cwd=clone).json
    assert [t["trecho_hash"] for t in cloned] == [t["trecho_hash"] for t in original]


def test_parallel_ingestion_no_shared_state_conflict(cli, wiki, tmp_path):
    # Two "people" write different pages from different Trechos; the queue is
    # recomputed from the pages, so nothing they both edited can conflict.
    _multi_trecho_source(wiki)
    q = cli("ingest", "queue").json
    _write_item(cli, wiki, tmp_path, q[0], "alpha")
    _write_item(cli, wiki, tmp_path, q[1], "beta")
    remaining = cli("ingest", "queue").json
    assert len(remaining) == 1
    assert remaining[0]["trecho_hash"] == q[2]["trecho_hash"]
