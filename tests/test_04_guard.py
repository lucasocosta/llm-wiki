"""Ticket 04: augmentation guard — six invariants, two modes.

Tests drive the guard through the CLI seam. The test plays two successive
workers: the first writes a good page, the second tries a degrading write and
must be refused with a message that names the invariant and what was lost.
"""

from __future__ import annotations

from llmwiki.okf.page import Page, write_page


def _wiki_with_source(wiki):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}]
    )
    wiki.write_source("notes.md", "# A\n\nsome text about alpha and beta and gamma\n")


def _seed_page(wiki, *, body, sources=None, trecho="h1"):
    """Write an initial page directly (playing the tool's first write)."""
    fm = {"type": "Topic", "id": "alpha", "title": "Alpha", "trechos": [trecho]}
    if sources is not None:
        fm["sources"] = sources
    write_page(wiki.page_path("alpha.md"), Page(frontmatter=fm, body=body))


def _write(cli, wiki, tmp_path, content, *, trecho_hash="h2"):
    cf = tmp_path / "w.md"
    cf.write_text(content, encoding="utf-8")
    return cli(
        "ingest", "write-page",
        "--page-id", "alpha",
        "--source-id", "notes",
        "--trecho-hash", trecho_hash,
        "--content-file", str(cf),
    )


