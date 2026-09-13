"""Contributions survive drafts that omit or forge tool-owned metadata."""

import shutil

import pytest
import yaml


@pytest.mark.parametrize("draft_metadata", [{}, {"trechos": [], "source_ids": [], "consolidated_trechos": []}])
def test_augmentation_preserves_history(cli, wiki, tmp_path, draft_metadata):
    wiki.write_manifest(sources=[
        {"id": sid, "type": "markdown", "location": f"{sid}.md"}
        for sid in ("first", "second", "third")
    ])
    for sid in ("first", "second", "third"):
        wiki.write_source(f"{sid}.md", f"# {sid}\n\nKnowledge contributed by {sid}.\n")
    draft = tmp_path / "draft.md"
    hashes = []
    for i in range(3):
        item = cli("ingest", "next").json
        hashes.append(item["trecho_hash"])
        draft.write_text("---\n" + yaml.safe_dump({"type": "Topic", **draft_metadata}) + "---\n# Example\n\nPreserved knowledge.\n")
        args = ("ingest", "write-page", "--page-id", "example", "--source-id", item["source_id"],
                "--trecho-hash", item["trecho_hash"], "--content-file", str(draft))
        result = cli(*args)
        assert result.exit_code == 0, result.stderr
        assert cli(*args).exit_code == 0  # retry must not duplicate contributions
        page = cli("read-page", "example").json["frontmatter"]
        assert page["trechos"] == hashes
        assert set(page["source_ids"]) == set(("first", "second", "third")[:i + 1])
        assert len(cli("ingest", "queue").json) == 2 - i
        assert cli("consolidate", "list").json == ([] if i == 0 else ["example"])
        if i == 1:
            result = cli("consolidate", "write-page", "--page-id", "example", "--content-file", str(draft))
            assert result.exit_code == 0, result.stderr
            assert cli("consolidate", "list").json == []
        if i == 2:
            assert page["consolidated_trechos"] == hashes[:2]

    clone = tmp_path / "clone"
    shutil.copytree(wiki.bundle, clone / "wiki")
    shutil.copytree(wiki.sources, clone / "sources")
    shutil.copy(wiki.root / "llm-wiki.yml", clone / "llm-wiki.yml")
    assert cli("ingest", "queue", cwd=clone).json == []
    assert cli("consolidate", "list", cwd=clone).json == ["example"]
