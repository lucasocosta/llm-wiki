"""The augmentation guard: refuse writes that lose provenance or coverage.

Successive writes to the same page are made by workers who don't know each
other, because a concept appears in distinct Trechos. The guard makes those
writes enrich rather than degrade. It protects *provenance and coverage, never
prose*: rewriting a paragraph is free; losing a trail is not (spec, ADR 0002).

The six invariants (ingestion mode):

1. ``sources`` is append-only. New writes are merged into the existing list by
   ``id``; removing an entry needs an explicit curator command.
2. Section headers don't disappear. Every header present before is present
   after. Renaming is remove + add, and is therefore refused.
3. Every footnote label cited in the body resolves to a ``sources`` ``id``.
4. Identity is immutable on a common write: ``type`` and ``id`` don't change.
5. Shrinkage beyond a configurable fraction is refused.
6. Outgoing links are append-only.

There is **no write-time escape marker**. The escape is the *mode of
operation*, decided by which command runs, never a key the model can set. In
**consolidation mode**, invariants 2, 5 and 6 are replaced by a single looser
one — every ``sources`` entry cited before must still be cited by some footnote
after — which frees merging sections, shrinking, and pruning duplicate links
while keeping provenance impossible to lose. Invariants 1, 3 and 4 hold in both
modes.

Refusals name the violated invariant and what was lost, so the worker can fix
it without human intervention (error-as-instruction).
"""

from __future__ import annotations

import enum
import re

from llmwiki.links import resolve_link
from llmwiki.okf.page import Page

# Default max fraction of body length a common write may drop (invariant 5).
DEFAULT_MAX_SHRINK = 0.5

_HEADER_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$", re.MULTILINE)
# Footnote-style citation used in the body, e.g. [^some-id].
_FOOTNOTE_RE = re.compile(r"\[\^([^\]]+)\]")
# Markdown link target, e.g. [text](some/target.md). Outgoing edges.
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class Mode(enum.Enum):
    INGESTION = "ingestion"
    CONSOLIDATION = "consolidation"


class GuardError(Exception):
    """A guard refusal. The message names the invariant and what was lost."""


def _headers(body: str) -> list[str]:
    return _HEADER_RE.findall(body or "")


def _footnote_labels(body: str) -> set[str]:
    return set(_FOOTNOTE_RE.findall(body or ""))


def _links(body: str) -> set[str]:
    return set(_LINK_RE.findall(body or ""))


def _source_ids(page: Page) -> list[str]:
    ids = []
    for entry in page.frontmatter.get("sources", []) or []:
        if isinstance(entry, dict) and "id" in entry:
            ids.append(str(entry["id"]))
    return ids


def _cited_source_ids(page: Page) -> set[str]:
    """Which ``sources`` ids are cited by a footnote in the body."""
    labels = _footnote_labels(page.body)
    return {sid for sid in _source_ids(page) if sid in labels}


