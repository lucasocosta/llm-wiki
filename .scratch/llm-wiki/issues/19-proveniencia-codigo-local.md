# 19: Registrar e consultar proveniência de código local por arquivo

**Status:** done
**Priority:** P1
**Blocked by:** None (can start immediately).
**Related:** [08 — Fontes de código](08-fontes-codigo.md), [10 — obsolescência](10-obsolescencia.md), [17 — versão por página](17-versao-fonte-por-pagina.md).

## Problema

Review de `75597d6...4eb32c1`: `stamp_write`, em `src/llmwiki/ingestion.py`, grava apenas `source.commit`, opcional para código local. O Espelho fica sem SHA e com hash vazio. Em `src/llmwiki/staleness.py`, a consulta cai no caminho de texto e tenta ler o diretório da Fonte, causando `IsADirectoryError`.

O ticket 08 exige “O Espelho de Fonte guarda o commit SHA do arquivo lido”; o ticket 10 exige detectar mudança no commit daquele arquivo e avisar quem lê.

## Reprodução pela CLI

1. Em diretório temporário, criar um repositório Git com `sources/proj/mod.py`, conteúdo legível e um commit real.
2. Declarar Fonte `code`, `location: proj`, `allowlist: ['.']`, sem `commit` no manifesto.
3. Obter o item por `ingest next` e gravar a página `code` por `ingest write-page`.
4. Executar `read-page code` e `stale report`.

Atual: a ingestão aceita a escrita, mas a consulta tenta ler `sources/proj` como texto. Esperado: consulta válida com proveniência do arquivo e seu SHA real.

## Critérios de aceitação

- [x] A proveniência identifica os arquivos efetivamente lidos e suas revisões reais, sem exigir um SHA manual para a Fonte local inteira.
- [x] O Espelho e o registro de derivação por Página Conceitual conservam essa rastreabilidade, inclusive para Fonte com vários arquivos.
- [x] `read-page` e `stale report` funcionam após ingerir código local, sem ler diretório como texto.
- [x] Um novo commit que altera o arquivo contribuinte torna a página obsoleta e produz aviso na leitura.
- [x] Um commit que altera somente outro arquivo não invalida indevidamente a página.
- [x] Quando não for possível verificar uma revisão do conteúdo lido, a CLI não inventa um SHA nem declara a página atual sem evidência; informa a limitação de forma explícita.
- [x] Regressões usam repositório Git temporário com commits reais e chamadas da CLI, verificando disco e stdout, sem simular SHAs apenas trocando o manifesto.

## Comments

- 2026-09-12 — Em andamento. Proveniência verificável por arquivo e regressões com commits Git reais.

- 2026-09-12 — Concluído. 22 testes relacionados passaram. SHA real por arquivo; commits em outro arquivo não invalidam a página; código sem revisão verificável é relatado explicitamente sem erro de diretório.
