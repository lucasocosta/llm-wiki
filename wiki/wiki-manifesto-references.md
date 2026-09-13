---
id: wiki-manifesto-references
type: Topic
title: Manifesto e Espelho de Fonte
description: Um manifesto YAML na raiz declara Bundle e Fontes; cada Fonte tem um
  Espelho em references/ com a versão que foi lida.
tags:
- manifesto
- fontes
- reference
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- bd967ec8c289371e724135c1018fbb455081bf83c0a93a497f49cf6063d2063c
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      manifest.py:
        content_hash: bd967ec8c289371e724135c1018fbb455081bf83c0a93a497f49cf6063d2063c
        commit: 89ebb36ce1ce40c931ef7401714aea9c6a853dc2
---


## Manifesto (`manifest.py`)

Único arquivo YAML na raiz: `bundle_dir`, `sources_dir`, `language`, `max_trecho_chars`
(padrão 12000) e a lista de Fontes. Cada Fonte: `id`, `type` (`text`/`pdf`/`markdown`/`code`),
`location` e `language` original. Fontes `code` adicionam `allowlist` (padrões tipo
glob/dir; um padrão `.` é tudo) e, para código externo, `repository` + `commit` fixados
por SHA — a CLI exige que o checkout esteja naquele commite e nunca copia o código para
o repositório da wiki. Violações de estrutura levantam `ManifestError` (chaves obrigatórias:
id, tipo, location).

## Espelho de Fonte (`reference.py`)

Página de tipo `Reference` em `references/` (garantida por `ensure_reference`) registrando
por Fonte o `content_hash` (SHA-256 dos bytes) e, para código, a versão por arquivo
(SHA do commit). Atualizar o Espelho de uma Fonte **não** atualiza a proveniência de
páginas existentes: só `write-page` carimba a derivação nova.

`CommandError` centraliza desvios de operação dos comandos registrados em
`commands/__init__.py`.
