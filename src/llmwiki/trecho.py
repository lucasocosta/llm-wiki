"""The Trecho: the portion of a Source that one reading consumes end to end.

Delimited by a natural boundary of the Source (chapter, section, file,
function), not by a count (CONTEXT.md glossary). A Trecho is identified by the
hash of its text, not by its position, so reordering a Source does not
invalidate pages derived from it (spec: "O carimbo é o hash do Trecho, não sua
posição").
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace


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
    # Relative file path within a code Source; empty for single-file Sources.
    source_path: str = ""

    @property
    def hash(self) -> str:
        return trecho_hash(self.text)


def trecho_hash(text: str) -> str:
    """Content hash of a Trecho's text — its identity."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def limit_trechos(trechos: list[Trecho], max_chars: int) -> list[Trecho]:
    """Subdivide oversized natural units without discarding any extracted text."""
    result = []
    for trecho in trechos:
        start = 0
        while start < len(trecho.text):
            end = min(start + max_chars, len(trecho.text))
            if end < len(trecho.text):
                # Prefer a nearby line/word boundary, then fall back to a
                # Unicode character boundary for a single oversized word.
                floor = start + max_chars // 2
                newline = trecho.text.rfind("\n", floor, end)
                whitespace = trecho.text.rfind(" ", floor, end)
                boundary = newline if newline >= 0 else whitespace
                if boundary >= 0:
                    end = boundary + 1
            result.append(replace(trecho, text=trecho.text[start:end], index=len(result)))
            start = end
    return result
