"""Ticket 12: graph and lint."""

from __future__ import annotations

from llmwiki.okf.page import Page, write_page


def _pages(wiki, *specs):
    wiki.write_manifest()
    for pid, body in specs:
        write_page(
            wiki.page_path(f"{pid}.md"),
            Page(frontmatter={"type": "Topic", "id": pid, "title": pid.title()}, body=body),
        )


def test_backlinks(cli, wiki):
    _pages(
        wiki,
        ("target", "# Target\n\ncontent\n"),
        ("a", "# A\n\nsee [Target](target.md).\n"),
        ("b", "# B\n\nalso [Target](target.md).\n"),
    )
    result = cli("graph", "backlinks", "target")
    assert result.exit_code == 0, result.stderr
    assert result.json == ["a", "b"]


def test_orphans_excludes_index(cli, wiki):
    _pages(
        wiki,
        ("linked", "# Linked\n\ncontent\n"),
        ("hub", "# Hub\n\nsee [Linked](linked.md).\n"),
    )
    # 'linked' has an incoming edge; 'hub' has none → hub is an orphan.
    orphans = cli("graph", "orphans").json
    assert "hub" in orphans
    assert "linked" not in orphans


def test_broken_links(cli, wiki):
    _pages(wiki, ("a", "# A\n\nsee [Ghost](ghost.md).\n"))
    broken = cli("graph", "broken-links").json
    assert broken == [{"from": "a", "to": "ghost"}]


def test_long_page_warned_with_headers_never_refused(cli, wiki):
    long_body = (
        "# Big\n\n## Section One\n\n" + ("padding. " * 200) +
        "\n\n## Section Two\n\n" + ("more. " * 200) + "\n"
    )
    _pages(wiki, ("big", long_body))
    result = cli("graph", "lint", "--long-page-chars", "500")
    assert result.exit_code == 0, result.stderr
    warned = result.json["long_pages"]
    assert len(warned) == 1
    entry = warned[0]
    assert entry["id"] == "big"
    # The headers are in the output to suggest where to cut.
    assert "Section One" in entry["headers"]
    assert "Section Two" in entry["headers"]
    # The page still exists (warned, never refused/removed).
    assert wiki.page_path("big.md").exists()
