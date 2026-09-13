# 05: Fila computada e retomada

**What to build:** Ingestão de material longo deixa de ser tudo-ou-nada. A fila é derivada da comparação entre as Fontes declaradas e o que a wiki já tem, então interromper no meio de um PDF de duzentas páginas não perde progresso, e retomar em outra máquina funciona sem nada precisar ser sincronizado. É o que torna viável trabalhar de dentro de um assistente cuja janela de contexto compacta quando quer.

**Blocked by:** 02.

**Status:** done

- [x] A fila é derivada da comparação Fontes/wiki, sem arquivo de estado versionado
- [x] Uma ingestão interrompida retoma sem reprocessar o que já foi feito
- [x] O item em voo no momento da interrupção volta para a fila
- [x] Retomar em outra máquina, a partir de um clone, produz a mesma fila
- [x] Duas pessoas ingerindo em paralelo não produzem conflito em arquivo de estado

## Comments

- 2026-09-12 — Reaberto após review de `75597d6...4eb32c1`. Augmentar a mesma página sem repetir metadados automáticos apaga o carimbo anterior e devolve um Trecho concluído à fila. Correção e reprodução em [16 — preservar carimbos](16-preservar-carimbos-augmentacao.md).

- 2026-09-12 — Concluído. Regressões da issue 16 e testes de retomada passaram; Trechos concluídos não retornam à fila após augmentar a mesma página.
