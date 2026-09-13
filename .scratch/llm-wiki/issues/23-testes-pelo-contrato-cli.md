# 23: Adequar os testes ao contrato da CLI

**Status:** done
**Priority:** P2
**Blocked by:** None (can start immediately).
**Related:** [01 — fundação](01-fundacao-okf.md), [10 — obsolescência](10-obsolescencia.md), [14 — log](14-log-historico.md), [15 — skill](15-skill-e-distribuicao.md), [spec — Testing Decisions](../spec.md#testing-decisions).

## Problema

Review Standards de `75597d6...4eb32c1`: a spec exige “Um único seam: o contrato da CLI” e declara que a skill fica “sem teste automatizado”, por ser prosa que governa julgamento do modelo.

- `tests/test_01_okf_foundation.py` afirma diretamente sobre `render_page`, `parse_page` e geração de índices.
- `tests/test_10_staleness.py` acrescenta `source_ids` apenas em memória e chama `staleness_report`, validando um estado diferente do que a CLI persistiu.
- `tests/test_14_log.py` testa ordenação chamando `append_log` diretamente.
- `tests/test_15_skill_distribution.py` exige redação específica, como `"use when"`, sem verificar comportamento observável da ferramenta.

A suíte atual passa com 84 testes, mas isso não comprova os comportamentos ausentes nas issues funcionais 16–22. Esta issue não deve fazer testes passarem fabricando estados internos que a CLI não produz.

## Reprodução / evidência

1. Executar `.venv/bin/python -m pytest`: a revisão observou 84 testes passando.
2. Inspecionar os testes acima e identificar as chamadas internas sob teste e os asserts sobre redação.
3. Comparar o teste de obsolescência com `read-page`/`stale report` sobre o estado realmente gravado pela ingestão: o metadado acrescentado somente em memória não faz parte dessa reprodução.

## Critérios de aceitação

- [x] As afirmações sobre comportamento invocam o entry point por `argv` e verificam disco, stdout e código de saída; testes por subprocess continuam garantindo a ligação do binário.
- [x] Ordenação de frontmatter, validação, índices e histórico são exercitados por operações públicas da CLI, sem criar novas opções somente para testes.
- [x] Testes de proveniência partem do que a CLI persistiu, sem completar o objeto em memória antes de consultar uma função interna.
- [x] Helpers podem preparar fixtures; isso não cria um segundo seam para afirmar diretamente sobre implementações internas.
- [x] Remover asserts que fixam palavras ou pretendem validar julgamento induzido pela skill. Preservar verificações técnicas necessárias de distribuição/arquivos, sem fingir que comprovam a prosa.
- [x] Cada bug funcional mantém sua regressão na issue correspondente; esta adequação não enfraquece nem remove cobertura para esconder falhas.
- [x] A suíte completa passa após as correções necessárias; dependências descobertas são vinculadas, não contornadas com mocks de lógica interna.

## Comments

- 2026-09-12 — Em andamento. Migrar afirmações internas para o contrato público, preservar cobertura e remover asserts de palavras da skill.

- 2026-09-12 — Concluído. Suíte: 108 testes passando. `test_page_without_type_is_rejected_on_read` removida: a recusa de frontmatter sem `type` é contrato de escrita (spec §28, `ingest write-page` recusa com exit 2) e já coberta por `test_page_without_type_is_rejected_on_write`; `read-page` é leniente por design porque staleness, grafo e busca precisam ler páginas em disco. `test_newest_date_first` agora ingere de uma segunda Fonte na segunda passada — a primeira versão reingestava da mesma Fonte, mas a fila já estava vazia por retomada e `ingest next` devolvia `work_item: null`.
