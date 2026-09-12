"""Extraction: turn a Source into Trechos, split at natural boundaries.

Extraction never calls an LLM. Each Source type has its own extractor and its
own Anchor form (spec, ticket 07/08):

- ``markdown``: split at section headers; Anchor is the header path.
- ``text``: split at blank-line paragraph runs; heading-less text uses the
  Trecho index as its Anchor.
- ``pdf``: one Trecho per page; Anchor is the page number.
- ``code``: one Trecho per file (leaves-first ordering handled elsewhere);
  Anchor is the qualified symbol name.

A Source whose extracted text falls below a per-page/per-Trecho minimum is
*refused* with an error naming the file (ticket 07). Extraction that yields zero
text is always an error, never a zero-Trecho Source.
"""

from __future__ import annotations

import re

from llmwiki.trecho import Trecho


class ExtractionError(Exception):
    """Raised when a Source cannot be turned into Trechos (e.g. scanned PDF)."""


_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def extract_markdown(source_id: str, text: str) -> list[Trecho]:
    """Split Markdown into Trechos at section headers.

    Each Trecho is a header and the content beneath it, up to the next header of
    the same or higher level. The Anchor is the path of enclosing headers joined
    by ``" > "`` (spec: "caminho de cabeçalhos"). Content before the first
    header, if any, becomes its own Trecho with an empty-path Anchor.
    """
    lines = text.splitlines()
    trechos: list[Trecho] = []
    # A stack of (level, title) for the current header path.
    header_stack: list[tuple[int, str]] = []
    buf: list[str] = []
    current_anchor = ""

    def flush() -> None:
        nonlocal buf
        chunk = "\n".join(buf).strip()
        if chunk:
            trechos.append(
                Trecho(
                    source_id=source_id,
                    index=len(trechos),
                    text=chunk,
                    anchor=current_anchor,
                )
            )
        buf = []

    for line in lines:
        m = _HEADER_RE.match(line)
        if m:
            flush()
            level = len(m.group(1))
            title = m.group(2).strip()
            while header_stack and header_stack[-1][0] >= level:
                header_stack.pop()
            header_stack.append((level, title))
            current_anchor = " > ".join(t for _, t in header_stack)
            buf = [line]
        else:
            buf.append(line)
    flush()

    if not trechos:
        raise ExtractionError(f"source {source_id!r} produced zero text")
    return trechos


def extract_text(source_id: str, text: str) -> list[Trecho]:
    """Split plain text into Trechos at blank-line paragraph boundaries.

    Heading-less text uses the Trecho index as its Anchor (ticket 07). Stable
    because the Trecho is identified by hash, not position.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    trechos = [
        Trecho(source_id=source_id, index=i, text=p, anchor=f"trecho:{i}")
        for i, p in enumerate(paragraphs)
    ]
    if not trechos:
        raise ExtractionError(f"source {source_id!r} produced zero text")
    return trechos


# Minimum extracted characters per page below which a PDF is treated as scanned
# and refused (ticket 07). No OCR in v1.
MIN_CHARS_PER_PAGE = 20


def extract_pdf(
    source_id: str,
    pdf_path,
    *,
    min_chars_per_page: int = MIN_CHARS_PER_PAGE,
) -> list[Trecho]:
    """Extract one Trecho per PDF page; the Anchor is the page number.

    A PDF whose extracted text falls below ``min_chars_per_page`` on average is
    refused with an error naming the file — a scanned PDF fails loud rather than
    producing empty pages (spec). Zero extracted text is always an error. No OCR.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    page_texts = [(page.extract_text() or "").strip() for page in reader.pages]
    total_chars = sum(len(t) for t in page_texts)
    n_pages = len(page_texts) or 1

    if total_chars == 0:
        raise ExtractionError(
            f"PDF {pdf_path!s} produced zero extractable text; refusing "
            f"(no OCR in v1)"
        )
    if total_chars / n_pages < min_chars_per_page:
        raise ExtractionError(
            f"PDF {pdf_path!s} looks scanned: only {total_chars} chars across "
            f"{n_pages} pages (< {min_chars_per_page}/page); refusing (no OCR)"
        )

    trechos: list[Trecho] = []
    for i, text in enumerate(page_texts):
        if not text:
            continue
        trechos.append(
            Trecho(
                source_id=source_id,
                index=i,
                text=text,
                anchor=f"page:{i + 1}",
            )
        )
    if not trechos:
        raise ExtractionError(f"PDF {pdf_path!s} produced zero text")
    return trechos
