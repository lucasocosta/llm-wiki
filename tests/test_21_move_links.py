import pytest


@pytest.mark.parametrize("old,new,outgoing,expected", [
    ("a", "nested/a", "other.md", "../other.md"),
    ("old/a", "deep/nested/a", "../other.md", "../../other.md"),
])
def test_move_preserves_link_destinations(cli, wiki, old, new, outgoing, expected):
    wiki.write_manifest()
    old_path = wiki.bundle / f"{old}.md"
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text(f"---\ntype: Topic\nid: {old}\n---\n# A\n\n[other]({outgoing}#topic) [self](a.md#self) [anchor](#local) [web](https://example.org/other.md) [mail](mailto:user@example.org)\n")
    (wiki.bundle / "other.md").write_text("---\ntype: Topic\n---\n# Other\n")
    (wiki.bundle / "caller.md").write_text(f"---\ntype: Topic\n---\n[A]({old}.md#self)\n")
    assert cli("graph", "broken-links").json == []
    result = cli("sources", "move-page", "--from", old, "--to", new)
    assert result.exit_code == 0, result.stderr
    assert not old_path.exists()
    assert cli("graph", "broken-links").json == []
    body = cli("read-page", new).json["body"]
    assert f"[other]({expected}#topic)" in body
    assert "[self](a.md#self)" in body
    assert "[anchor](#local)" in body
    assert "[web](https://example.org/other.md)" in body
    assert "[mail](mailto:user@example.org)" in body
    assert f"[A]({new}.md#self)" in cli("read-page", "caller").json["body"]
    assert "caller" in cli("graph", "backlinks", new).json
