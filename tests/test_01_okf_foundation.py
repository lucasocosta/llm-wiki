"""Ticket 01: OKF foundation — page read/write, ordered frontmatter, index.md §8."""

from __future__ import annotations

from pathlib import Path

import pytest

from llmwiki.okf import (
    Page,
    PageError,
    concept_id_from_path,
    parse_page,
    read_page,
    render_page,
    write_page,
)
from llmwiki.okf.index import generate_index_files


def test_page_round_trips_without_loss(tmp_path: Path):
    page = Page(
        frontmatter={
            "type": "Topic",
            "id": "concurrency",
            "title": "Concurrency",
            "description": "How the system schedules work.",
            "tags": ["runtime", "scheduling"],
        },
        body="# Concurrency\n\nBody text.\n",
    )
    path = tmp_path / "concurrency.md"
    write_page(path, page)
    back = read_page(path)
    assert back.frontmatter == page.frontmatter
    assert back.body.strip() == page.body.strip()


def test_frontmatter_keys_always_same_order():
    # Same logical content, different insertion order → identical output.
    a = Page(frontmatter={"title": "T", "type": "Topic", "id": "x"}, body="b")
    b = Page(frontmatter={"id": "x", "type": "Topic", "title": "T"}, body="b")
    assert render_page(a) == render_page(b)
    # And the canonical order puts id, type, title in that order.
    text = render_page(a)
    assert text.index("id:") < text.index("type:") < text.index("title:")


def test_page_without_type_is_rejected_on_write(tmp_path: Path):
    page = Page(frontmatter={"id": "x", "title": "No type"}, body="b")
    with pytest.raises(PageError):
        render_page(page)
    with pytest.raises(PageError):
        write_page(tmp_path / "x.md", page)


def test_page_without_type_is_rejected_on_read():
    text = "---\nid: x\ntitle: No type\n---\n\nbody\n"
    with pytest.raises(PageError):
        parse_page(text)


def test_concept_id_from_path(tmp_path: Path):
    bundle = tmp_path / "wiki"
    (bundle / "references").mkdir(parents=True)
    p = bundle / "references" / "notes-md.md"
    p.write_text("x", encoding="utf-8")
    assert concept_id_from_path(p, bundle) == "references/notes-md"
    top = bundle / "concurrency.md"
    top.write_text("x", encoding="utf-8")
    assert concept_id_from_path(top, bundle) == "concurrency"


def test_index_md_follows_section_8(tmp_path: Path):
    bundle = tmp_path / "wiki"
    (bundle / "references").mkdir(parents=True)
    write_page(
        bundle / "concurrency.md",
        Page(
            frontmatter={"type": "Topic", "title": "Concurrency", "description": "Sched."},
            body="body",
        ),
    )
    write_page(
        bundle / "references" / "paper.md",
        Page(
            frontmatter={"type": "Reference", "title": "Paper", "description": "A PDF."},
            body="body",
        ),
    )
    generate_index_files(bundle, language="pt-BR")

    root_index = (bundle / "index.md").read_text(encoding="utf-8")
    # Root index carries frontmatter with okf_version and language.
    assert root_index.startswith("---")
    assert "okf_version:" in root_index
    assert "language: pt-BR" in root_index
    # Body is bullets of title + link + description.
    assert "- [Concurrency](concurrency.md) — Sched." in root_index
    assert "- [references](references/index.md)" in root_index

    # Nested index has no frontmatter (§8).
    nested = (bundle / "references" / "index.md").read_text(encoding="utf-8")
    assert not nested.startswith("---")
    assert "- [Paper](paper.md) — A PDF." in nested


def test_directory_description_composed_without_network(tmp_path: Path):
    # The default describer is deterministic; the whole suite runs offline.
    bundle = tmp_path / "wiki"
    (bundle / "references").mkdir(parents=True)
    write_page(
        bundle / "references" / "paper.md",
        Page(frontmatter={"type": "Reference", "title": "Paper"}, body="b"),
    )
    generate_index_files(bundle, language="pt-BR")
    root_index = (bundle / "index.md").read_text(encoding="utf-8")
    # The directory line has a composed description ending in item count.
    assert "- [references](references/index.md) — references: 1 item." in root_index


def test_regenerate_index_command(cli, wiki):
    wiki.write_manifest()
    write_page(
        wiki.page_path("topic.md"),
        Page(frontmatter={"type": "Topic", "title": "T", "description": "D"}, body="b"),
    )
    result = cli("regenerate-index")
    assert result.exit_code == 0, result.stderr
    assert "index.md" in result.stdout
    assert (wiki.bundle / "index.md").exists()
