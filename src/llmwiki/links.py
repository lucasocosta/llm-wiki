"""Link resolution: turn a relative Markdown link target into a concept id.

Links between pages are relative to the document's directory, never started by
``/`` (ADR 0001): the OKF reference implementation forbids the leading ``/``
because it breaks GitHub rendering. Absolute concept ids exist only inside the
machine index. This single resolver is shared by the guard (dead-link rule) and
the graph/lint (edges), so the two never drift.
"""

from __future__ import annotations

import posixpath


def resolve_link(page_id: str, target: str) -> str | None:
    """Resolve a relative link ``target`` on page ``page_id`` to a concept id.

    Returns None for external links (http/https/mailto), pure anchors, targets
    that are not ``.md``, and leading-``/`` targets (forbidden by ADR 0001).
    """
    if target.startswith(("http://", "https://", "#", "mailto:")):
        return None
    target = target.split("#", 1)[0]
    if not target.endswith(".md") or target.startswith("/"):
        return None
    page_dir = posixpath.dirname(page_id)
    joined = posixpath.normpath(posixpath.join(page_dir, target))
    if joined.endswith(".md"):
        joined = joined[: -len(".md")]
    return joined
