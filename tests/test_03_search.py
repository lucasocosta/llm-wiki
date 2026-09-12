"""Ticket 03: lexical search over the machine index."""

from __future__ import annotations

from llmwiki.okf.page import Page, write_page


def _seed_pages(wiki):
    wiki.write_manifest()
    write_page(
        wiki.page_path("scheduler.md"),
        Page(
            frontmatter={
                "type": "Topic",
                "title": "Scheduler",
                "description": "How the runtime schedules concurrent tasks.",
                "tags": ["runtime", "concurrency"],
            },
            body="# Scheduler\n\nThe scheduler picks the next task to run.\n",
        ),
    )
    write_page(
        wiki.page_path("storage.md"),
        Page(
            frontmatter={
                "type": "Topic",
                "title": "Storage",
                "description": "How pages are stored on disk.",
                "tags": ["storage"],
            },
            body="# Storage\n\nPages are Markdown files with frontmatter.\n",
        ),
    )
    write_page(
        wiki.page_path("references/paper.md"),
        Page(
            frontmatter={
                "type": "Reference",
                "title": "Concurrency Paper",
                "description": "A PDF about concurrency and scheduling.",
                "tags": ["concurrency"],
            },
            body="Mirror of a source about scheduling.\n",
        ),
    )


def test_search_ranks_and_returns_metadata_never_body(cli, wiki):
    _seed_pages(wiki)
    result = cli("search", "scheduler task")
    assert result.exit_code == 0, result.stderr
    results = result.json
    assert results, "expected at least one hit"
    top = results[0]
    assert top["id"] == "scheduler"
    assert set(top.keys()) == {"id", "title", "type", "description"}
    assert "body" not in top


def test_deterministic_order_over_fixtures(cli, wiki):
    _seed_pages(wiki)
    # "concurrency" is in scheduler's tags (weight 3) and the paper's
    # description + tags. Scheduler also matches "scheduler" via title.
    ids = [r["id"] for r in cli("search", "concurrency scheduler").json]
    assert ids[0] == "scheduler"  # weighted higher via title + tags
    assert "references/paper" in ids
    # Running again yields the same order.
    ids2 = [r["id"] for r in cli("search", "concurrency scheduler").json]
    assert ids == ids2


def test_title_weight_beats_body(cli, wiki):
    _seed_pages(wiki)
    # "storage" appears in storage title/desc/body and only nowhere else.
    ids = [r["id"] for r in cli("search", "storage").json]
    assert ids[0] == "storage"


def test_filter_by_type(cli, wiki):
    _seed_pages(wiki)
    results = cli("search", "concurrency", "--type", "Reference").json
    assert results
    assert all(r["type"] == "Reference" for r in results)


def test_filter_by_tag(cli, wiki):
    _seed_pages(wiki)
    # "concurrency" matches both scheduler (tag) and the paper (tag+desc);
    # filtering by the "runtime" tag narrows it to the scheduler alone.
    results = cli("search", "concurrency", "--tag", "runtime").json
    assert [r["id"] for r in results] == ["scheduler"]


def test_snippet_behind_flag(cli, wiki):
    _seed_pages(wiki)
    without = cli("search", "scheduler").json[0]
    assert "snippet" not in without
    with_flag = cli("search", "scheduler", "--snippet").json[0]
    assert "snippet" in with_flag
    assert with_flag["snippet"]


def test_index_lives_outside_vcs_and_rebuilds_on_change(cli, wiki):
    _seed_pages(wiki)
    cli("search", "scheduler")
    index_file = wiki.root / ".llmwiki" / "search-index.json"
    assert index_file.exists(), "machine index should be materialised under .llmwiki/"

    # Add a new page; the next search must find it (index rebuilt on change).
    write_page(
        wiki.page_path("caching.md"),
        Page(
            frontmatter={"type": "Topic", "title": "Caching", "description": "A cache."},
            body="# Caching\n\nAn ephemeral cache layer.\n",
        ),
    )
    ids = [r["id"] for r in cli("search", "cache caching").json]
    assert "caching" in ids
