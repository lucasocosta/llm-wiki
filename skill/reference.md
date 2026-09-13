# llm-wiki command reference (read side)

This is the reference the skill points at. It is one level deep from the skill
and points nowhere further.

## search

```sh
llm-wiki search "QUERY" [--type TYPE] [--tag TAG ...] [--snippet] [--limit N]
```

Ranks pages lexically over frontmatter and body (title, description and tags
weigh more) and prints a JSON array of winners. Each result is
`{"id", "title", "type", "description"}`, plus `"snippet"` when `--snippet` is
given. The body is never included.

- `--type` filters by page type (`Topic` for a concept page, `Reference` for a
  Source mirror).
- `--tag` filters by tag; repeat it to require several tags.
- `--limit` caps the number of results (default 10).

## read-page

```sh
llm-wiki read-page CONCEPT_ID
```

Prints `{"id", "frontmatter", "body", "stale"}`. `stale` is `null` when the page
has no verifiable provenance; otherwise `{"stale": bool, "changed": [...]}`.

## graph

```sh
llm-wiki graph backlinks CONCEPT_ID   # who links to a page
llm-wiki graph orphans                # pages nothing links to
llm-wiki graph broken-links           # links to missing pages
llm-wiki graph lint                   # long-page warnings + pending draft pages
```

`lint` returns `{"long_pages": [...], "draft_pages": [...]}`. A draft page
(frontmatter `draft: true`) may contain links to missing pages; while the flag
stands the write accepts them, and `draft_pages` is the curation to-do.

## Notes

- No LLM API key is required for any command; ranking happens on-device.
- The machine index lives under `.llmwiki/` and is rebuilt when pages change.

## ingest report extras

- Code Sources also report `excluded_unreadable`: files matched by the allowlist
  but not UTF-8-decodable (e.g. compiled artifacts under `__pycache__` — cache
  directories are never ingested) (ticket 07).
- `usage` summarizes characters served per command over time (from
  `.llmwiki/usage.jsonl`), so the cost model is measurable (ticket 05).

## write-page multiple Trechos

`--trecho-hash` is repeatable: one call may stamp several Trecho hashes on the
same page (thematic consolidation). All hashes must still be present in the
Source; like every stamped field, `trechos` is append-only (ticket 03).
