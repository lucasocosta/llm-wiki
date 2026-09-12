"""``log.md``: a human-readable, append-only history of what the tool did.

Deliberately *only history*, never state (ticket 14). If it became state it
would reintroduce the versioned merge-conflict file that the computed queue
exists to eliminate. Deleting it must not affect the queue, dirtiness or
staleness — all of which are computed from pages, not from the log.

Entries are grouped under ISO-date headers, newest first, so the file is
readable top-down and parseable by common unix tools (``grep '^## '``).
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

LOG_NAME = "log.md"
_DATE_HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2})$")


def log_path(bundle_root: Path) -> Path:
    return Path(bundle_root) / LOG_NAME


def append_log(bundle_root: Path, message: str, *, when: _dt.datetime | None = None) -> None:
    """Append an entry under today's ISO-date header, keeping newest-first order."""
    when = when or _dt.datetime.now()
    date = when.date().isoformat()
    time = when.strftime("%H:%M:%S")
    entry = f"- {time} {message}"

    path = log_path(bundle_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# Log\n\n## {date}\n\n{entry}\n", encoding="utf-8")
        return

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Collect every date header and its line index.
    date_headers = [
        (i, m.group(1)) for i, line in enumerate(lines)
        if (m := _DATE_HEADER.match(line))
    ]

    matching = next((i for i, d in date_headers if d == date), None)
    if matching is not None:
        # Append the entry to the end of that date's block.
        header_idx = matching
        insert_at = len(lines)
        for j in range(header_idx + 1, len(lines)):
            if _DATE_HEADER.match(lines[j]) or lines[j].startswith("# "):
                insert_at = j
                break
        block_end = insert_at
        while block_end - 1 > header_idx and not lines[block_end - 1].strip():
            block_end -= 1
        lines = lines[:block_end] + [entry] + lines[block_end:]
    else:
        # New date: insert its block so that dates stay sorted newest-first.
        # Find the first existing header whose date is older than ``date``.
        insert_at = None
        for i, d in date_headers:
            if d < date:
                insert_at = i
                break
        if insert_at is None:
            # Older than everything (or no headers): append at end.
            insert_at = len(lines)
        new_block = [f"## {date}", "", entry, ""]
        # Ensure a blank line separates from preceding content.
        prefix = lines[:insert_at]
        if prefix and prefix[-1].strip():
            prefix = prefix + [""]
        lines = prefix + new_block + lines[insert_at:]

    path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
