import pytest


@pytest.mark.parametrize("mode", ["ingest", "consolidate"])
def test_citation_cannot_be_dropped(cli, wiki, worker, tmp_path, mode):
    wiki.write_manifest(sources=[{"id": "notes", "type": "text", "location": "notes.txt"}])
    wiki.write_source("notes.txt", "Enough information for a meaningful citation.")
    item = cli("ingest", "next").json
    metadata = {"sources": [{"id": "s1"}]}
    body = "# Example\n\nAn attributed claim with enough surrounding text[^s1].\n"
    assert worker(item, "example", metadata=metadata, body=body).exit_code == 0
    before = (wiki.bundle / "example.md").read_bytes()
    if mode == "ingest":
        result = worker(item, "example", metadata=metadata, body=body.replace("[^s1]", ""))
    else:
        draft = tmp_path / "consolidated.md"
        draft.write_text("---\ntype: Topic\nsources:\n- id: s1\n---\n" + body.replace("[^s1]", ""))
        result = cli("consolidate", "write-page", "--page-id", "example", "--content-file", str(draft))
    assert result.exit_code != 0
    assert "s1" in result.stderr
    assert (wiki.bundle / "example.md").read_bytes() == before
    if mode == "ingest":
        result = worker(item, "example", metadata=metadata, body=body.replace("claim", "rewritten claim"))
    else:
        draft.write_text("---\ntype: Topic\nsources:\n- id: s1\n---\n# Unified\n\nShorter claim[^s1].\n")
        result = cli("consolidate", "write-page", "--page-id", "example", "--content-file", str(draft))
    assert result.exit_code == 0, result.stderr
