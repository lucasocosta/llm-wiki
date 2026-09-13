"""Curator project setup: ``llm-wiki init`` (ticket 14).

One command, one folder: the scaffold creates a self-contained ``llm-wiki/``
directory holding the manifest (`llm-wiki/llm-wiki.yml`), the bundle
(`llm-wiki/wiki`), the sources (`llm-wiki/sources`) and later the derived state
(`llm-wiki/.llmwiki/`, never versioned). From then on the CLI is invoked with
``-C <project>/llm-wiki``. ``--migrate`` standardizes an existing flat layout
(``wiki/``, ``sources/``, ``.llmwiki/`` at the project root) into that folder,
rewriting the manifest paths and carrying the usage log along.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from llmwiki.commands import CommandError
from llmwiki.manifest import MANIFEST_NAME, ManifestError, load_manifest

WIKI_DIR_NAME = "llm-wiki"
_MANIFEST_TEMPLATE = """bundle_dir: wiki
sources_dir: sources
language: pt-BR
max_trecho_chars: 12000
sources: []
"""

_GITIGNORE_RULES = [
    "# Estado derivado da wiki: reconstrutível a partir das páginas, nunca versionado.",
    ".llmwiki/",
    # Wiki/Fontes do curador: versionáveis por padrão (proveniência de clone).
    # Se a wiki for uso local/teste, ignore a pasta inteira: llm-wiki/
]


def cmd_init(args: argparse.Namespace, root: Path) -> int:
    target = (Path(args.dir).resolve() if getattr(args, "dir", None) else root.resolve())
    wiki_dir = target / WIKI_DIR_NAME
    try:
        if args.migrate:
            _migrate(target)
        elif (wiki_dir / MANIFEST_NAME).exists():
            raise CommandError(
                f"{wiki_dir / MANIFEST_NAME} already exists; --migrate standardizes "
                f"an existing layout, and init never overwrites content",
                exit_code=2,
            )
        elif not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            _create(target)
        else:
            _create(target)
    except CommandError:
        raise
    except (OSError, ManifestError) as exc:
        raise CommandError(str(exc)) from exc
    return 0


def _create(target: Path) -> None:
    """One self-contained folder; the contract afterwards is ``-C <dir>/llm-wiki``."""
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
    wiki_dir = target / WIKI_DIR_NAME
    if wiki_dir.exists() and not wiki_dir.is_dir():
        raise CommandError(f"{wiki_dir} exists and is not a directory", exit_code=2)
    wiki_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = wiki_dir / MANIFEST_NAME
    if manifest_path.exists() or (wiki_dir / "wiki").exists():
        raise CommandError(
            f"{wiki_dir} already exists and holds wiki state; --migrate standardizes it",
            exit_code=2,
        )
    manifest_path.write_text(_MANIFEST_TEMPLATE, encoding="utf-8")
    (wiki_dir / "wiki").mkdir(parents=True, exist_ok=True)
    (wiki_dir / "sources").mkdir(parents=True, exist_ok=True)
    _ensure_gitignore(target)
    print(f"created {manifest_path}")
    print(f"invoke: llm-wiki -C {os.path.join(target.name, WIKI_DIR_NAME)} ...")


def _migrate(target: Path) -> None:
    manifest_path = target / MANIFEST_NAME
    if not manifest_path.exists():
        raise CommandError(f"no manifest at {manifest_path}; nothing to migrate", exit_code=2)
    manifest = load_manifest(target)
    old_bundle = (target / manifest.bundle_dir).resolve()
    old_sources = (target / manifest.sources_dir).resolve()
    wiki_root = target / WIKI_DIR_NAME
    new_bundle = wiki_root / "wiki"
    new_sources = wiki_root / "sources"
    for new, old in ((new_bundle, old_bundle), (new_sources, old_sources)):
        if new.exists() and new.resolve() != old and not old.is_relative_to(new):
            raise CommandError(
                f"migration refused: {new} already exists and is not the old path; move it first",
                exit_code=2,
            )
    if wiki_root.exists() and any(wiki_root.iterdir()):
        raise CommandError(
            f"migration refused: {wiki_root} already exists with content; move it first",
            exit_code=2,
        )
    wiki_root.mkdir(parents=True, exist_ok=True)
    if not old_bundle.exists():
        raise CommandError(f"bundle dir not found: {old_bundle}", exit_code=2)
    if old_bundle != new_bundle:
        shutil.move(str(old_bundle), str(new_bundle))
    if old_sources != new_sources:
        shutil.move(str(old_sources), str(new_sources))
    old_derived = target / ".llmwiki"
    new_derived = wiki_root / ".llmwiki"
    if old_derived.exists() and new_derived != old_derived:
        new_derived.mkdir(parents=True, exist_ok=True)
        for artifact in sorted(old_derived.iterdir()):
            dest = new_derived / artifact.name
            if dest.exists():
                dest.unlink()
            shutil.move(str(artifact), str(dest))
        if not any(old_derived.iterdir()):
            old_derived.rmdir()
    lines = [
        "bundle_dir: wiki",
        "sources_dir: sources",
        f"language: {manifest.language}",
        f"max_trecho_chars: {manifest.max_trecho_chars}",
        "sources:",
    ]
    for source in manifest.sources:
        location = source.location
        if source.type == "code":
            old_manifest_dir = manifest_path.resolve().parent
            old_root = old_manifest_dir
            if manifest.bundle_dir != WIKI_DIR_NAME + "/wiki":
                pass  # original manifest layout resolved code root-relative
            resolved = (old_root / source.location).resolve()
            if not resolved.is_dir():
                resolved = (target / source.location).resolve()
            location = os.path.relpath(resolved, wiki_root).replace("\\", "/")
        lines.append(f"  - id: {source.id}")
        lines.append(f"    type: {source.type}")
        lines.append(f"    location: {location}")
        if source.language:
            lines.append(f"    language: {source.language}")
        if source.allowlist:
            lines.append(f"    allowlist: [{', '.join(repr(a) for a in source.allowlist)}]")
    # The manifest joins the self-contained folder; from now on: -C llm-wiki.
    (wiki_root / MANIFEST_NAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
    if manifest_path.resolve() != (wiki_root / MANIFEST_NAME).resolve():
        manifest_path.unlink()
    _ensure_gitignore(target)
    print(f"migrated -> {WIKI_DIR_NAME}/ (manifest, wiki, sources, .llmwiki carried; -C {WIKI_DIR_NAME} from now on)")


def _ensure_gitignore(target: Path) -> None:
    ignore = target / ".gitignore"
    rules = []
    existing = ignore.read_text(encoding="utf-8") if ignore.is_file() else ""
    if not existing.endswith("\n") and existing:
        existing += "\n"
    needed = [rule for rule in _GITIGNORE_RULES if rule not in existing]
    if needed:
        with ignore.open("a", encoding="utf-8") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            for rule in needed:
                fh.write(rule + "\n")
    print(f"gitignore guard ensured: {ignore}")


def register(sub: "argparse._SubParsersAction") -> None:
    i = sub.add_parser(
        "init",
        help="scaffold llm-wiki/{llm-wiki.yml,wiki,sources}; --migrate standardizes an existing (flat) layout",
    )
    i.add_argument("dir", nargs="?", default=None, help="project directory (default: the -C directory)")
    i.add_argument(
        "--migrate",
        action="store_true",
        help="move an existing flat layout (wiki/, sources/, .llmwiki/) into llm-wiki/ and rewrite the manifest",
    )
    i.set_defaults(func=cmd_init)
