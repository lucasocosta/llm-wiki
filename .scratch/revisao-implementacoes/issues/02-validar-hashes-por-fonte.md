# 02: Validar hashes de Trechos para todos os tipos de Fonte

Type: task
Status: resolved
Priority: P1

## Problema

write-page aceita hashes de outras Fontes textuais ou de conteúdo substituído após next. A fila perde trabalho sem registrar a Fonte contribuinte, ou a versão nova é atribuída ao conteúdo antigo.

## Reprodução

Passar hashes de duas Fontes com --source-id de apenas uma; observar sucesso, fila vazia e proveniência incompleta.

## Critérios de aceitação

- [x] Recusar hashes que não existem na Fonte declarada, antes de alterar páginas, Espelhos ou histórico.
- [x] Manter suporte a vários Trechos da mesma Fonte; Fontes diferentes exigem escritas separadas.
- [x] Cobrir texto, Markdown, PDF, Fonte alterada após next e preservação do estado após recusa pela CLI.

## Comments

- 2026-09-13 — Criado a partir da revisão dos commits 4eb32c1 e 89ebb36 e das alterações locais. Correção autorizada pelo usuário e iniciada.

- 2026-09-13 — Resolvido. A pertença dos hashes é validada para todos os tipos de Fonte antes de qualquer escrita no Bundle. Hash estranho ou de conteúdo substituído resulta em recusa com instrução; a CLI também trata erros de extração. O teste temático foi corrigido para usar duas seções da mesma Fonte. Regressões cobrem texto/Markdown/PDF, hashes de outra Fonte, substituição de conteúdo e ausência de alterações em páginas, Espelhos e histórico após recusa.

Validação: 58 testes dirigidos passaram; suíte completa com 136 testes passando via `.venv/bin/python -m pytest --tb=short`. Regressões funcionais em `tests/test_25_review_regressions.py`; testes ajustados em `tests/test_02_tracer_bullet.py` e `tests/test_23_tickets_avaliacao.py`.
