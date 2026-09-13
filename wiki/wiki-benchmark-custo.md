---
id: wiki-benchmark-custo
type: Topic
title: Benchmark de custo por caminho
description: Medição de chars servidos por caminho — search ~920, read-page ~2,8k,
  dump do Bundle ~61,5k.
tags:
- benchmark
- custo
- uso
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 6e3e873c91de910161a470209430d6af177dfd9b7b02312d3b669470aefc29ff
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
---


A medição completa está em `.scratch/avaliacao-teste-llm-wiki/benchmark.md`.
Resumo: consulta típica custa 1–3% de um dump do Bundle; o laço
usage.jsonl (usage.py) é o lado da ferramenta da conta.
