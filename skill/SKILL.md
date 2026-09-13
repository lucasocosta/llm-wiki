---
name: llm-wiki-search
description: Search a local llm-wiki knowledge base cheaply before answering. Use when the user asks a question that a curated wiki in this repository might answer, when a repository contains an llm-wiki.yml manifest, or when the user mentions the wiki, the knowledge base, or asks "what do we know about X". Ranks off-model and returns metadata first so the index never enters context.
---

# Searching an llm-wiki

An **llm-wiki** is a local Markdown knowledge base (a *Bundle*) built from
declared *Sources*. A repository has one when an `llm-wiki.yml` manifest sits at
its root. The `llm-wiki` command-line tool ranks pages off-model and returns
only the winning metadata, so the whole index never enters the assistant's
context. It needs no LLM API key and runs anywhere a shell runs.

## When this applies

Reach for the wiki when a question could be answered by curated knowledge in the
repository — background on a concept, why some code exists, what a PDF or a note
says — rather than by reading source files directly. Trigger terms include "the
wiki", "the knowledge base", "what do we know about", "look it up", and any
topic the Sources plausibly cover.

## How to search

Call the tool through the shell. It prints JSON.

1. Search for candidates. The default payload is `id`, `title`, `type`, and
   `description` — never the body, so this stays cheap:

   ```sh
   llm-wiki search "your query here"
   ```

   Narrow with `--type Topic` or `--type Reference`, and with `--tag NAME`
   (repeatable). Add `--snippet` only when a factual question might be answered
   by the matched excerpt alone, so most searches don't pay for it.

2. Read the winners you actually need, whole:

   ```sh
   llm-wiki read-page CONCEPT_ID
   ```

   The result includes the page's frontmatter, its body, and a `stale` field.
   When `stale` reports the page's Source changed after the page was written,
   qualify the answer instead of stating it with confidence.

3. Follow the graph rather than re-searching:

   ```sh
   llm-wiki graph backlinks CONCEPT_ID
   ```

## Rules

- Prefer `search` then `read-page` over reading wiki files directly: the point
  is to spend few tokens finding the right page.
- Never dump the whole wiki or the machine index into context.
- Search is lexical: use words that appear in the material, not paraphrases.

## Evidence protocol (ask the wiki like a curator, not a retriever)

Search is lexical, so a paraphrase can slide the ranking to adjacent pages and
an answer built on the wrong page comes out confidently wrong (the RAG failure
mode). Guard against it by procedure:

1. **Cite the evidence**: every factual answer names the pages read
   (`read-page ids`); no page — no claim.
2. **Empty result is an answer**: an empty `search` result (or results that
   only partially match) means *the wiki does not answer this*. Say so, list
   the terms tried, and suggest a term from the material instead of
   answering from prior knowledge. `search --suggest` lists real vocabulary
   terms from the index to redirect the query.
3. **Read whole winners, several of them**, before committing to an answer
   (never answer from metadata or a snippet alone).
4. **Qualify, never assert**, when a page reports `stale` values or
   unverifiable provenance.

For the full command surface, see [reference.md](reference.md).

## Construction notes (from the 2026-09 evaluation)

- Extract Trechos only through `ingest next`. Calling the engine's internal
  extractor to read many Trechos at once bypasses the per-Trecho budget and is
  an anti-pattern (ticket 01).
- A page may derive from several Trechos: repeat `--trecho-hash` to consolidate
  thematically in one page (ticket 03). Provenance accumulates.
- A page written with frontmatter `draft: true` may reference pages that do not
  exist yet; drop the flag (writing the finished content revalidates links).
  `graph lint` lists pending drafts (ticket 02).
