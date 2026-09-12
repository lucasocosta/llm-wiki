"""The Trecho: the portion of a Source that one reading consumes end to end.

Delimited by a natural boundary of the Source (chapter, section, file,
function), not by a count (CONTEXT.md glossary). A Trecho is identified by the
hash of its text, not by its position, so reordering a Source does not
invalidate pages derived from it (spec: "O carimbo é o hash do Trecho, não sua
posição").
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Trecho:
    """One unit of ingestion work extracted from a Source."""

    source_id: str
    # Stable ordinal within the Source (0-based). Used for the plain-text
    # Anchor and for leaves-first ordering; never used as identity.
    index: int
    text: str
    # The natural-boundary Anchor: a header path for Markdown, a page number
    # for PDF, a qualified symbol name for code, or the Trecho index for
    # heading-less plain text. Its shape depends on the Source type.
    anchor: str

    @property
    def hash(self) -> str:
        return trecho_hash(self.text)


def trecho_hash(text: str) -> str:
    """Content hash of a Trecho's text — its identity."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
