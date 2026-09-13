"""Code Sources: ingest code as reading material, not as API surface.

The wiki captures *why* the code exists and what decisions are frozen in it,
rather than becoming API docs that age each commit (spec). A code Source
declares a per-Source allowlist of included paths; an unlisted path is not
ingested, and the ingestion report says how many files were excluded, so the
exclusion doesn't pass unnoticed (ticket 08).

The citation Anchor is the *qualified symbol name* (function/class), never a
line number, so the reference survives moving files and reindentation. The
Source Mirror stores the commit SHA of the file read; external code is pinned by
SHA without copying it into the repository.
"""

from __future__ import annotations

import ast
import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

from llmwiki.trecho import Trecho


@dataclass
class CodeScan:
    """The result of scanning a code Source against its allowlist."""

    included: list[Path] = field(default_factory=list)
    excluded_count: int = 0
    # Files matching the allowlist but not decodable as UTF-8 (compiled
    # artifacts picked up by broad allowlists). Excluded with justification in
    # the ingest report (ticket 07).
    excluded_unreadable: int = 0


def _matches_allowlist(rel_posix: str, allowlist: list[str]) -> bool:
    for pattern in allowlist:
        # '.' or '' means the whole Source is included.
        if pattern in (".", "", "./"):
            return True
        norm = pattern.rstrip("/")
        # A bare directory prefix includes everything under it.
        if rel_posix == norm or rel_posix.startswith(norm + "/"):
            return True
        if fnmatch.fnmatch(rel_posix, pattern):
            return True
    return False


def scan_code_source(base: Path, allowlist: list[str]) -> CodeScan:
    """Walk ``base``, partitioning files by the allowlist.

    Only files whose path (relative to ``base``) matches the allowlist are
    included; the rest are counted as excluded. Cache directories
    (``__pycache__``) and files that are not UTF-8-decodable (compiled
    artifacts a broad allowlist might match) are never ingested: the latter
    are counted in ``excluded_unreadable`` (ticket 07).
    """
    base = Path(base)
    included: list[Path] = []
    excluded = 0
    excluded_unreadable = 0
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        parts = path.relative_to(base).parts
        if ".git" in parts or "__pycache__" in parts:
            continue
        if _matches_allowlist(rel, allowlist):
            try:
                path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                excluded_unreadable += 1
                continue
            included.append(path)
        else:
            excluded += 1
    return CodeScan(included=included, excluded_count=excluded, excluded_unreadable=excluded_unreadable)


def _qualified_symbols(source: str) -> list[str]:
    """Top-level qualified names (functions, classes, methods) in Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    names: list[str] = []

    def visit(node, prefix: str) -> None:
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qname = f"{prefix}{child.name}"
                names.append(qname)
                if isinstance(child, ast.ClassDef):
                    visit(child, prefix=f"{qname}.")

    visit(tree, prefix="")
    return names


def extract_code_file(source_id: str, path: Path, index: int) -> Trecho:
    """Extract one Trecho for a code file; Anchor is its first qualified symbol.

    A file with no symbols uses the relative file path as its Anchor (still not
    a line number).
    """
    text = Path(path).read_text(encoding="utf-8")
    symbols = _qualified_symbols(text)
    anchor = f"symbol:{symbols[0]}" if symbols else f"file:{Path(path).name}"
    return Trecho(source_id=source_id, index=index, text=text, anchor=anchor)


def _module_name(base: Path, path: Path) -> str:
    """The dotted module name of a file relative to ``base``."""
    rel = path.relative_to(base)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _imported_modules(source: str) -> set[str]:
    """Module names imported by a Python source (best-effort, static)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module)
            # relative imports: record the dotted target parts too
    return mods


def order_leaves_first(base: Path, files: list[Path]) -> list[Path]:
    """Order code files leaves-first over the intra-Source import graph.

    A file that imports another (within this Source) comes *after* it, so that
    when the worker reaches a high-level module the concepts it depends on
    already exist (spec, ticket 09). Import cycles do not hang or duplicate: they
    are broken deterministically by falling back to path order. A file that
    imports nothing appears before any file that imports it.
    """
    base = Path(base)
    name_to_file: dict[str, Path] = {}
    for f in files:
        name_to_file[_module_name(base, f)] = f

    # Build edges: importer -> imported (both within this Source).
    deps: dict[Path, set[Path]] = {f: set() for f in files}
    for f in files:
        src = f.read_text(encoding="utf-8")
        for mod in _imported_modules(src):
            # Match a full or suffix module name within the Source.
            for name, target in name_to_file.items():
                if target is f:
                    continue
                if mod == name or mod.endswith("." + name) or name.endswith("." + mod) or mod.split(".")[-1] == name.split(".")[-1]:
                    deps[f].add(target)

    # Kahn-style topological sort, leaves (no deps) first, ties by path order.
    ordered: list[Path] = []
    remaining = dict(deps)
    placed: set[Path] = set()
    file_sort = sorted(files, key=lambda p: p.as_posix())

    while remaining:
        ready = [
            f for f in file_sort
            if f in remaining and remaining[f].issubset(placed)
        ]
        if not ready:
            # A cycle: break it by taking the lowest-path remaining file.
            ready = [next(f for f in file_sort if f in remaining)]
        for f in ready:
            ordered.append(f)
            placed.add(f)
            del remaining[f]
    return ordered
