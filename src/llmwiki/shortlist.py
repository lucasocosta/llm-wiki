"""Shortlist: a ranked list of the concepts nearest to a Trecho.

The work item carries the Trecho plus a *ranked shortlist* of neighbouring
concepts, so the worker reuses ids without the whole index entering its context
(spec, ticket 06). Same rule as the read side: the index never enters the
context, only the winners. The shortlist is size-limited and never the full
index.

Ranking reuses the lexical index (ticket 03): the Trecho text is the query.
Until the index exists, the shortlist is empty — which is exactly the first
ingestion into an empty wiki, where every id creation is genuinely new.
"""

from __future__ import annotations

from pathlib import Path

from llmwiki.trecho import Trecho


def build_shortlist(bundle_root: Path, trecho: Trecho, limit: int = 5) -> list[dict]:
    """Return up to ``limit`` neighbour-concept metadata dicts for a Trecho."""
    from llmwiki.search import search_index

    if not bundle_root.exists():
        return []
    results = search_index(bundle_root, query=trecho.text, limit=limit)
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "type": r["type"],
            "description": r["description"],
        }
        for r in results
    ]
