# 21: Preservar links relativos ao mover uma página entre diretórios

**Status:** done
**Priority:** P2
**Blocked by:** None (can start immediately).
**Related:** [13 — escapes de curador](13-escapes-curador.md), [spec — armazenamento](../spec.md#armazenamento).

## Problema

Review de `75597d6...4eb32c1`: `cmd_move_page`, em `src/llmwiki/commands/sources.py`, grava a página no novo diretório sem recalcular seus links de saída. A atualização de quem aponta para ela não basta: os links são relativos ao diretório da própria página.

O ticket 13 exige “Depois de mover, o relatório de links quebrados sai vazio”. Há também possível Duplicated Code: `_rewrite_links` mantém uma resolução de destinos separada de `src/llmwiki/links.py`, usada pela guarda e pelo grafo. Tratar esse julgamento de padrões junto da correção funcional.

## Reprodução pela CLI

1. Criar as páginas `other` e `a`; o corpo de `a` contém `[other](other.md)`.
2. Confirmar `graph broken-links` vazio.
3. Executar `sources move-page --from a --to nested/a`.
4. Consultar `read-page nested/a` e `graph broken-links`.

Atual: o corpo conserva `other.md`, que agora resolve para o id inexistente `nested/other`. Esperado: link `../other.md`, mantendo o destino original.

## Critérios de aceitação

- [x] A página movida preserva os destinos de seus links de saída, recalculando caminhos relativos ao novo diretório.
- [x] Quem aponta para ela é atualizado na mesma operação; o relatório de links quebrados continua vazio para Bundle inicialmente válido.
- [x] Fragmentos, links para a própria página e movimentações entre diretórios em profundidades diferentes preservam o destino pretendido.
- [x] Links externos e âncoras locais que não dependem do diretório permanecem válidos.
- [x] A resolução de destinos usa a regra compartilhada com guarda/grafo, evitando manter outra interpretação em `_rewrite_links`.
- [x] Testes pela CLI verificam corpo, backlinks e links quebrados após mover; não testam apenas renomear dentro do mesmo diretório.

## Comments

- 2026-09-12 — Em andamento. Reprodução de movimentação entre diretórios, incluindo links de saída, fragmentos e links para a própria página.

- 2026-09-12 — Concluído. 10 testes de movimentação, escapes e grafo passaram; links são resolvidos na localização antiga, preservando destinos e fragmentos. Resolução compartilhada com a guarda e o grafo.
