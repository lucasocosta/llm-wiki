# 05: Fila computada e retomada

**What to build:** Ingestão de material longo deixa de ser tudo-ou-nada. A fila é derivada da comparação entre as Fontes declaradas e o que a wiki já tem, então interromper no meio de um PDF de duzentas páginas não perde progresso, e retomar em outra máquina funciona sem nada precisar ser sincronizado. É o que torna viável trabalhar de dentro de um assistente cuja janela de contexto compacta quando quer.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] A fila é derivada da comparação Fontes/wiki, sem arquivo de estado versionado
- [ ] Uma ingestão interrompida retoma sem reprocessar o que já foi feito
- [ ] O item em voo no momento da interrupção volta para a fila
- [ ] Retomar em outra máquina, a partir de um clone, produz a mesma fila
- [ ] Duas pessoas ingerindo em paralelo não produzem conflito em arquivo de estado
