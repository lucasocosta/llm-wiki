"""Ticket 06: work item with a ranked shortlist, and the worker's tools."""

from __future__ import annotations

from llmwiki.okf.page import Page, write_page


def _two_trecho_source(wiki):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source(
        "notes.md",
        "# Scheduler basics\n\n"
        "The scheduler decides which task runs next in the runtime.\n\n"
        "# Scheduler fairness\n\n"
        "The scheduler also enforces fairness between competing tasks.\n",
    )


def test_work_item_carries_trecho_and_ranked_shortlist(cli, wiki, tmp_path):
    _two_trecho_source(wiki)
    # First Trecho → write a page about the scheduler.
    first = cli("ingest", "next").json
    cf = tmp_path / "p.md"
    cf.write_text(
        "---\ntype: Topic\ntitle: Scheduler\ndescription: The runtime scheduler.\n"
        "tags: [runtime, scheduler]\n---\n\n# Scheduler\n\nDecides which task runs.\n",
        encoding="utf-8",
    )
    cli(
        "ingest", "write-page",
        "--page-id", "scheduler",
        "--source-id", first["source_id"],
        "--trecho-hash", first["trecho_hash"],
        "--content-file", str(cf),
    )
    # Second Trecho is also about the scheduler → its shortlist should surface
    # the existing 'scheduler' page.
    second = cli("ingest", "next").json
    assert "text" in second
    ids = [c["id"] for c in second["shortlist"]]
    assert "scheduler" in ids


def test_shortlist_is_size_limited_never_full_index(cli, wiki, tmp_path):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source("notes.md", "# Topic\n\nThe scheduler runs tasks in the runtime.\n")
    # Seed ten pages that all mention 'scheduler'.
    for i in range(10):
        write_page(
            wiki.page_path(f"page{i}.md"),
            Page(
                frontmatter={
                    "type": "Topic",
                    "title": f"Scheduler note {i}",
                    "description": "About the scheduler and tasks.",
                    "tags": ["scheduler"],
                },
                body=f"# Note {i}\n\nThe scheduler runs tasks.\n",
            ),
        )
    item = cli("ingest", "next", "--shortlist-size", "3").json
    assert len(item["shortlist"]) <= 3
    assert len(item["shortlist"]) < 10  # never the full index


def test_worker_shortlist_verifiable_over_fixtures(cli, wiki):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source("notes.md", "# Q\n\nHow does storage persist pages on disk?\n")
    write_page(
        wiki.page_path("storage.md"),
        Page(
            frontmatter={"type": "Topic", "title": "Storage", "description": "Persisting pages on disk."},
            body="# Storage\n\nPages persist as Markdown on disk.\n",
        ),
    )
    write_page(
        wiki.page_path("scheduler.md"),
        Page(
            frontmatter={"type": "Topic", "title": "Scheduler", "description": "Task scheduling."},
            body="# Scheduler\n\nSchedules tasks.\n",
        ),
    )
    item = cli("ingest", "next").json
    ids = [c["id"] for c in item["shortlist"]]
    # The storage page is the relevant neighbour for a storage Trecho.
    assert ids and ids[0] == "storage"


def test_worker_shortlist_payload_shape(cli, wiki):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source("notes.md", "# Q\n\nThe scheduler runs tasks.\n")
    write_page(
        wiki.page_path("scheduler.md"),
        Page(
            frontmatter={"type": "Topic", "title": "Scheduler", "description": "Scheduling."},
            body="# Scheduler\n\nRuns tasks.\n",
        ),
    )
    item = cli("ingest", "next").json
    entry = item["shortlist"][0]
    assert set(entry.keys()) == {"id", "title", "type", "description"}
    assert "body" not in entry


def test_worker_cannot_reach_curator_commands_via_ingest(cli, wiki):
    # The worker's namespace is 'ingest' + 'search'/'read-page'. Curator escapes
    # live under 'sources'/'consolidate' — not reachable as 'ingest' subcommands.
    _two_trecho_source(wiki)
    r = cli("ingest", "remove-source-entry")
    assert r.exit_code != 0  # argparse rejects the unknown subcommand
    r2 = cli("ingest", "move-page")
    assert r2.exit_code != 0
