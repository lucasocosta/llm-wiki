# 04: Ler métricas de uso na raiz do manifesto

Type: task
Status: resolved
Priority: P2

## Problema

Os comandos registram métricas na raiz do manifesto, mas ingest report procura no diretório pai do Bundle. Com bundle_dir: docs/wiki, usage desaparece.

## Reprodução

Executar search com Bundle docs/wiki; conferir que ingest report não inclui usage apesar do log gravado.

## Critérios de aceitação

- [x] Gravação e leitura de uso compartilham a raiz do manifesto.
- [x] Cobrir Bundle simples, aninhado e invocação com -C.
- [x] Verificar contagens exatas dos payloads pela CLI.

## Comments

- 2026-09-13 — Criado a partir da revisão dos commits 4eb32c1 e 89ebb36 e das alterações locais. Correção autorizada pelo usuário e iniciada.

- 2026-09-13 — Resolvido. ingest report consulta usage na raiz do manifesto, usada também na gravação. O teste parametrizado cobre wiki e docs/wiki, invocação com -C e contagem exata de eventos/caracteres; a cobertura existente mantém a invocação direta.

Validação: 58 testes dirigidos passaram; suíte completa com 136 testes passando via `.venv/bin/python -m pytest --tb=short`. Regressões funcionais em `tests/test_25_review_regressions.py`; testes ajustados em `tests/test_02_tracer_bullet.py` e `tests/test_23_tickets_avaliacao.py`.
