---
id: wiki-okf-paginas
type: Topic
title: Páginas OKF e index.md
description: Leitura/escrita de páginas com frontmatter, invariantes de contribuição
  e geração determinística de índices.
tags:
- okf
- paginas
- index
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- f79be9ddc5b8f1bbcbcb933df298b30e25111989a479ca26ffd32340407fcefd
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      okf/__init__.py:
        content_hash: f79be9ddc5b8f1bbcbcb933df298b30e25111989a479ca26ffd32340407fcefd
        commit: 4eb32c16354ab70d500d09943fb08f4130e86b4a
---


## Página (`okf/page.py`)

Leitura e escrita de pagina Markdown com frontmatter YAML (OKF, `okf_version` '0.2').
Regras: página exige `id` e `type` (ex. `Topic`/`Reference`) — sem `type`, a escrita é
recusada ("identity (type) is the caller's responsibility", spec §28). `write_worker_page`
só adiciona — nunca apaga — contribuições automáticas: se o rascunho omitir
`generated`/`generated_by`/`trechos`/`source_versions`, os carimbos anteriores são
preservados (`preserve_contributions`). Erros de página levantam `PageError`.

## Índices (`okf/index.py`)

Geração determinística (sem LLM) de `index.md` por diretório do Bundle, a partir do
frontmatter das páginas entradas; `IndexItem` compõe cada entrada do índice. O comando
`regenerate-index` reconstrói todos os índices após mudanças de página — a página `index`
é um artefato derivado, nunca editado à mão.
