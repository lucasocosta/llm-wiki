"""OKF page: read and write a Markdown page with YAML frontmatter.

A *page* (an OKF Concept) is a Markdown file with a YAML frontmatter block.
``type`` is the only mandatory key (OKF SPEC). We extend the format freely with
our own keys; the OKF SPEC §11 forbids consumers from rejecting unknown keys or
``type`` values, which makes the extension safe (ADR 0001).

Frontmatter keys are written in a stable order so that a re-ingestion diff shows
what actually changed rather than a reshuffle (spec: "as chaves do frontmatter
saem sempre na mesma ordem").
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Reserved OKF files that are not Concepts.
RESERVED_FILES = {"index.md", "log.md"}

# Canonical frontmatter key order. Keys not listed here are appended
# afterwards, sorted, so output stays deterministic even for extension keys we
# add later.
FRONTMATTER_KEY_ORDER = [
    "id",
    "type",
    "title",
    "description",
    "tags",
    "okf_version",
    "language",
    "links",
    "sources",
    # provenance / lifecycle (our extension keys)
    "generated",
    "generated_by",
    "trechos",
    "consolidated_trechos",
    "source_ids",
    "source_provenance",
]

_FRONTMATTER_DELIM = "---"


class PageError(Exception):
    """Raised when a page violates OKF conformance (e.g. missing ``type``)."""


@dataclass
class Page:
    """An in-memory OKF page: ordered frontmatter plus Markdown body."""

    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""

    @property
    def type(self) -> Any:
        return self.frontmatter.get("type")

    @property
    def id(self) -> Any:
        return self.frontmatter.get("id")


def order_frontmatter(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Return a new dict with keys in canonical order.

    Known keys come first in ``FRONTMATTER_KEY_ORDER``; any remaining keys are
    appended in sorted order so the result is fully deterministic.
    """
    ordered: dict[str, Any] = {}
    for key in FRONTMATTER_KEY_ORDER:
        if key in frontmatter:
            ordered[key] = frontmatter[key]
    for key in sorted(k for k in frontmatter if k not in ordered):
        ordered[key] = frontmatter[key]
    return ordered


def dump_frontmatter(frontmatter: dict[str, Any]) -> str:
    """Serialise frontmatter to YAML in canonical key order."""
    ordered = order_frontmatter(frontmatter)
    buf = io.StringIO()
    yaml.safe_dump(
        ordered,
        buf,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    return buf.getvalue()


def render_page(page: Page, *, require_type: bool = True) -> str:
    """Render a page to its on-disk string form.

    Raises ``PageError`` when ``type`` is missing and ``require_type`` is set,
    which is the default for Concept pages (index.md is rendered separately).
    """
    if require_type and not page.frontmatter.get("type"):
        raise PageError("frontmatter must include a 'type' key")
    fm = dump_frontmatter(page.frontmatter)
    body = page.body
    parts = [_FRONTMATTER_DELIM, fm.rstrip("\n"), _FRONTMATTER_DELIM, ""]
    text = "\n".join(parts)
    if body:
        text += "\n" + body.rstrip("\n") + "\n"
    return text


def parse_page(text: str, *, require_type: bool = True) -> Page:
    """Parse a page string into a ``Page``.

    Raises ``PageError`` when the frontmatter block is absent/malformed, or when
    ``type`` is missing and ``require_type`` is set.
    """
    if not text.startswith(_FRONTMATTER_DELIM):
        raise PageError("page must start with a YAML frontmatter block")
    # Split off the frontmatter between the first two delimiters.
    rest = text[len(_FRONTMATTER_DELIM):]
    if rest.startswith("\n"):
        rest = rest[1:]
    end = rest.find("\n" + _FRONTMATTER_DELIM)
    if end == -1:
        raise PageError("frontmatter block is not terminated")
    fm_text = rest[:end]
    after = rest[end + len("\n" + _FRONTMATTER_DELIM):]
    if after.startswith("\n"):
        after = after[1:]
    try:
        loaded = yaml.safe_load(fm_text) if fm_text.strip() else {}
    except yaml.YAMLError as exc:
        # Report cause + remedy, not the PyYAML stack (ticket 04). The two
        # failures seen most: a bare ':' inside the value, and a tab indent.
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 1 if mark is not None else None
        hint = "quote the value (title: \"...\") when it contains ':'"
        detail = str(getattr(exc, "problem", None) or exc)
        pos = f"line {line}" if line else "frontmatter"
        raise PageError(f"invalid frontmatter YAML ({pos}): {detail}; {hint}") from exc
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise PageError("frontmatter must be a YAML mapping")
    if require_type and not loaded.get("type"):
        raise PageError("frontmatter must include a 'type' key")
    return Page(frontmatter=loaded, body=after)


def read_page(path: str | Path, *, require_type: bool = True) -> Page:
    text = Path(path).read_text(encoding="utf-8")
    return parse_page(text, require_type=require_type)


def write_page(path: str | Path, page: Page, *, require_type: bool = True) -> None:
    text = render_page(page, require_type=require_type)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def concept_id_from_path(path: str | Path, bundle_root: str | Path) -> str:
    """Derive an OKF concept id from a page's path relative to the bundle root.

    The id is the POSIX-style relative path without the ``.md`` suffix, e.g.
    ``references/notes-md`` for ``<bundle>/references/notes-md.md``. This is the
    absolute id form used inside the machine index; links between pages are
    written relative to the document directory (ADR 0001 / spec).
    """
    rel = Path(path).resolve().relative_to(Path(bundle_root).resolve())
    posix = rel.as_posix()
    if posix.endswith(".md"):
        posix = posix[: -len(".md")]
    return posix
