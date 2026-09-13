# 14: `log.md` como histórico legível

**What to build:** Uma pessoa consegue auditar o que a ferramenta fez sem ler o histórico do git. O registro é cronológico e append-only, e é deliberadamente **só história**: se virar estado, reintroduz o arquivo versionado de conflito que a fila computada existe para eliminar.

**Blocked by:** 02.

**Status:** done

- [x] Registro cronológico com cabeçalhos de data ISO, mais novo primeiro
- [x] Parseável por ferramentas unix comuns
- [x] Apagar o arquivo não afeta a fila, a sujeira nem a obsolescência
- [x] É arquivo reservado do OKF e não é tratado como concept

## Comments

- 2026-09-12 — Acompanhamento do review de `75597d6...4eb32c1`. O teste de ordenação do histórico chama a implementação diretamente, contrariando o seam único da CLI. Adequação em [23 — testes pelo contrato da CLI](23-testes-pelo-contrato-cli.md). Este achado de validação não demonstrou falha nos critérios funcionais deste ticket, que permanecem marcados.
