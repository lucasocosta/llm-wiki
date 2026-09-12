"""Lexical search over the machine index (ticket 03).

The machine index **never enters the context**: the CLI ranks off-model and
returns only the winners as metadata. This is the central decision of the read
half — if the model read the index to choose, it already paid the cost the wiki
existed to avoid (spec).

The index covers frontmatter *and* body, weighting title, description and tags
higher. Search is **lexical only**: no embeddings, no vector index, no local
model. The hook for hybrid search is foreseen (a pluggable scorer) but not paid
for. The default payload is id, title, ``type``, description — never the body; a
matched snippet is available behind a flag.

The index lives outside version control under ``.llmwiki/`` and is rebuilt when
the pages change (detected by an aggregate mtime/size fingerprint), because
versioning a derived index only produces merge conflicts in a file nobody
inspects (spec).
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from llmwiki.okf.page import RESERVED_FILES, concept_id_from_path, read_page

INDEX_DIR = ".llmwiki"
INDEX_FILE = "search-index.json"

# Field weights (spec: title/description/tags weigh more than body).
_WEIGHTS = {"title": 5.0, "description": 3.0, "tags": 3.0, "body": 1.0}

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def _index_dir(bundle_root: Path) -> Path:
    # Store the machine index beside the repo root (parent of the bundle), so a
    # single .llmwiki/ holds cache for the whole repo. Falls back to bundle.
    return Path(bundle_root).parent / INDEX_DIR


def _index_path(bundle_root: Path) -> Path:
    return _index_dir(bundle_root) / INDEX_FILE


def _iter_concept_pages(bundle_root: Path) -> list[Path]:
    if not Path(bundle_root).exists():
        return []
    return sorted(
        p
        for p in Path(bundle_root).rglob("*.md")
        if p.name not in RESERVED_FILES
    )


def _fingerprint(bundle_root: Path) -> str:
    """Cheap change-detector: paths + sizes + mtimes of concept pages."""
    parts = []
    for p in _iter_concept_pages(bundle_root):
        st = p.stat()
        parts.append(f"{p.as_posix()}:{st.st_size}:{int(st.st_mtime_ns)}")
    return "|".join(parts)


def _field_texts(page) -> dict[str, str]:
    fm = page.frontmatter
    tags = fm.get("tags", []) or []
    if isinstance(tags, str):
        tags = [tags]
    return {
        "title": str(fm.get("title", "")),
        "description": str(fm.get("description", "")),
        "tags": " ".join(str(t) for t in tags),
        "body": page.body or "",
    }


def build_index(bundle_root: Path) -> dict:
    """Build the machine index from every concept page's frontmatter and body."""
    bundle_root = Path(bundle_root)
    docs = []
    df: Counter[str] = Counter()  # document frequency per term
    for page_file in _iter_concept_pages(bundle_root):
        page = read_page(page_file, require_type=False)
        cid = concept_id_from_path(page_file, bundle_root)
        fields = _field_texts(page)
        # Weighted term frequencies across fields.
        weighted_tf: Counter[str] = Counter()
        for field_name, text in fields.items():
            w = _WEIGHTS[field_name]
            for tok in _tokenize(text):
                weighted_tf[tok] += w
        for tok in set(weighted_tf):
            df[tok] += 1
        tags = page.frontmatter.get("tags", []) or []
        if isinstance(tags, str):
            tags = [tags]
        docs.append(
            {
                "id": cid,
                "title": str(page.frontmatter.get("title", cid)),
                "type": page.frontmatter.get("type", ""),
                "description": str(page.frontmatter.get("description", "")),
                "tags": [str(t) for t in tags],
                "tf": dict(weighted_tf),
                "body": page.body or "",
            }
        )
    return {
        "fingerprint": _fingerprint(bundle_root),
        "n_docs": len(docs),
        "df": dict(df),
        "docs": docs,
    }


def _load_or_build(bundle_root: Path) -> dict:
    """Load the cached index, rebuilding it when the pages have changed."""
    bundle_root = Path(bundle_root)
    path = _index_path(bundle_root)
    current_fp = _fingerprint(bundle_root)
    if path.exists():
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
            if cached.get("fingerprint") == current_fp:
                return cached
        except (json.JSONDecodeError, OSError):
            pass
    index = build_index(bundle_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index), encoding="utf-8")
    return index


def _score(query_tokens: list[str], doc: dict, df: dict, n_docs: int) -> float:
    """TF-IDF-style lexical score. Deterministic given the corpus."""
    score = 0.0
    tf = doc["tf"]
    for tok in query_tokens:
        if tok in tf:
            idf = math.log((n_docs + 1) / (df.get(tok, 0) + 1)) + 1.0
            score += tf[tok] * idf
    return score


def _make_snippet(body: str, query_tokens: list[str], width: int = 160) -> str:
    tokens = set(query_tokens)
    lower = body.lower()
    pos = -1
    for tok in query_tokens:
        idx = lower.find(tok)
        if idx != -1:
            pos = idx
            break
    if pos == -1:
        return body[:width].strip()
    start = max(0, pos - width // 2)
    end = min(len(body), pos + width // 2)
    snippet = body[start:end].strip().replace("\n", " ")
    return snippet


def search_index(
    bundle_root: Path,
    *,
    query: str,
    limit: int = 10,
    type_filter: str | None = None,
    tags_filter: list[str] | None = None,
    snippet: bool = False,
) -> list[dict]:
    """Rank pages by lexical relevance to ``query`` and return metadata winners.

    Filters by ``type`` and ``tags`` when given. The payload never includes the
    body; a matched snippet is included only when ``snippet`` is True. Ties are
    broken by id for a deterministic order over fixtures.
    """
    index = _load_or_build(bundle_root)
    query_tokens = _tokenize(query)
    n_docs = index["n_docs"]
    df = index["df"]

    scored = []
    for doc in index["docs"]:
        if type_filter is not None and doc["type"] != type_filter:
            continue
        if tags_filter:
            doc_tags = set(doc.get("tags", []))
            if not set(tags_filter).issubset(doc_tags):
                continue
        s = _score(query_tokens, doc, df, n_docs)
        if s <= 0:
            continue
        scored.append((s, doc))

    # Sort by score desc, then id asc — deterministic.
    scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))

    results = []
    for s, doc in scored[:limit]:
        payload = {
            "id": doc["id"],
            "title": doc["title"],
            "type": doc["type"],
            "description": doc["description"],
        }
        if snippet:
            payload["snippet"] = _make_snippet(doc["body"], query_tokens)
        results.append(payload)
    return results
