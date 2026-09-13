---
id: wiki-proveniencia-staleness
type: Topic
title: Proveniência, staleness e guard
description: Provenância via Git sem tocar no checkout, relatório de obsolescência,
  páginas sujas e o guard de escrita.
tags:
- proveniencia
- staleness
- git
- guard
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 71b83f8feafef8c86a1562e4b079914f15cebd02548893cf3d4af3cb7f085800
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      provenance.py:
        content_hash: 71b83f8feafef8c86a1562e4b079914f15cebd02548893cf3d4af3cb7f085800
        commit: 89ebb36ce1ce40c931ef7401714aea9c6a853dc2
---


## Proveniência (`provenance.py`)

Todas as chamadas a `git` passam por `git_output` (retorna `None` quando o comando falha —
leitura de estado, nunca mutação). Para arquivos de código, `code_file_version` atribui um
commit **só quando os bytes lidos são idênticos ao conteúdo comitado** em HEAD
(`git show HEAD:path`); caso contrário a versão fica explicitamente `unverifiable`
("untracked, modified, or outside Git") — a CLI não inventa SHA.

## Obsolescência (`staleness.py`, `commands/stale.py`)

`staleness_report` compara a versão de derivação gravada em cada página (hash de conteúdo,
ou por-arquivo `files` para código) contra o estado atual da Fonte: `stale: bool` +
lista de arquivos/campo `changed`; `stale: null` quando a proveniência não é verificável.
Páginas antigas sem versão de derivação são explicitamente não-verificáveis até reingestão.

## Página Suja e guard (`dirty.py`, `guard.py`)

`is_dirty` marca páginas escritas por mais de uma Fonte de contribuição — alvo do
`consolidate` (reconciliar em uma voz só). O **augmentation guard** (`guard.py`, `Mode`)
recusa writes destrutivos na reescrita: invariantes observadas no teste de monografia
incluem headers preserved e outgoing links append-only.
