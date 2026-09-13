# 18: Recusar perda de citações também na ingestão

**Status:** done
**Priority:** P1
**Blocked by:** None (can start immediately).
**Related:** [04 — guarda](04-guarda-augmentacao.md), [spec — testes dos dois modos](../spec.md#testing-decisions).

## Problema

Review de `75597d6...4eb32c1`: `check_write`, em `src/llmwiki/guard.py`, verifica se as entradas de `sources` continuam presentes e se as footnotes restantes resolvem. Na ingestão, isso permite remover uma citação do corpo mantendo sua entrada no frontmatter.

Requisito do ticket 04: “Nos dois modos, perder a citação de uma entrada de `sources` é recusado”. A atribuição de uma alegação desaparece mesmo que o id permaneça na lista de proveniência.

## Reprodução pela CLI

1. Gravar pela ingestão uma Página Conceitual com `sources: [{id: s1}]`, cabeçalho `# Exemplo` e corpo contendo `Afirmação documentada[^s1].`.
2. Tentar augmentá-la com `ingest write-page`, mantendo a entrada `s1`, o cabeçalho e o restante do conteúdo, mas removendo `[^s1]`. Manter comprimento suficiente para não acionar a recusa por encolhimento.

Atual: escrita aceita. Esperado: recusa nomeando `s1` e instruindo o trabalhador a preservar a citação no corpo.

## Critérios de aceitação

- [x] Uma entrada citada antes continua citada no corpo depois, tanto na ingestão quanto na consolidação.
- [x] Manter a entrada apenas em `sources` não satisfaz a preservação da citação.
- [x] A recusa identifica a citação perdida e como corrigir; a página persistida permanece intacta.
- [x] Reescrever a frase ou deslocar a citação, mantendo a atribuição, continua permitido quando as demais invariantes do modo são satisfeitas.
- [x] O comando explícito do curador continua sendo a via de remoção de proveniência; nenhum campo no rascunho desliga a guarda.
- [x] Testes pela CLI cobrem recusa nos dois modos e escrita válida com citação preservada, sem invocar a guarda diretamente.

## Comments

- 2026-09-12 — Em andamento. Reprodução da perda de footnote nos dois modos pela CLI.

- 2026-09-12 — Concluído. Regressão falhou na ingestão antes da correção e passou nos dois modos depois; 17 testes de citações, guarda e escapes de curador passaram.
