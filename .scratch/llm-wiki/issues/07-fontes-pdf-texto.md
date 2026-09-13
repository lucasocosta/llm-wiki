# 07: Fontes paginadas e de texto corrido

**What to build:** PDF e texto simples entram na wiki, e PDF escaneado falha alto em vez de produzir páginas vazias — que é o modo de falha caro, porque parece sucesso. A Âncora de citação ganha a forma que cada material permite: número de página no PDF, índice do Trecho no texto sem cabeçalhos.

**Blocked by:** 02.

**Status:** done

- [x] PDF com texto extraível é ingerido, e a Âncora das citações é o número de página
- [x] Texto simples é ingerido; sem cabeçalhos, a Âncora é o índice do Trecho, estável por ser identificado por hash
- [x] PDF cujo texto extraído fica abaixo do mínimo por página é recusado com erro nomeando o arquivo, e não entra na fila
- [x] Extração que produz zero texto é erro, nunca uma Fonte de zero Trechos
- [x] Não há OCR

## Comments

- 2026-09-12 — Acompanhamento do review de `75597d6...4eb32c1`. O teto de orçamento das histórias 13–14 da spec não foi decomposto nos tickets originais. Implementação e regressões para texto e PDF em [22 — teto de Trechos](22-teto-orcamento-trechos.md).
