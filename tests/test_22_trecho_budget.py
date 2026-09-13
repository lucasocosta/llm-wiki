from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize("kind", ["markdown", "text", "pdf", "code"])
def test_budget_preserves_extracted_text_and_anchors(cli, wiki, worker, kind):
    text = " ".join(f"Informação {i:03d} sobre o assunto." for i in range(12))
    if kind == "pdf":
        wiki.write_manifest(sources=[{"id": "source", "type": kind, "location": "paper.pdf"}])
        wiki.copy_source("paper.pdf", Path(__file__).parent / "fixtures/text.pdf")
    elif kind == "code":
        wiki.write_manifest(sources=[{"id": "source", "type": kind, "location": "proj", "allowlist": ["."]}])
        wiki.write_source("proj/mod.py", f'def entry():\n    """{text}"""\n    return 1\n')
    else:
        wiki.write_manifest(sources=[{"id": "source", "type": kind, "location": "notes.txt"}])
        wiki.write_source("notes.txt", ("# Knowledge\n\n" if kind == "markdown" else "") + text)
    original = cli("ingest", "next").json
    assert len(original["text"]) > 40
    path = wiki.root / "llm-wiki.yml"
    manifest = yaml.safe_load(path.read_text())
    manifest["max_trecho_chars"] = 40
    path.write_text(yaml.safe_dump(manifest))
    queue = cli("ingest", "queue").json
    assert len(queue) > 1
    assert cli("ingest", "next", "--max-trecho-chars", "10000").json["text"] == original["text"]
    delivered = []
    for index in range(len(queue)):
        item = cli("ingest", "next").json
        assert 0 < len(item["text"]) <= 40
        assert item["anchor"] in {q["anchor"] for q in queue}
        assert cli("ingest", "next").json == item
        assert worker(item, f"page-{index}").exit_code == 0
        delivered.append(item)
        assert len(cli("ingest", "queue").json) == len(queue) - index - 1
    # PDF fixture has several pages: compare the first page with its subdivisions.
    first_anchor = original["anchor"]
    assert "".join(i["text"] for i in delivered if i["anchor"] == first_anchor) == original["text"]
    assert cli("ingest", "next").json == {"work_item": None}


@pytest.mark.parametrize("value", [0, -1, True, "many"])
def test_invalid_manifest_budget_is_refused(cli, wiki, value):
    path = wiki.write_manifest()
    data = yaml.safe_load(path.read_text())
    data["max_trecho_chars"] = value
    path.write_text(yaml.safe_dump(data))
    result = cli("ingest", "next")
    assert result.exit_code != 0
    assert "max_trecho_chars" in result.stderr


def test_override_keeps_small_natural_sections_and_rejects_invalid_limit(cli, wiki):
    wiki.write_manifest(sources=[{"id": "notes", "type": "markdown", "location": "notes.md"}])
    wiki.write_source("notes.md", "# Alpha\n\n" + "A" * 25 + "\n\n# Beta\n\n" + "B" * 25)
    original = cli("ingest", "queue").json
    result = cli("ingest", "queue", "--max-trecho-chars", "40")
    assert result.exit_code == 0, result.stderr
    assert result.json == original
    assert cli("ingest", "next", "--max-trecho-chars", "0").exit_code != 0


def test_default_budget_forces_a_cut(cli, wiki):
    wiki.write_manifest(sources=[{"id": "notes", "type": "text", "location": "notes.txt"}])
    wiki.write_source("notes.txt", "a" * 13000)
    assert len(cli("ingest", "next").json["text"]) <= 12000
    assert len(cli("ingest", "queue").json) == 2


def test_code_budget_override_is_repeatable_at_write_time(cli, wiki, tmp_path):
    wiki.write_manifest(sources=[{"id": "proj", "type": "code", "location": "proj", "allowlist": ["."]}])
    wiki.write_source("proj/mod.py", 'def entry():\n    """' + "A long explanation. " * 10 + '"""\n    return 1\n')
    item = cli("ingest", "next", "--max-trecho-chars", "40").json
    draft = tmp_path / "draft.md"
    draft.write_text("---\ntype: Topic\n---\nKnowledge from code.\n")
    result = cli("ingest", "write-page", "--max-trecho-chars", "40", "--page-id", "entry",
                 "--source-id", item["source_id"], "--trecho-hash", item["trecho_hash"], "--content-file", str(draft))
    assert result.exit_code == 0, result.stderr
    assert item["trecho_hash"] not in [t["trecho_hash"] for t in cli("ingest", "queue", "--max-trecho-chars", "40").json]
    assert "max_trecho_chars" not in yaml.safe_load((wiki.root / "llm-wiki.yml").read_text())
