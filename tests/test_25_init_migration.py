"""Tickets 14/15: llm-wiki init --migrate and sources list-trechos."""

from __future__ import annotations

import subprocess

import pytest


def _md_src(wiki):
    wiki.write_source("doc01.md", "# Sobre ingestão\n\n" + "texto. " * 40)
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])


def test_list_trechos_returns_all_and_filters(cli, wiki):
    _md_src(wiki)
    wiki.write_source("doc02.md", "# Capítulo dois\n\n" + "texto. " * 40)
    wiki.write_manifest(
        sources=[
            {"left": None} or {"id": "md", "type": "markdown", "location": "doc01.md"}
        ]
    )
    wiki.write_manifest(
        sources=[
            {"id": "md", "type": "markdown", "location": "doc01.md"},
            {"id": "md2", "type": "markdown", "location": "doc02.md"},
        ]
    )
    all_md = cli("sources", "list-trechos", "md").json
    assert len(all_md) >= 1
    assert {t["source_id"] for t in all_md} == {"md"}
    assert all("text" not in t for t in all_md), "payload must be metadata-only by default"
    with_text = cli("sources", "list-trechos", "md", "--with-text").json
    assert all_md[0]["trecho_hash"] == with_text[0]["trecho_hash"]
    assert "text" in with_text[0]
    # Unknown source id refuses with a domain message.
    r = cli("sources", "list-trechos", "nao-existe")
    assert r.exit_code != 0
    assert "no source with id" in (r.stderr or "")


def test_init_scaffolds_selfcontained_and_refuses_overwrite(cli, tmp_path):
    r = cli("init", str(tmp_path / "proj"))
    assert r.exit_code == 0, r.stderr
    wiki_dir = tmp_path / "proj" / "llm-wiki"
    assert (wiki_dir / "llm-wiki.yml").exists()
    assert (wiki_dir / "wiki").exists() and (wiki_dir / "sources").exists()
    assert ".llmwiki/" in (tmp_path / "proj" / ".gitignore").read_text()
    again = cli("init", str(tmp_path / "proj"))
    assert again.exit_code == 2
    assert "already exists" in (again.stderr or "")


def test_init_migrate_moves_flat_layout(cli, wiki, tmp_path):
    _md_src(wiki)  # flat layout: wiki/ + sources/ + manifest at tmp_path root
    from llmwiki.cli import run

    r = run(["init", "--migrate"], cwd=tmp_path)
    assert r.exit_code == 0, r.stderr
    wiki_dir = tmp_path / "llm-wiki"
    for name in ("llm-wiki.yml", "wiki", "sources"):
        assert (wiki_dir / name).exists()
    assert not (tmp_path / "wiki").exists()  # moved, not copied
    assert (wiki_dir / ".llmwiki").exists() or not (tmp_path / ".llmwiki").exists()
    manifest = (wiki_dir / "llm-wiki.yml").read_text()
    assert "bundle_dir: wiki" in manifest
    assert "sources_dir: sources" in manifest
    # The tool works from the new directory immediately; provenance intact.
    item = run(["ingest", "next"], cwd=wiki_dir)
    assert item.exit_code == 0, item.stderr
    draft = tmp_path / "d.md"
    draft.write_text("---\ntype: Topic\n---\n\nPreserved knowledge.\n")
    from llmwiki.okf.page import read_page
    import json
    r2 = run(["ingest", "write-page", "--page-id", "pos-migracao",
              "--source-id", "md", "--trecho-hash", item.json["trecho_hash"],
              "--content-file", str(draft)], cwd=wiki_dir)
    assert r2.exit_code == 0, r2.stderr


def test_migrate_refuses_collision(cli, wiki, tmp_path):
    _md_src(wiki)
    from llmwiki.cli import run

    (tmp_path / "llm-wiki").mkdir(); 
    (tmp_path / "llm-wiki" / "wiki").mkdir()
    r = run(["init", "--migrate"], cwd=tmp_path)
    assert r.exit_code == 2
    assert "migration refused" in (r.stderr or "")
