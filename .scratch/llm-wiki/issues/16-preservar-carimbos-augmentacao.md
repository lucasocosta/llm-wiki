# 16: Preservar os carimbos de contribuição na augmentação

**Status:** done
**Priority:** P1
**Blocked by:** None (can start immediately).
**Related:** [05 — retomada](05-fila-computada-retomada.md), [11 — Página Suja](11-pagina-suja-consolidacao.md), [spec — contrato do trabalhador](../spec.md#contrato-do-trabalhador).

## Problema

Review de `75597d6...4eb32c1`: `src/llmwiki/ingestion.py`, em `stamp_write`, parte dos metadados do rascunho recebido, sem mesclar os carimbos persistidos. Uma augmentação pode apagar o hash do Trecho anterior e seus ids de Fonte. A fila volta a oferecer trabalho concluído e a Página Conceitual pode parecer limpa.

A spec exige: “A tool carimba a contribuição, não o trabalhador” e retomada “sem reprocessar o que já foi feito”.

## Reprodução pela CLI

1. Criar Bundle temporário com uma Fonte Markdown contendo duas seções distintas.
2. Obter o primeiro item com `ingest next` e gravar a página `example` com `ingest write-page --page-id example --source-id <source_id> --trecho-hash <trecho_hash> --content-file <rascunho>`.
3. Obter o segundo item e augmentar a mesma página, preservando corpo, cabeçalhos e `sources`, mas omitindo os campos automáticos `trechos`, `source_ids` e `consolidated_trechos` no rascunho.
4. Consultar `ingest queue`, `read-page example` e `consolidate list`.

Atual: o primeiro Trecho volta à fila; `trechos` contém apenas o segundo hash; `example` não aparece como Página Suja. Esperado: fila vazia, ambos os carimbos preservados e página suja.

## Critérios de aceitação

- [x] A tool mescla os carimbos persistidos com a contribuição atual, mesmo que o rascunho omita ou forneça listas incompletas dos metadados automáticos.
- [x] A reprodução acima termina com fila vazia e ambos os hashes visíveis em disco/`read-page`.
- [x] Contribuições de duas Fontes preservam ambos os ids de Fonte e seus registros de derivação.
- [x] Página nunca consolidada e tocada por dois Trechos aparece em `consolidate list`.
- [x] Após consolidar e augmentar por outro Trecho, o registro da última consolidação é preservado e a página volta a aparecer como suja.
- [x] Repetir uma escrita não duplica carimbos; copiar o Bundle sem cache mantém a mesma fila e a mesma sujeira.
- [x] Regressões exercitam o contrato da CLI por `argv`, verificando disco e stdout, sem chamar os cálculos internos diretamente.

## Comments

- 2026-09-12 — Em andamento. Regressão pela CLI para preservar contribuições entre augmentações e consolidação.

- 2026-09-12 — Concluído. 12 testes focados passaram; augmentação preserva carimbos, Fontes e a última consolidação, inclusive em rascunhos incompletos e retomada sem cache. Verificação ampliada com issue 17: 20 testes passaram.
