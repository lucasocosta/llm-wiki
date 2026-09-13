"""Ticket 01: OKF behavior observed through the CLI and persisted files."""


def _source(cli, wiki):
    wiki.write_manifest(sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}])
    wiki.write_source("notes.md", "# Knowledge\n\nEnough information for one useful Trecho.\n")
    return cli("ingest", "next").json


def test_page_round_trips_without_loss(cli, wiki, worker):
    item = _source(cli, wiki)
    metadata = {"title": "Concurrency", "description": "How work is scheduled.",
                "tags": ["runtime", "scheduling"], "extension": {"unknown": "preserved"}}
    body = "# Concurrency\n\nBody text.\n"
    for _ in range(2):
        result = worker(item, "concurrency", metadata=metadata, body=body)
        assert result.exit_code == 0, result.stderr
        page = cli("read-page", "concurrency").json
        assert page["body"].strip() == body.strip()
        for key, value in metadata.items():
            assert page["frontmatter"][key] == value


def test_frontmatter_keys_always_same_order(cli, wiki, tmp_path):
    item = _source(cli, wiki)
    draft = tmp_path / "draft.md"
    outputs = []
    for fields in ("title: T\ntype: Topic\nid: x", "id: x\ntype: Topic\ntitle: T"):
        draft.write_text("---\n" + fields + "\n---\nBody.\n")
        result = cli("ingest", "write-page", "--page-id", "x", "--source-id", item["source_id"],
                     "--trecho-hash", item["trecho_hash"], "--content-file", str(draft))
        assert result.exit_code == 0, result.stderr
        outputs.append((wiki.bundle / "x.md").read_text())
    assert outputs[0] == outputs[1]
    assert outputs[0].index("id:") < outputs[0].index("type:") < outputs[0].index("title:")


def test_page_without_type_is_rejected_on_write(cli, wiki, tmp_path):
    item = _source(cli, wiki)
    draft = tmp_path / "draft.md"
    draft.write_text("---\ntitle: Missing type\n---\nBody.\n")
    result = cli("ingest", "write-page", "--page-id", "x", "--source-id", item["source_id"],
                 "--trecho-hash", item["trecho_hash"], "--content-file", str(draft))
    assert result.exit_code != 0 and "type" in result.stderr
    assert not (wiki.bundle / "x.md").exists()


def test_concept_id_derived_from_relative_path(cli, wiki):
    wiki.write_manifest()
    (wiki.bundle / "references").mkdir()
    for relative in ("references/notes-md", "concurrency"):
        (wiki.bundle / f"{relative}.md").write_text("---\ntype: Topic\ntitle: Needle\n---\nKnowledge.\n")
    assert {hit["id"] for hit in cli("search", "Needle").json} == {"references/notes-md", "concurrency"}


def test_index_md_section8_shape(cli, wiki):
    wiki.write_manifest()
    (wiki.bundle / "references").mkdir()
    (wiki.bundle / "concurrency.md").write_text("---\ntype: Topic\ntitle: Concurrency\ndescription: Sched.\n---\nBody.\n")
    (wiki.bundle / "references/paper.md").write_text("---\ntype: Reference\ntitle: Paper\ndescription: PDF.\n---\nBody.\n")
    result = cli("regenerate-index")
    assert result.exit_code == 0, result.stderr
    root = (wiki.bundle / "index.md").read_text()
    assert root.startswith("---") and "okf_version:" in root and "language: pt-BR" in root
    assert "- [Concurrency](concurrency.md) — Sched." in root
    assert "- [references](references/index.md)" in root
    nested = (wiki.bundle / "references/index.md").read_text()
    assert not nested.startswith("---")
    assert "- [Paper](paper.md) — PDF." in nested


def test_directory_description_composed_without_network(cli, wiki):
    wiki.write_manifest()
    (wiki.bundle / "references").mkdir()
    (wiki.bundle / "references/paper.md").write_text("---\ntype: Reference\ntitle: Paper\n---\nBody.\n")
    assert cli("regenerate-index").exit_code == 0
    root = (wiki.bundle / "index.md").read_text()
    assert "- [references](references/index.md) — references: 1 item." in root
    assert cli("regenerate-index").exit_code == 0
    assert (wiki.bundle / "index.md").read_text() == root


def test_regenerate_index_command(cli, wiki):
    wiki.write_manifest()
    (wiki.bundle / "topic.md").write_text("---\ntype: Topic\ntitle: T\ndescription: D\n---\nBody.\n")
    result = cli("regenerate-index")
    assert result.exit_code == 0, result.stderr
    assert "index.md" in result.stdout
    assert (wiki.bundle / "index.md").exists()
