"""Generate ``index.md`` files per OKF SPEC §8.

Every directory in the Bundle gets an ``index.md`` whose body is a bullet list
of the items it contains: title, relative link, and one-line description. Only
the root ``index.md`` carries frontmatter (holding ``okf_version`` and the wiki
``language``); nested ``index.md`` files have no frontmatter (§8).

The ``index.md`` is *derived from the frontmatter of the pages*, not from the
manifest: per-item descriptions come from each page's ``description``, and a
directory's own description is composed from the items it contains — **without
an LLM**. The OKF reference agent synthesises directory descriptions by calling
Gemini; wiring that in unchanged would make the CLI call an LLM and violate
ADR 0002, so the synthesis function is injectable with a deterministic default.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from llmwiki.okf.page import (
    RESERVED_FILES,
    Page,
    concept_id_from_path,
    read_page,
    render_page,
)


@dataclass
class IndexItem:
    """One row of an ``index.md`` bullet list."""

    title: str
    link: str  # relative to the directory holding the index.md
    description: str
    is_dir: bool


# A directory-description synthesiser: given the directory name and the items
# it directly contains, return a one-line description. Injectable; the default
# is deterministic and makes no network call.
DirDescriber = Callable[[str, list[IndexItem]], str]


def default_dir_describer(dir_name: str, items: list[IndexItem]) -> str:
    """Deterministic directory description — no LLM (ADR 0002).

    Composes a plain-language summary from the items the directory contains.
    """
    if not items:
        return f"{dir_name}: (vazio)"
    n = len(items)
    noun = "item" if n == 1 else "itens"
    return f"{dir_name}: {n} {noun}."


def _title_for(page: Page, fallback: str) -> str:
    title = page.frontmatter.get("title")
    return str(title) if title else fallback


def _iter_page_files(directory: Path) -> list[Path]:
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix == ".md" and p.name not in RESERVED_FILES
    )


def _iter_subdirs(directory: Path) -> list[Path]:
    return sorted(p for p in directory.iterdir() if p.is_dir())


def build_index_items(
    directory: Path,
    bundle_root: Path,
    describer: DirDescriber,
) -> list[IndexItem]:
    """Build the ``index.md`` items for one directory.

    Subdirectories are listed first (linking to their own ``index.md``), then
    the pages in this directory, both in sorted order for determinism.
    """
    items: list[IndexItem] = []
    for sub in _iter_subdirs(directory):
        sub_items = build_index_items(sub, bundle_root, describer)
        desc = describer(sub.name, sub_items)
        items.append(
            IndexItem(
                title=sub.name,
                link=f"{sub.name}/index.md",
                description=desc,
                is_dir=True,
            )
        )
    for page_file in _iter_page_files(directory):
        page = read_page(page_file)
        title = _title_for(page, page_file.stem)
        desc = str(page.frontmatter.get("description", "")).strip()
        items.append(
            IndexItem(
                title=title,
                link=page_file.name,
                description=desc,
                is_dir=False,
            )
        )
    return items


def render_index_body(items: list[IndexItem]) -> str:
    """Render the bullet-list body of an ``index.md`` (§8)."""
    lines = []
    for item in items:
        if item.description:
            lines.append(f"- [{item.title}]({item.link}) — {item.description}")
        else:
            lines.append(f"- [{item.title}]({item.link})")
    return "\n".join(lines) + ("\n" if lines else "")


def generate_index_files(
    bundle_root: str | Path,
    *,
    language: str,
    okf_version: str = "0.2",
    describer: DirDescriber = default_dir_describer,
) -> list[Path]:
    """(Re)generate every ``index.md`` under ``bundle_root``.

    Returns the list of index files written. The root index carries frontmatter
    with ``okf_version`` and the wiki ``language``; nested indexes carry none.
    """
    bundle_root = Path(bundle_root)
    written: list[Path] = []

    def _walk(directory: Path) -> None:
        for sub in _iter_subdirs(directory):
            _walk(sub)
        items = build_index_items(directory, bundle_root, describer)
        body = render_index_body(items)
        index_path = directory / "index.md"
        is_root = directory.resolve() == bundle_root.resolve()
        if is_root:
            page = Page(
                frontmatter={
                    "okf_version": okf_version,
                    "language": language,
                },
                body=body,
            )
            text = render_page(page, require_type=False)
        else:
            text = body if body else ""
        index_path.write_text(text, encoding="utf-8")
        written.append(index_path)

    _walk(bundle_root)
    return written
