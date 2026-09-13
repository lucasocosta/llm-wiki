---
id: wiki-grafo-lint
type: Topic
title: Grafo de links e lint
description: Backlinks, orphans, broken-links e lint — propriedades computáveis do
  grafo, sem LLM.
tags:
- grafo
- lint
- links
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 877de3ef350cde949ec642f4186451e790360ca4fc90ecc65caebbedad943bf8
- ee951fe4fb8b70f9fa4fb037e682c921610884d1641b23f056724c25158cc7a3
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      graph.py:
        content_hash: ee951fe4fb8b70f9fa4fb037e682c921610884d1641b23f056724c25158cc7a3
        unverifiable: content has no matching committed revision (untracked, modified,
          or outside Git)
---



O grafo de links do Bundle é um instrumento de curadoria computável:

- **edges-out / backlinks**: cada link no body é resolvido por `resolve_link`;
  `graph backlinks id` lista quem aponta para a página;
- **orphans**: páginas que nada endossa à;
- **broken-links**: links que resolvem para id sem página — checkable na escrita
  (guard) ou depois;
- **lint**: páginas longas e headers de estrutura (avisos, não erros).

`commands/graph.py` registra os comandos; `commands/index_cmd.py` registra
`regenerate-index` (regenerar todos os `index.md` a partir do frontmatter).
Todas as propriedades são derivadas do estado no disco, determinísticas e testáveis
por asserts — coerente com a postura de ADR 0002 (julgamento de prosa nunca simulado
por teste).