def check_write(
    manifest,
    *,
    page_id: str,
    old: Page | None,
    new: Page,
    mode: Mode,
    max_shrink: float = DEFAULT_MAX_SHRINK,
    known_ids: set[str] | None = None,
) -> None:
    """Raise :class:`GuardError` if the write violates the guard for ``mode``.

    ``old`` is None for a brand-new page (only creation checks apply).
    ``known_ids`` is the set of concept ids that exist (for the "no link to a
    nonexistent id" rule); when None, that rule is skipped.
    On success, omitted fields of existing ``sources`` entries are restored
    in ``new`` so ingestion and consolidation preserve the same citation data.
    """
    # Invariant 3 (both modes): every footnote label resolves to a sources id.
    src_ids = set(_source_ids(new))
    for label in _footnote_labels(new.body):
        if label not in src_ids:
            raise GuardError(
                f"invariant 3 (footnote resolves): body cites footnote "
                f"[^{label}] but no sources entry has id {label!r}"
            )

    # Rule: no outgoing link to a nonexistent concept id. A page flagged
    # ``draft: true`` is exempt (ticket 02): drafts may reference pages that
    # still have to be written; the flag must be dropped (and links resolve)
    # before the page counts as finished.
    if known_ids is not None and not new.frontmatter.get("draft"):
        for target in _links(new.body):
            cid = resolve_link(page_id, target)
            if cid is None:
                continue
            if cid not in known_ids:
                raise GuardError(
                    f"link target does not exist: [{target}] resolves to id "
                    f"{cid!r}, which is not a page in the wiki"
                )

    if old is None:
        return  # creation: nothing prior to preserve.

    # Invariant 1 (both modes): sources is append-only.
    old_src = _source_ids(old)
    new_src = _source_ids(new)
    missing_src = [s for s in old_src if s not in new_src]
    if missing_src:
        raise GuardError(
            f"invariant 1 (sources append-only): write drops sources entries "
            f"{missing_src}; removal needs the explicit remove-source-entry command"
        )

    # Invariant 4 (both modes): identity immutable on a common write.
    if old.frontmatter.get("type") and new.frontmatter.get("type") != old.frontmatter.get("type"):
        raise GuardError(
            f"invariant 4 (identity immutable): type changed from "
            f"{old.frontmatter.get('type')!r} to {new.frontmatter.get('type')!r}; "
            f"use the move-page command to change identity"
        )
    if old.frontmatter.get("id") and new.frontmatter.get("id") != old.frontmatter.get("id"):
        raise GuardError(
            f"invariant 4 (identity immutable): id changed from "
            f"{old.frontmatter.get('id')!r} to {new.frontmatter.get('id')!r}; "
            f"use the move-page command to move a page"
        )

    if mode is Mode.INGESTION:
        _check_ingestion(old, new, max_shrink)
    _check_citations(old, new)
    _preserve_source_details(old, new)


def _preserve_source_details(old: Page, new: Page) -> None:
    """Restore omitted citation fields; changing recorded values needs a curator."""
    previous = {
        str(entry["id"]): entry
        for entry in old.frontmatter.get("sources", []) or []
        if isinstance(entry, dict) and "id" in entry
    }
    merged = []
    for entry in new.frontmatter.get("sources", []) or []:
        if not isinstance(entry, dict) or "id" not in entry:
            merged.append(entry)
            continue
        recorded = previous.get(str(entry["id"]), {})
        changed = [key for key in recorded if key in entry and entry[key] != recorded[key]]
        if changed:
            raise GuardError(
                f"invariant 1 (sources append-only): entry {entry['id']!r} changes "
                f"recorded fields {changed}; keep the recorded values or use the "
                "explicit remove-source-entry command before correcting the citation"
            )
        merged.append({**recorded, **entry})
    if "sources" in new.frontmatter:
        new.frontmatter["sources"] = merged


def _check_ingestion(old: Page, new: Page, max_shrink: float) -> None:
    # Invariant 2: headers don't disappear.
    old_headers = _headers(old.body)
    new_headers = set(_headers(new.body))
    lost_headers = [h for h in old_headers if h not in new_headers]
    if lost_headers:
        raise GuardError(
            f"invariant 2 (headers preserved): these section headers were "
            f"present before and are gone: {lost_headers}"
        )

    # Invariant 6: outgoing links are append-only.
    old_links = _links(old.body)
    new_links = _links(new.body)
    lost_links = sorted(old_links - new_links)
    if lost_links:
        raise GuardError(
            f"invariant 6 (outgoing links append-only): these links were "
            f"present before and are gone: {lost_links}"
        )

    # Invariant 5: shrinkage beyond the threshold is refused.
    old_len = len(old.body or "")
    new_len = len(new.body or "")
    if old_len > 0:
        dropped = (old_len - new_len) / old_len
        if dropped > max_shrink:
            raise GuardError(
                f"invariant 5 (no over-shrinking): body shrank by "
                f"{dropped:.0%} (from {old_len} to {new_len} chars), "
                f"more than the {max_shrink:.0%} limit"
            )


def _check_citations(old: Page, new: Page) -> None:
    # The single looser invariant: every sources entry cited before must still
    # be cited by some footnote after. Freeing merge/shrink/prune of links.
    old_cited = _cited_source_ids(old)
    new_cited = _cited_source_ids(new)
    lost_citations = sorted(old_cited - new_cited)
    if lost_citations:
        raise GuardError(
            f"ingestion/consolidation invariant (citations preserved): these sources "
            f"entries were cited before and are no longer cited by any "
            f"footnote: {lost_citations}; keep a body citation for each entry"
        )
