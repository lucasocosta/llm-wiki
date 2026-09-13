# 17: Preservar a versão da Fonte por Página Conceitual

**Status:** done
**Priority:** P1
**Blocked by:** None (can start immediately).
**Related:** [10 — obsolescência](10-obsolescencia.md), [16 — carimbos](16-preservar-carimbos-augmentacao.md), [19 — código local](19-proveniencia-codigo-local.md), [spec — armazenamento](../spec.md#armazenamento).

## Problema

Review de `75597d6...4eb32c1`: `staleness_report`, em `src/llmwiki/staleness.py`, consulta a versão no Espelho de Fonte compartilhado. `ensure_reference` atualiza esse Espelho a cada escrita. Reingerir uma Página Conceitual limpa indevidamente a obsolescência das demais páginas derivadas da mesma Fonte.

Requisito do ticket 10: “Página derivada de arquivo fica obsoleta quando o hash do conteúdo muda”. O esclarecimento na spec registra que a versão usada na derivação pertence à Página Conceitual; atualizar o Espelho não atualiza páginas antigas.

## Reprodução pela CLI

1. Declarar uma Fonte Markdown com seções Alpha e Beta. Usar `ingest next` e `ingest write-page` para gravar `alpha` a partir da primeira e `beta` a partir da segunda.
2. Alterar o conteúdo das duas seções. `stale report` lista as duas páginas como obsoletas.
3. Reingerir somente o novo Trecho Alpha e gravar somente `alpha`.
4. Consultar `stale report`, `read-page beta` e `ingest queue`.

Atual: o relatório deixa de listar ambas as páginas, embora Beta ainda esteja na fila. Esperado: `beta` continua obsoleta e sua leitura inclui o aviso.

## Critérios de aceitação

- [x] A tool persiste na Página Conceitual a versão efetivamente usada de cada Fonte contribuinte; hash para arquivo e proveniência verificável por arquivo/revisão para código.
- [x] Reingerir `alpha` não altera a versão registrada em `beta`; relatório e leitura mantêm o aviso de `beta`.
- [x] O relatório compara a versão usada por aquela página com a versão atual e mostra o que mudou, mesmo após atualizar o Espelho.
- [x] Páginas com várias Fontes preservam a proveniência das Fontes que não participaram da escrita atual.
- [x] Copiar o Bundle sem cache mantém a detecção; o índice e o Espelho não substituem o registro persistido na página.
- [x] Páginas antigas sem registro suficiente não são declaradas atuais por inferência a partir do Espelho atualizado; a limitação é explícita, sem inventar uma versão histórica.
- [x] Testes pela CLI cobrem a reingestão parcial e verificam o estado persistido, sem injetar proveniência apenas em memória.

## Comments

- 2026-09-12 — Em andamento. Regressões de reingestão parcial, múltiplas Fontes e proveniência histórica insuficiente.

- 2026-09-12 — Em andamento. Reingestão parcial, várias Fontes, clone sem cache e estado histórico desconhecido passam. Proveniência de código será validada com as issues 19–20 antes de encerrar todos os critérios.

- 2026-09-12 — Concluído. Versões por página e por arquivo contribuinte verificadas com reingestão parcial, múltiplas Fontes, clone sem cache e histórico legado desconhecido. 22 testes relacionados passaram.
