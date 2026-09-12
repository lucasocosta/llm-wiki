"""Ticket 07: paginated (PDF) and plain-text Sources."""

from __future__ import annotations

from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_pdf_with_text_ingested_with_page_number_anchor(cli, wiki):
    wiki.write_manifest(
        sources=[{"id": "doc", "type": "pdf", "location": "doc.pdf"}]
    )
    wiki.copy_source("doc.pdf", FIXTURES / "text.pdf")
    q = cli("ingest", "queue")
    assert q.exit_code == 0, q.stderr
    items = q.json
    assert len(items) == 2  # two pages
    anchors = {t["anchor"] for t in items}
    assert anchors == {"page:1", "page:2"}


def test_plain_text_uses_trecho_index_anchor(cli, wiki):
    wiki.write_manifest(
        sources=[{"id": "notes", "type": "text", "location": "notes.txt"}]
    )
    wiki.write_source(
        "notes.txt",
        "First paragraph about alpha and how it works.\n\n"
        "Second paragraph about beta and its purpose.\n",
    )
    items = cli("ingest", "queue").json
    assert [t["anchor"] for t in items] == ["trecho:0", "trecho:1"]


def test_scanned_pdf_refused_naming_the_file(cli, wiki):
    wiki.write_manifest(
        sources=[{"id": "scan", "type": "pdf", "location": "scan.pdf"}]
    )
    wiki.copy_source("scan.pdf", FIXTURES / "scanned.pdf")
    result = cli("ingest", "queue")
    assert result.exit_code != 0
    assert "scan.pdf" in result.stderr
    # And it did not enter the queue as a zero-Trecho success.
    assert result.json is None


def test_pdf_page_becomes_reference_with_byte_hash(cli, wiki, tmp_path):
    wiki.write_manifest(
        sources=[{"id": "doc", "type": "pdf", "location": "doc.pdf"}]
    )
    wiki.copy_source("doc.pdf", FIXTURES / "text.pdf")
    item = cli("ingest", "next").json
    cf = tmp_path / "p.md"
    cf.write_text("---\ntype: Topic\ntitle: Sched\n---\n\nbody\n", encoding="utf-8")
    r = cli(
        "ingest", "write-page",
        "--page-id", "scheduler",
        "--source-id", item["source_id"],
        "--trecho-hash", item["trecho_hash"],
        "--anchor", item["anchor"],
        "--content-file", str(cf),
    )
    assert r.exit_code == 0, r.stderr
    from llmwiki.okf.page import read_page

    ref = read_page(wiki.page_path("references/doc.md"))
    prov = ref.frontmatter["source_provenance"]
    assert prov["source_type"] == "pdf"
    assert prov["path"] == "sources/doc.pdf"
    assert prov["content_hash"]
