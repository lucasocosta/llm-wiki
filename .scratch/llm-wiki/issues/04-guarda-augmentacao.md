# 04: Guarda de augmentação — seis invariantes, dois modos

**What to build:** Escritas sucessivas na mesma página, feitas por trabalhadores que não se conhecem, passam a enriquecer em vez de degradar. A guarda protege proveniência e cobertura, nunca prosa: reescrever um parágrafo é livre, perder rastro não é. E a consolidação ganha liberdade de reescrever a forma sem nunca poder perder rastro, porque o escape é o modo de operação e não uma chave que o modelo possa setar.

**Blocked by:** 02.

**Status:** done

- [x] `sources` é append-only
- [x] Cabeçalho presente antes continua presente depois
- [x] Toda footnote citada no corpo resolve para uma entrada de `sources`
- [x] `type` e id de página existente não mudam por escrita comum
- [x] Encolhimento do corpo acima de uma fração configurável é recusado
- [x] Link de saída para concept existente é append-only
- [x] Cada recusa nomeia a invariante violada e o que foi perdido — quais entradas, quais cabeçalhos, quais links
- [x] Modo ingestão aplica as seis sem exceção, e é o único que o trabalhador alcança
- [x] Modo consolidação aceita fundir seção, encurtar e podar link duplicado
- [x] Nos dois modos, perder a citação de uma entrada de `sources` é recusado
- [x] Não existe marcador de escape por escrita
- [x] Link para id inexistente é recusado

## Comments

- 2026-09-12 — Reaberto após review de `75597d6...4eb32c1`. A ingestão aceita remover a citação do corpo quando sua entrada permanece em `sources`. Correção e regressão pela CLI em [18 — preservar citações](18-preservar-citacoes-ingestao.md).

- 2026-09-12 — Concluído. Issue 18 corrige perda de citação na ingestão; regressões dos dois modos e escapes do curador passaram.
