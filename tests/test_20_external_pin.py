import pytest


@pytest.mark.parametrize("state", ["matching", "other_commit", "dirty", "invalid"])
def test_external_pin_matches_the_delivered_content(cli, wiki, worker, git, tmp_path, state):
    repo = tmp_path / "external"
    repo.mkdir()
    module = repo / "mod.py"
    module.write_text("def entry():\n    return 1\n")
    git(repo, "init", "-q")
    git(repo, "add", "mod.py")
    git(repo, "commit", "-qm", "A")
    pin = git(repo, "rev-parse", "HEAD")
    if state in ("other_commit", "dirty"):
        module.write_text("def entry():\n    return 2\n")
    if state == "other_commit":
        git(repo, "add", "mod.py")
        git(repo, "commit", "-qm", "B")
    if state == "invalid":
        pin = "f" * 40
    wiki.write_manifest(sources=[{"id": "ext", "type": "code", "location": str(repo),
                                 "repository": str(repo), "commit": pin, "allowlist": ["mod.py"]}])
    before = module.read_bytes()
    head = git(repo, "rev-parse", "HEAD")
    result = cli("ingest", "next")
    if state == "matching":
        assert result.exit_code == 0, result.stderr
        assert "return 1" in result.json["text"]
        assert worker(result.json, "entry").exit_code == 0
        # A change after delivery must also be rejected at write time.
        module.write_text("def entry():\n    return 9\n")
        rejected = worker(result.json, "later")
        assert rejected.exit_code != 0
        assert not (wiki.bundle / "later.md").exists()
        module.write_bytes(before)
    else:
        assert result.exit_code != 0
        assert "ext" in result.stderr
        assert not list(wiki.bundle.glob("*.md"))
    assert module.read_bytes() == before
    assert git(repo, "rev-parse", "HEAD") == head
    assert not list(wiki.sources.iterdir())
