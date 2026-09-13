"""Shared test fixtures and helpers.

The single seam under test is the CLI contract. ``cli`` invokes the entry point
via ``argv`` in-process against a temporary Bundle; a handful of tests use the
installed console script via subprocess to prove the binary is wired up. The
test *plays the worker*: it writes the pages an assistant would write. No LLM is
mocked anywhere in the suite because the CLI never calls one.
"""

from __future__ import annotations

import textwrap
import subprocess
from pathlib import Path

import pytest
import yaml

from llmwiki.cli import CliResult, run


@pytest.fixture
def git():
    def invoke(root, *args):
        return subprocess.run(
            ["git", "-c", "user.name=Wiki tests", "-c", "user.email=tests@example.invalid", *args],
            cwd=root, check=True, capture_output=True, text=True,
        ).stdout.strip()
    return invoke


@pytest.fixture
def cli(tmp_path: Path):
    """Return a callable that runs the CLI in-process, rooted at ``tmp_path``."""

    def _run(*argv: str, cwd: Path | None = None) -> CliResult:
        return run(list(argv), cwd=cwd or tmp_path)

    return _run


@pytest.fixture
def wiki(tmp_path: Path):
    """A helper for constructing a temporary Bundle + manifest + sources."""
    return WikiFixture(tmp_path)


@pytest.fixture
def worker(cli, tmp_path):
    """Write a worker draft through the public CLI, using a delivered item."""
    def write(item, page_id, *, body="# Example\n\nPreserved knowledge.\n", metadata=None):
        draft = tmp_path / "worker-draft.md"
        draft.write_text("---\n" + yaml.safe_dump({"type": "Topic", **(metadata or {})}) + "---\n" + body)
        return cli("ingest", "write-page", "--page-id", page_id,
                   "--source-id", item["source_id"], "--trecho-hash", item["trecho_hash"],
                   "--content-file", str(draft))
    return write


class WikiFixture:
    def __init__(self, root: Path):
        self.root = root
        self.bundle = root / "wiki"
        self.sources = root / "sources"

    def write_manifest(
        self,
        *,
        language: str = "pt-BR",
        bundle_dir: str = "wiki",
        sources_dir: str = "sources",
        sources: list[dict] | None = None,
    ) -> Path:
        data = {
            "bundle_dir": bundle_dir,
            "sources_dir": sources_dir,
            "language": language,
            "sources": sources or [],
        }
        path = self.root / "llm-wiki.yml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        (self.root / bundle_dir).mkdir(parents=True, exist_ok=True)
        (self.root / sources_dir).mkdir(parents=True, exist_ok=True)
        return path

    def write_source(self, rel: str, content: str) -> Path:
        path = self.sources / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content), encoding="utf-8")
        return path

    def copy_source(self, rel: str, src_path) -> Path:
        import shutil

        path = self.sources / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_path, path)
        return path

    def page_path(self, rel: str) -> Path:
        return self.bundle / rel
