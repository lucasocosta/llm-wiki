# 03: Preservar os detalhes das entradas de proveniência

Type: task
Status: resolved
Priority: P1

## Problema

A guarda compara apenas ids de sources. Uma escrita com o mesmo id pode apagar Âncora, URI e outros dados da citação.

## Reprodução

Ingerir sources com id, anchor e uri; reescrever mantendo apenas id e a citação no corpo.

## Critérios de aceitação

- [x] Campos omitidos de uma entrada existente são preservados por id na ingestão e na consolidação.
- [x] Alterar valores existentes é recusado com instrução; acrescentar campos e novas entradas continua permitido.
- [x] Regressões pela CLI verificam o estado em disco e a recusa sem perda de dados.

## Comments

- 2026-09-13 — Criado a partir da revisão dos commits 4eb32c1 e 89ebb36 e das alterações locais. Correção autorizada pelo usuário e iniciada.

- 2026-09-13 — Resolvido. A guarda mescla os detalhes de sources pelo id, recuperando campos omitidos e permitindo campos adicionais. Valores existentes divergentes são recusados com indicação do campo e do comando de curadoria. As regressões verificam ingestão e consolidação, preservação de Âncora/URI/metadados e Bundle inalterado após recusa.

Validação: 58 testes dirigidos passaram; suíte completa com 136 testes passando via `.venv/bin/python -m pytest --tb=short`. Regressões funcionais em `tests/test_25_review_regressions.py`; testes ajustados em `tests/test_02_tracer_bullet.py` e `tests/test_23_tickets_avaliacao.py`.
