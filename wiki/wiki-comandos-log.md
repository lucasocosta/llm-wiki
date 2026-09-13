---
id: wiki-comandos-log
type: Topic
title: Comandos CLI e log.md
description: Comandos de ingestão, consulta e curadoria, e o log append-only legível
  por humanos.
tags:
- comandos
- cli
- log
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 38e6f30a2e4f9aee0d315580a8f6ea73a48c8dd6aa53fcd0144bf740fb6b63a8
- 38290d29c5dff64680f89c32bd43c6aa6361c9d0d9e081bfb9e60b8288c6942e
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      commands/ingest.py:
        content_hash: 38290d29c5dff64680f89c32bd43c6aa6361c9d0d9e081bfb9e60b8288c6942e
        unverifiable: content has no matching committed revision (untracked, modified,
          or outside Git)
---



Um `register(cmds>` por arquivo em `commands/`; cada comando uma função pura de args:

- **`ingest next` / `queue` / `report` / `write-page`** (`commands/ingest.py`):
  `next` entrega o próximo item de trabalho (Trecho + shortlist), `queue` o balanço
  completo, `report` as Fontes com contagens de arquivos incluídos/excluídos,
  `write-page` grava com validação e stamping de proveniência.
- **`read-page` / `search`** (`commands/query.py`).
- **`sources`** (`commands/sources.py`): caminho de curador para remover Fonte e
  reescrever links entre páginas quando o Espelho termina.
- **`stale report`** (`commands/stale.py`), **`graph`** (`commands/graph.py`),
  **`consolidate list`/run** (`commands/consolidate.py`) e **`regenerate-index`**
  (`commands/index_cmd.py`).

## log.md (`log.py`)

História **humano-apendível e append-only** (`## <data>` por dia) escrita pela própria
ferramenta a cada gravação: auditoria manual dos eventos de ingestão — nunca um fluxo
de máquina para o assistente (o registro de machine-ist boato fica em `.llmwiki/`).
