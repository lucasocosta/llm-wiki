# 14: `log.md` como histórico legível

**What to build:** Uma pessoa consegue auditar o que a ferramenta fez sem ler o histórico do git. O registro é cronológico e append-only, e é deliberadamente **só história**: se virar estado, reintroduz o arquivo versionado de conflito que a fila computada existe para eliminar.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] Registro cronológico com cabeçalhos de data ISO, mais novo primeiro
- [ ] Parseável por ferramentas unix comuns
- [ ] Apagar o arquivo não afeta a fila, a sujeira nem a obsolescência
- [ ] É arquivo reservado do OKF e não é tratado como concept
