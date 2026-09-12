"""Ticket 15: skill and no-install distribution.

The skill prose itself governs model judgement and has **no honest automated
test** — asserting on its wording would test the writer, not the tool. We record
that deliberate gap here (see ``test_skill_prose_has_no_automated_assertion``)
and instead test the structural, verifiable properties: the binary runs on a
plain shell without an API key, and the skill's references go at most one level
deep.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skill" / "SKILL.md"


def _console_script() -> Path | None:
    candidate = Path(sys.executable).parent / "llm-wiki"
    return candidate if candidate.exists() else None


@pytest.mark.skipif(_console_script() is None, reason="console script not installed")
def test_binary_runs_on_a_plain_shell_without_api_key(tmp_path):
    # A minimal wiki.
    (tmp_path / "llm-wiki.yml").write_text(
        "bundle_dir: wiki\nsources_dir: sources\nlanguage: en\nsources: []\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "scheduler.md").write_text(
        "---\ntype: Topic\ntitle: Scheduler\ndescription: Schedules tasks.\n---\n\n"
        "# Scheduler\n\nRuns tasks.\n",
        encoding="utf-8",
    )
    # Scrub anything that looks like an API key from the environment.
    env = {k: v for k, v in os.environ.items() if "API_KEY" not in k.upper()}
    result = subprocess.run(
        [str(_console_script()), "search", "scheduler"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload and payload[0]["id"] == "scheduler"


@pytest.mark.skipif(_console_script() is None, reason="console script not installed")
def test_invocation_without_prior_install_via_module(tmp_path):
    # Runnable as a module (python -m style) — no separate install step needed
    # beyond having the package importable, which mirrors uvx/pipx one-shot use.
    (tmp_path / "llm-wiki.yml").write_text(
        "bundle_dir: wiki\nsources_dir: sources\nlanguage: en\nsources: []\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki").mkdir()
    result = subprocess.run(
        [sys.executable, "-c", "import sys; from llmwiki.cli import main; sys.exit(main())",
         "graph", "orphans"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == []


def test_skill_exists_and_references_go_one_level_deep():
    assert SKILL.exists()
    text = SKILL.read_text(encoding="utf-8")
    # Collect every relative markdown link in the skill.
    links = re.findall(r"\]\(([^)]+)\)", text)
    md_links = [l for l in links if l.endswith(".md")]
    assert md_links, "skill should reference at least one companion doc"
    for target in md_links:
        ref = (SKILL.parent / target).resolve()
        assert ref.exists(), f"skill references missing file: {target}"
        # The referenced doc must not itself link deeper into more .md files.
        deeper = re.findall(r"\]\(([^)]+\.md)\)", ref.read_text(encoding="utf-8"))
        assert not deeper, f"{target} references go more than one level deep: {deeper}"


def test_skill_description_is_third_person_with_triggers():
    text = SKILL.read_text(encoding="utf-8")
    # Frontmatter description block.
    m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    assert m, "skill needs a description"
    desc = m.group(1).lower()
    # Third person "Use when ..." style, not "you"/"I".
    assert "use when" in desc
    # Trigger terms are present.
    assert "wiki" in desc or "knowledge base" in desc


def test_skill_prose_has_no_automated_assertion():
    """Documented gap: the skill's *prose quality* is intentionally untested.

    The prose governs model judgement (when to reach for the wiki, how to phrase
    a query). There is no honest assertion for that — checking wording would
    test the author, not the tool — so we assert only its structure elsewhere
    and record the omission here on purpose (spec: "Fica sem teste automatizado
    a skill que ensina o assistente a usar a CLI").
    """
    assert SKILL.exists()  # structure is tested; prose quality is not, by design