def test_sources_is_append_only(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    _seed_page(
        wiki,
        body="# Alpha\n\nBody[^s1].\n",
        sources=[{"id": "s1", "anchor": "A"}],
    )
    # New write drops the s1 sources entry.
    result = _write(cli, wiki, tmp_path, "---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\nBody.\n")
    assert result.exit_code == 2
    assert "invariant 1" in result.stderr
    assert "s1" in result.stderr


def test_headers_preserved(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    _seed_page(wiki, body="# Alpha\n\n## Details\n\ntext\n")
    result = _write(cli, wiki, tmp_path, "---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\ntext\n")
    assert result.exit_code == 2
    assert "invariant 2" in result.stderr
    assert "Details" in result.stderr


def test_footnote_must_resolve(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    _seed_page(wiki, body="# Alpha\n\ntext\n")
    # Body cites [^ghost] but no sources entry has that id.
    result = _write(
        cli, wiki, tmp_path,
        "---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\nClaim[^ghost].\n",
    )
    assert result.exit_code == 2
    assert "invariant 3" in result.stderr
    assert "ghost" in result.stderr


def test_identity_immutable(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    _seed_page(wiki, body="# Alpha\n\ntext\n")
    # Attempt to change type.
    result = _write(
        cli, wiki, tmp_path,
        "---\ntype: Reference\nid: alpha\ntitle: Alpha\n---\n\n# Alpha\n\ntext\n",
    )
    assert result.exit_code == 2
    assert "invariant 4" in result.stderr


def test_over_shrinking_refused(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    long_body = "# Alpha\n\n" + ("padding sentence. " * 60) + "\n"
    _seed_page(wiki, body=long_body)
    result = _write(cli, wiki, tmp_path, "---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\ntiny\n")
    assert result.exit_code == 2
    assert "invariant 5" in result.stderr


def test_outgoing_links_append_only(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    # Provide a link target that exists.
    write_page(wiki.page_path("beta.md"), Page(frontmatter={"type": "Topic", "title": "Beta"}, body="b"))
    _seed_page(wiki, body="# Alpha\n\nSee [Beta](beta.md).\n")
    result = _write(cli, wiki, tmp_path, "---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\ntext\n")
    assert result.exit_code == 2
    assert "invariant 6" in result.stderr
    assert "beta.md" in result.stderr


def test_link_to_nonexistent_id_refused(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    _seed_page(wiki, body="# Alpha\n\ntext\n")
    result = _write(
        cli, wiki, tmp_path,
        "---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\nSee [Ghost](ghost.md).\n",
    )
    assert result.exit_code == 2
    assert "does not exist" in result.stderr
    assert "ghost" in result.stderr


def test_section_merge_refused_in_ingestion_accepted_in_consolidation(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    # Page with two sections, both cited, contributed by two Trechos.
    body = "# Alpha\n\n## One\n\nfirst[^s1].\n\n## Two\n\nsecond[^s2].\n"
    fm = {
        "type": "Topic",
        "id": "alpha",
        "title": "Alpha",
        "trechos": ["h1", "h2"],
        "sources": [{"id": "s1", "anchor": "A"}, {"id": "s2", "anchor": "B"}],
    }
    write_page(wiki.page_path("alpha.md"), Page(frontmatter=fm, body=body))

    # Merged version drops the "One"/"Two" headers into one section, keeping
    # both citations and the sources entries. Refused in ingestion (inv. 2)...
    merged = (
        "---\ntype: Topic\ntitle: Alpha\n"
        "sources:\n- id: s1\n  anchor: A\n- id: s2\n  anchor: B\n---\n\n"
        "# Alpha\n\nfirst[^s1]. second[^s2].\n"
    )
    ing = _write(cli, wiki, tmp_path, merged)
    assert ing.exit_code == 2
    assert "invariant 2" in ing.stderr

    # ...accepted in consolidation, because both citations survive.
    cf = tmp_path / "merged.md"
    cf.write_text(merged, encoding="utf-8")
    con = cli("consolidate", "write-page", "--page-id", "alpha", "--content-file", str(cf))
    assert con.exit_code == 0, con.stderr


def test_losing_a_citation_refused_in_both_modes(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    body = "# Alpha\n\nfirst[^s1]. second[^s2].\n"
    fm = {
        "type": "Topic",
        "id": "alpha",
        "title": "Alpha",
        "trechos": ["h1", "h2"],
        "sources": [{"id": "s1", "anchor": "A"}, {"id": "s2", "anchor": "B"}],
    }
    write_page(wiki.page_path("alpha.md"), Page(frontmatter=fm, body=body))

    # Drop the citation of s2 (but keep the sources entry) → consolidation
    # refuses (citations-preserved invariant).
    dropped = "---\ntype: Topic\ntitle: Alpha\n---\n\n# Alpha\n\nfirst[^s1].\n"
    cf = tmp_path / "d.md"
    cf.write_text(dropped, encoding="utf-8")
    con = cli("consolidate", "write-page", "--page-id", "alpha", "--content-file", str(cf))
    assert con.exit_code == 2
    assert "s2" in con.stderr


def test_typeless_new_page_refused_on_write(cli, wiki, tmp_path):
    # Spec §28: a worker page with no 'type' in its frontmatter is refused, not
    # silently stamped Topic. (A brand-new page has no prior type to inherit.)
    _wiki_with_source(wiki)
    cf = tmp_path / "w.md"
    cf.write_text("---\ntitle: No Type\n---\n\n# X\n\nbody\n", encoding="utf-8")
    result = cli(
        "ingest", "write-page",
        "--page-id", "notype",
        "--source-id", "notes",
        "--trecho-hash", "hX",
        "--content-file", str(cf),
    )
    assert result.exit_code == 2
    assert "type" in result.stderr.lower()


def test_no_write_time_escape_marker(cli, wiki, tmp_path):
    _wiki_with_source(wiki)
    _seed_page(wiki, body="# Alpha\n\n## Keep\n\ntext\n")
    # A page trying to set a "mode: consolidation"-like key in frontmatter must
    # not gain consolidation privileges; the header drop is still refused.
    content = (
        "---\ntype: Topic\ntitle: Alpha\nmode: consolidation\nescape: true\n---\n\n"
        "# Alpha\n\ntext\n"
    )
    result = _write(cli, wiki, tmp_path, content)
    assert result.exit_code == 2
    assert "invariant 2" in result.stderr
