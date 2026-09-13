---
id: wiki-extracao-codigo
type: Topic
title: Extração de Trechos e ingestão de código
description: 'Como o motor transforma Fontes em Trechos: markdown/texto por seções,
  código por módulos com ordem leaves-first e âncora de símbolo qualificado.'
tags:
- trechos
- codigo
- extracao
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 2626a939d94287e48f0efd245158e860891c17bd26f5c24b39a8b1f5f950ef39
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      extract.py:
        content_hash: 2626a939d94287e48f0efd245158e860891c17bd26f5c24b39a8b1f5f950ef39
        commit: 4eb32c16354ab70d500d09943fb08f4130e86b4a
---


## Extração (`extract.py` / `code.py`)

Cada Fonte vira Trechos por fronteiras naturais; unidades acima do teto são subdivididas.
Markdown/texto: seções e limites de texto; PDF: por página. Código é lido **como material
de leitura** — o wiki captura o *porquê* e as decisões congeladas, não assinaturas de API
que envelhecem a cada commit:

- `scan_code_source` aplica a `allowlist` (fnmatch/prefixo de diretório) e separa
  `included` de `excluded_count`; exclusões aparecem no `ingest report` para não
  passarem despercebidas;
- `order_leaves_first` ordena os arquivos folhas-primeiro sobre o grafo de imports
  intra-Fonte (ciclos quebrados tomando o arquivo restante de menor caminho);
- a Âncora do Trecho de código é o **símbolo qualificado** (`symbol:X`) ou o arquivo
  (`file:a.py`), nunca número de linha — a referência sobrevive a mover arquivos e reindentar.

## Motor de ingestion (`ingestion.py`)

Coordena extração por tipo, fila determinística de Trechos sem página, e o único caminho
de gravação com stamping (`write_worker_page`: `generated`, `generated_by`, `trechos`,
`source_ids`, `source_versions`; e `ensure_reference` do Espelho). Para código, valida na
entrega e na escrita que o Trecho pedido ainda existe e que o checkout externo não
diverge do SHA declarado (`validate_code_pin`); diligencia `IngestionError` em qualquer
falha. Falha observada em teste: `allowlist` que deixa entrar arquivo binário (`.pyc`)
propagou `UnicodeDecodeError` crudo de `order_leaves_first` — a extração de código
assumiría UTF-8 ou retornaria erro de domínio.
