---
id: wiki-codigo-visao-geral
type: Topic
title: 'llm-wiki: visão geral do código'
description: 'Arquitetura geral: CLI como único test seam, motor determinístico sem
  LLM, Trecho como unidade de entrega.'
tags:
- codigo
- arquitetura
- cli
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- d2b9854ea6b7bc3b2781e7578a283d3596aad1091da4673807e24e78e4ed8640
source_ids:
- llmwiki-src
source_versions:
  llmwiki-src:
    type: code
    path: src/llmwiki
    files:
      __init__.py:
        content_hash: d2b9854ea6b7bc3b2781e7578a283d3596aad1091da4673807e24e78e4ed8640
        commit: 4eb32c16354ab70d500d09943fb08f4130e86b4a
---


O `llm-wiki` é um console script (`src/llmwiki/cli.py`) que constrói um Bundle de
Markdown em OKF estendido a partir de Fontes declaradas no `llm-wiki.yml` e consulta o
Bundle por busca lexical, sem chamar LLM (ADR 0002).

## Decisões arquiteturais congeladas

- **A CLI é o único test seam**: os testes invocam `run(argv, cwd)` e verificam retorno
  (`CliResult`: exit code + stdout/stderr capturados) e arquivos em disco; alguns exercitam
  também o binário via subprocesso. Todo comando é uma função `cmd_<nome>(args, root)`
  registrada por um `register()`.
- **O motor nunca chama LLM**: a CLI extrai e entrega Trechos; a redação das páginas é do
  worker, devolvida e validada por `ingest write-page` (o único caminho de gravação com
  stamping de proveniência).
- **O Trecho** (`trecho.py`) é a menor unidade de entrega de uma Fonte: texto,
  `trecho_hash` (SHA-256 do texto), `anchor` e `source_path` (rastreabilidade por arquivo
  para código). Trechos acima do teto `max_trecho_chars` são subdivididos cortando em
  fronteiras naturais e preservando a Âncora e a rastreabilidade; com as mesmas Fontes e
  configuração, os Trechos e hashes são determinísticos em outra máquina.

Erros de domínio são `CommandError` (`commands/__init__.py`), resolvidos em `SystemExit`
sem stack interna.
