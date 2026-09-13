# 05: Tornar efetivo o teste de exclusão de __pycache__

Type: task
Status: resolved
Priority: P2

## Problema

O teste consulta file_path, que não faz parte da saída de ingest queue; todos os valores são None e o assert passa mesmo sem a exclusão.

## Reprodução

Remover a exclusão em uma cópia temporária e executar o teste atual: permanece verde.

## Critérios de aceitação

- [x] Verificar quantidade de Trechos, conteúdo entregue e conclusão da fila pela CLI.
- [x] O teste corrigido falha quando a exclusão é removida numa cópia temporária.
- [x] Não acrescentar campos à CLI exclusivamente para testes.

## Comments

- 2026-09-13 — Criado a partir da revisão dos commits 4eb32c1 e 89ebb36 e das alterações locais. Correção autorizada pelo usuário e iniciada.

- 2026-09-13 — Resolvido. O teste agora verifica exatamente um Trecho na fila, seu texto entregue por next e o fim da fila após a escrita pela CLI. Validação por mutação numa cópia temporária: remover a exclusão de __pycache__ faz o teste falhar com dois Trechos em vez de um. A cópia foi descartada.

Validação: 58 testes dirigidos passaram; suíte completa com 136 testes passando via `.venv/bin/python -m pytest --tb=short`. Regressões funcionais em `tests/test_25_review_regressions.py`; testes ajustados em `tests/test_02_tracer_bullet.py` e `tests/test_23_tickets_avaliacao.py`.
