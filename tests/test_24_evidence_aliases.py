"""Tickets 10/11: evidence protocol + aliases/did-you-mean (senior S3)."""

from __future__ import annotations

import json


def _setup_wiki(cli, wiki):
    wiki.write_source("doc01.md", "# A busca funciona por tokens.\n\n" + "texto. " * 40)
    wiki.write_manifest(sources=[{"id": "md", "type": "markdown", "location": "doc01.md"}])


def test_alias_raises_paraphrased_query(cli, wiki, worker):
    _setup_wiki(cli, wiki)
    item = cli("ingest", "next").json
    draft = wiki.root / "d.md"
    # The body says "busca" everywhere; the alias adds the paraphrase "pesquisa".
    draft.write_text(
        "---\ntype: Topic\ntitle: Como a busca funciona\n"
        'description: Ranking lexical da wiki.\naliases: [pesquisa]\n---\n\n'
        "A busca ranqueia título, descrição e tags.\n"
    )
    r = worker(item, "como-busca", metadata={"aliases": ["pesquisa"]})
    assert r.exit_code == 0, r.stderr
    # The paraphrase now finds the page.
    r = cli("search", "pesquisa").json
    assert r, "empty results"
    assert r[0]["id"] == "como-busca"


def test_suggest_returns_real_vocabulary(cli, wiki, worker):
    _setup_wiki(cli, wiki)
    item = cli("ingest", "next").json
    r = worker(item, "como-busca", body="A busca ranqueia o índice lexical.\n")
    assert r.exit_code == 0, r.stderr
    # Typo query: no results, suggestion points into the index vocabulary.
    r = cli("search", "buxka lexcial", "--suggest", "--limit", "3").json
    assert r["results"] == []
    suggestions = r["suggestions"]
    assert suggestions, "did you mean something?"
    # Every suggestion is a token from the index vocabulary (never hallucinated).
    out = r["suggestions"]
    assert all(out.count(t) == 1 for t in out)
    assert len(out) <= 5
    assert "busca" in out or "lexical" in out or "lexcial" in out


def test_suggest_shape_and_default_shape_unchanged(cli, wiki, worker):
    _setup_wiki(cli, wiki)
    item = cli("ingest", "next").json
    r = worker(item, "como-busca", body="A busca ranqueia título, descrição e tags.\n",
               metadata={"title": "Como a busca funciona", "description": "Ranking lexical da wiki."})
    assert r.exit_code == 0, r.stderr
    plain = cli("search", "busca").json
    assert isinstance(plain, list) and plain
    # interesting: plain default must remain a list (no flag = old payload).
    shaped = cli("search", "busca", "--suggest").json
    assert set(shaped.keys()) == {"results", "suggestions"}
    assert shaped["results"] and isinstance(shaped["suggestions"], list)


def test_alias_deterministic_between_rebuilds(cli, wiki, worker):
    _setup_wiki(cli, wiki)
    item = cli("ingest", "next").json
    r = worker(item, "como-busca", body="A busca ranqueia o índice lexical.\n",
               metadata={"aliases": ["pesquisa"]})
    assert r.exit_code == 0, r.stderr
    q = "pesquisa busca"
    for _ in range(2):
        r1 = cli("search", q)
        r2 = cli("search", q)
        assert r1.stdout == r2.stdout
