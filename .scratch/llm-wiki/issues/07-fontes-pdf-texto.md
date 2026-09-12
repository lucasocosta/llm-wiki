# 07: Fontes paginadas e de texto corrido

**What to build:** PDF e texto simples entram na wiki, e PDF escaneado falha alto em vez de produzir páginas vazias — que é o modo de falha caro, porque parece sucesso. A Âncora de citação ganha a forma que cada material permite: número de página no PDF, índice do Trecho no texto sem cabeçalhos.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] PDF com texto extraível é ingerido, e a Âncora das citações é o número de página
- [ ] Texto simples é ingerido; sem cabeçalhos, a Âncora é o índice do Trecho, estável por ser identificado por hash
- [ ] PDF cujo texto extraído fica abaixo do mínimo por página é recusado com erro nomeando o arquivo, e não entra na fila
- [ ] Extração que produz zero texto é erro, nunca uma Fonte de zero Trechos
- [ ] Não há OCR
