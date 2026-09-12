"""Generate the real PDF fixtures used by the test suite.

Run once with reportlab installed:

    python tests/fixtures/make_pdfs.py

The generated PDFs are committed so the suite does not depend on reportlab at
run time. The "scanned" PDF is a text PDF with almost no extractable text,
standing in for a scanned page (we cannot embed a real raster cheaply, and the
behaviour under test is "below the per-page minimum", which this reproduces).
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent


def make_text_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=letter)
    c.drawString(72, 720, "Page one discusses the scheduler and how tasks are run.")
    c.drawString(72, 700, "It explains cooperative multitasking in some detail here.")
    c.showPage()
    c.drawString(72, 720, "Page two covers storage and how pages persist on disk.")
    c.drawString(72, 700, "Markdown files with YAML frontmatter are the unit of storage.")
    c.showPage()
    c.save()


def make_scanned_pdf(path: Path) -> None:
    # Two pages with essentially no extractable text (below the per-page min).
    c = canvas.Canvas(str(path), pagesize=letter)
    c.drawString(72, 720, ".")
    c.showPage()
    c.drawString(72, 720, ".")
    c.showPage()
    c.save()


if __name__ == "__main__":
    make_text_pdf(HERE / "text.pdf")
    make_scanned_pdf(HERE / "scanned.pdf")
    print("wrote text.pdf and scanned.pdf")
