"""The manifest: a single versioned YAML file at the repository root.

Declares, at the wiki level, the Bundle directory, the Sources directory, and
the language of the pages. Declares, per Source, a stable id, the type
(``text``/``pdf``/``markdown``/``code``), the location, and the original
language. A ``code`` Source also declares an allowlist of included paths, and
optionally an external repository pinned by commit SHA.

YAML for coherence with the frontmatter, to avoid a second config dialect
(spec). A wiki always spans many Sources; the single-project wiki is the
special case where they happen to come from one repository.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

MANIFEST_NAME = "llm-wiki.yml"

_VALID_SOURCE_TYPES = {"text", "pdf", "markdown", "code"}


class ManifestError(Exception):
    pass


@dataclass
class Source:
    id: str
    type: str
    location: str
    language: str = ""
    # code sources only
    allowlist: list[str] = field(default_factory=list)
    repository: str | None = None
    commit: str | None = None


@dataclass
class Manifest:
    bundle_dir: str
    sources_dir: str
    language: str
    sources: list[Source] = field(default_factory=list)
    root: Path = field(default=Path("."))

    @property
    def bundle_path(self) -> Path:
        return (self.root / self.bundle_dir).resolve()

    @property
    def sources_path(self) -> Path:
        return (self.root / self.sources_dir).resolve()

    def source(self, source_id: str) -> Source:
        for s in self.sources:
            if s.id == source_id:
                return s
        raise ManifestError(f"no source with id {source_id!r}")


def manifest_path(root: str | Path) -> Path:
    return Path(root) / MANIFEST_NAME


def load_manifest(root: str | Path) -> Manifest:
    root = Path(root)
    path = manifest_path(root)
    if not path.exists():
        raise ManifestError(f"manifest not found: {path}")
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    for key in ("bundle_dir", "sources_dir", "language"):
        if not data.get(key):
            raise ManifestError(f"manifest missing required key {key!r}")

    sources: list[Source] = []
    for raw in data.get("sources", []) or []:
        for key in ("id", "type", "location"):
            if not raw.get(key):
                raise ManifestError(f"source missing required key {key!r}: {raw!r}")
        stype = raw["type"]
        if stype not in _VALID_SOURCE_TYPES:
            raise ManifestError(
                f"source {raw['id']!r} has invalid type {stype!r}; "
                f"expected one of {sorted(_VALID_SOURCE_TYPES)}"
            )
        sources.append(
            Source(
                id=raw["id"],
                type=stype,
                location=raw["location"],
                language=raw.get("language", ""),
                allowlist=list(raw.get("allowlist", []) or []),
                repository=raw.get("repository"),
                commit=raw.get("commit"),
            )
        )

    return Manifest(
        bundle_dir=data["bundle_dir"],
        sources_dir=data["sources_dir"],
        language=data["language"],
        sources=sources,
        root=root,
    )
