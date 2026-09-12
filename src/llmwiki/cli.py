"""CLI: the single test seam.

The CLI is the engine; tools/skills are the façade. Tests invoke :func:`run`
with an ``argv`` list and a working directory, in-process, and assert on the
returned exit code and captured stdout/stderr plus the files on disk. Some
tests also run the installed console script via subprocess to prove the binary
is wired up. The CLI never calls an LLM (ADR 0002).
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from pathlib import Path

from llmwiki import commands


@dataclass
class CliResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    # Parsed JSON payload when the command emitted JSON on stdout.
    json: object = field(default=None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-wiki", description=__doc__)
    parser.add_argument(
        "-C",
        "--directory",
        default=".",
        help="run as if invoked from this directory (holds the manifest)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    commands.register(sub)
    return parser


def run(argv: list[str], cwd: str | Path | None = None) -> CliResult:
    """Run the CLI in-process. Returns exit code and captured output."""
    parser = build_parser()
    out, err = io.StringIO(), io.StringIO()
    exit_code = 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            args = parser.parse_args(argv)
            root = Path(cwd) if cwd is not None else Path(args.directory)
            if cwd is not None and args.directory != ".":
                root = Path(cwd) / args.directory
            exit_code = args.func(args, root)
    except SystemExit as exc:  # argparse errors
        code = exc.code
        exit_code = code if isinstance(code, int) else (0 if code is None else 1)
    except commands.CommandError as exc:
        err.write(str(exc) + "\n")
        exit_code = exc.exit_code
    stdout, stderr = out.getvalue(), err.getvalue()
    payload = None
    stripped = stdout.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            payload = None
    return CliResult(exit_code=exit_code, stdout=stdout, stderr=stderr, json=payload)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    result = run(argv, cwd=Path.cwd())
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
