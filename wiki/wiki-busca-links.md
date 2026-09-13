---
id: wiki-busca-links
type: Topic
title: Busca lexical, shortlist e resolução de links
description: Ranking off-model que nunca devolve corpo, shortlist no work item e resolução
  de links relativos aplicando as regras do ADR 0001.
tags:
- busca
- search
- links
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- d0e798cfab3c70da66336e71ceef63de1acc24f1aa4eccfc0bc3636a2f91bec5
- 16464711c77027eea9faf0955484ad3d0a0a59b936a244e8a98dd503fb846ecb
source_ids:
- llmwiki-src
aliases:
- pesquisa
- pesquisa lexical
- procura
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      search.py:
        content_hash: 16464711c77027eea9faf0955484ad3d0a0a59b936a244e8a98dd503fb846ecb
        unverifiable: content has no matching committed revision (untracked, modified,
          or outside Git)
---



## Busca (`search.py`)

Ranking lexical sobre o índice de máquina (`_tokenize` em palavras Unicode), com peso
maior para título, descrição e tags. O resultado é `{"id","title","type","description"}` —
o corpo **nunca** é incluído; `--snippet` é opcional, pago a mais quando a pergunta fática
pode ser respondida pelo trecho casado (page snippet do body curtido) sem abrir a página.

## Shortlist (`shortlist.py`)

`build_shortlist` ranqueia conceitos candidatos a esperar o Trecho: mesmo mecanismo de
peso lexical da busca, servido dentro de `ingest next` para orientar o worker sem
derramar o índice inteiro no contexto.

## Links (`links.py`)

`resolve_link(page_id, target)`: externos (`http/https/mailto`), âncoras puras (`#`) e
alvos sem `.md` não são conceito (retornam `None`); alvo iniciado por `/` está proibido
(ADR 0001 — nulo também ainda). Alvo relativo é normalizado com `posixpath.normpath`
sobre o `dirname(page_id)` e converte `x.md` → id `x`.
