# 06: Verificar o manifesto pelo contrato da CLI

Type: task
Status: resolved
Priority: P3

## Problema

O teste do manifesto chama load_manifest diretamente e afirma sobre atributos internos, contrariando Testing Decisions e a issue 23.

## Reprodução

Inspecionar test_manifest_declares_bundle_sources_language_and_a_markdown_source em test_02_tracer_bullet.py.

## Critérios de aceitação

- [x] Exercitar diretórios personalizados, língua e Fonte declarada por comandos públicos.
- [x] Verificar payloads e arquivos produzidos, sem chamar load_manifest como operação sob teste.
- [x] Manter a cobertura do comportamento do manifesto e executar a suíte completa.

## Comments

- 2026-09-13 — Criado a partir da revisão dos commits 4eb32c1 e 89ebb36 e das alterações locais. Correção autorizada pelo usuário e iniciada.

- 2026-09-13 — Resolvido. O teste do manifesto usa diretórios personalizados (knowledge/pages e reading), língua fr, ingest next, write-page e read-page. Confere o caminho real da página, a língua do índice raiz e o caminho da Fonte no Espelho, sem chamar load_manifest como operação sob teste.

Validação: 58 testes dirigidos passaram; suíte completa com 136 testes passando via `.venv/bin/python -m pytest --tb=short`. Regressões funcionais em `tests/test_25_review_regressions.py`; testes ajustados em `tests/test_02_tracer_bullet.py` e `tests/test_23_tickets_avaliacao.py`.
