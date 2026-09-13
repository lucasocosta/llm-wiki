"""CLI command implementations.

Each command is a function ``(args, root: Path) -> int`` returning an exit code.
``register(subparsers)`` wires them onto the argparse subparser. Commands raise
:class:`CommandError` for expected failures (bad manifest, guard refusal, etc.),
which the CLI turns into a nonzero exit code and a stderr message.
"""

from __future__ import annotations

import argparse


class CommandError(Exception):
    """An expected command failure. Message goes to stderr; ``exit_code`` to the shell."""

    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


def register(sub: "argparse._SubParsersAction") -> None:
    # Imported here to avoid circular imports at module load.
    from llmwiki.commands import (
        consolidate,
        graph,
        index_cmd,
        ingest,
        init,
        query,
        sources,
        stale,
    )

    index_cmd.register(sub)
    ingest.register(sub)
    query.register(sub)
    graph.register(sub)
    stale.register(sub)
    consolidate.register(sub)
    sources.register(sub)
    init.register(sub)
