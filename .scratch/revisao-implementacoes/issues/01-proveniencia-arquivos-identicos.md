# 01: Preservar proveniência de arquivos de código idênticos

Type: task
Status: resolved
Priority: P1

## Problema

O mapa por hash em stamp_write conserva só o último arquivo de código com o mesmo conteúdo. A fila considera ambos concluídos; modificar o arquivo omitido não marca a Página Conceitual como obsoleta.

## Reprodução

Ingerir a.py e b.py idênticos e commitados; gravar o item entregue; modificar e commitar a.py; consultar read-page.

## Critérios de aceitação

- [x] Registrar todos os arquivos correspondentes aos hashes entregues, sem incluir arquivos de conteúdo diferente.
- [x] A leitura e o relatório detectam alterações em qualquer arquivo correspondente.
- [x] Regressão pela CLI com repositório Git temporário e commits reais.

## Comments

- 2026-09-13 — Criado a partir da revisão dos commits 4eb32c1 e 89ebb36 e das alterações locais. Correção autorizada pelo usuário e iniciada.

- 2026-09-13 — Resolvido. stamp_write conserva todos os Trechos correspondentes aos hashes entregues, sem colapsar arquivos idênticos num único valor. A regressão test_identical_code_files_keep_all_derivation_versions cobre a.py e b.py separadamente, com commits reais, e confirma os avisos em read-page e stale report.

Validação: 58 testes dirigidos passaram; suíte completa com 136 testes passando via `.venv/bin/python -m pytest --tb=short`. Regressões funcionais em `tests/test_25_review_regressions.py`; testes ajustados em `tests/test_02_tracer_bullet.py` e `tests/test_23_tickets_avaliacao.py`.
