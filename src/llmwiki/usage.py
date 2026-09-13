"""Usage accounting: characters served per command (ticket 05).

The library's cost promise ("the assistant receives metadata, not the wiki")
is only verifiable if the tool measures its own payload. Every payload-ful
command appends one JSONL line to ``.llmwiki/usage.jsonl``; ``ingest report``
summarizes it. The log is data for the curator, not for the assistant, so it
must never enter the machine index.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

LOG_NAME = "usage.jsonl"


def log_path(root: Path) -> Path:
    """Where the usage log lives for the wiki rooted at ``root``: `.llmwiki/`."""
    return Path(root) / ".llmwiki" / LOG_NAME


def record(root: Path, command: str, chars: int) -> None:
    """Append one accounting line. Failures never break the command itself."""
    try:
        path = log_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "date": _dt.date.today().isoformat(),
            "command": command,
            "chars": int(chars),
        }
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # telemetry must not cost correctness


def summary(root: Path) -> dict | None:
    """Totals by command, or ``None`` when nothing has been served yet."""
    path = log_path(root)
    if not path.exists():
        return None
    by_command: dict[str, int] = {}
    total = 0
    lines = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        chars = entry.get("chars", 0)
        cmd = entry.get("command", "?")
        if isinstance(chars, int):
            by_command[cmd] = by_command.get(cmd, 0) + chars
            total += chars
            lines += 1
    return {"total_chars": total, "events": lines, "by_command": by_command}
