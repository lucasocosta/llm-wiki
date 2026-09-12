# 04: Guarda de augmentação — seis invariantes, dois modos

**What to build:** Escritas sucessivas na mesma página, feitas por trabalhadores que não se conhecem, passam a enriquecer em vez de degradar. A guarda protege proveniência e cobertura, nunca prosa: reescrever um parágrafo é livre, perder rastro não é. E a consolidação ganha liberdade de reescrever a forma sem nunca poder perder rastro, porque o escape é o modo de operação e não uma chave que o modelo possa setar.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] `sources` é append-only
- [ ] Cabeçalho presente antes continua presente depois
- [ ] Toda footnote citada no corpo resolve para uma entrada de `sources`
- [ ] `type` e id de página existente não mudam por escrita comum
- [ ] Encolhimento do corpo acima de uma fração configurável é recusado
- [ ] Link de saída para concept existente é append-only
- [ ] Cada recusa nomeia a invariante violada e o que foi perdido — quais entradas, quais cabeçalhos, quais links
- [ ] Modo ingestão aplica as seis sem exceção, e é o único que o trabalhador alcança
- [ ] Modo consolidação aceita fundir seção, encurtar e podar link duplicado
- [ ] Nos dois modos, perder a citação de uma entrada de `sources` é recusado
- [ ] Não existe marcador de escape por escrita
- [ ] Link para id inexistente é recusado
