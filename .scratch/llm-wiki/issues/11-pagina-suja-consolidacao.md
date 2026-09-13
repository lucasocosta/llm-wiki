# 11: Página Suja e passe de consolidação

**What to build:** Uma página escrita a partir de seis Trechos por seis trabalhadores que não se conhecem é uma colagem de seis vozes. Esta fatia dá visibilidade a isso — quais páginas estão sujas — e um passe que as reconcilia numa voz só, relendo apenas a página e sem reabrir as Fontes, o que o torna barato o suficiente para rodar sobre muitas. É opt-in por decisão: consolidar durante a ingestão obrigaria a decidir coerência antes de ter todas as Fontes na mão.

**Blocked by:** 04, 05.

**Status:** done

- [x] Listar as Páginas Sujas da wiki
- [x] Página tocada por um único Trecho não é suja
- [x] Página nunca consolidada e tocada por mais de um Trecho é suja
- [x] A consolidação relê só a página, sem reabrir as Fontes
- [x] A consolidação roda em modo consolidação, com a guarda no perfil correspondente
- [x] Ao terminar, o conjunto de Trechos contribuintes vigente é gravado e a página deixa de ser suja
- [x] O passe nunca dispara durante a ingestão

## Comments

- 2026-09-12 — Reaberto após review de `75597d6...4eb32c1`. A segunda contribuição pode substituir os carimbos anteriores e a página não aparece como suja. Correção em [16 — preservar carimbos](16-preservar-carimbos-augmentacao.md), incluindo regressão antes e depois de consolidar.

- 2026-09-12 — Concluído. Regressões da issue 16 comprovam sujeira antes/depois da consolidação e preservação de histórico em rascunhos incompletos.
