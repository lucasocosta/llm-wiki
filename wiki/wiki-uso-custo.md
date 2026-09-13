---
id: wiki-uso-custo
type: Topic
title: Uso e dados de custo
description: Instrumentação de payload (usage.py) e a conta de chars/tokens por caminho.
tags:
- uso
- custo
- custo-benchmark
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 6e3e873c91de910161a470209430d6af177dfd9b7b02312d3b669470aefc29ff
- c08689d6645cad0e169f61ef9993c0804e2b37abed73de49ea15d54241755a18
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      usage.py:
        content_hash: 6e3e873c91de910161a470209430d6af177dfd9b7b02312d3b669470aefc29ff
        unverifiable: content has no matching committed revision (untracked, modified,
          or outside Git)
      log.py:
        content_hash: c08689d6645cad0e169f61ef9993c0804e2b37abed73de49ea15d54241755a18
        commit: 4eb32c16354ab70d500d09943fb08f4130e86b4a
---





A ferramenta mede o próprio payload (ticket 05): cada comando com carga
(search, read-page, next, queue) acrescenta uma linha JSONL em
`.llmwiki/usage.jsonl` (módulo `usage.py`); `ingest report` resume por
comando. Detalhes em [benchmark de custo](wiki-benchmark-custo.md).
