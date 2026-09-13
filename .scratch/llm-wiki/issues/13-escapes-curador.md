# 13: Escapes de curador — remover proveniência, mover página

**What to build:** A guarda impede o trabalhador de perder rastro, mas uma pessoa às vezes precisa consertar uma citação errada ou reorganizar a wiki. Esta fatia dá os dois escapes legítimos como comandos próprios, de pessoa, inacessíveis ao trabalhador — que é o que mantém a guarda sendo guarda em vez de sugestão. Sem estes testes, uma guarda implementada como trava absoluta passaria na suíte.

**Blocked by:** 04, 12.

**Status:** done

- [x] Remover uma entrada de `sources` por comando explícito
- [x] Mover ou renomear uma página por comando explícito, atualizando quem aponta para ela na mesma operação
- [x] Depois de mover, o relatório de links quebrados sai vazio
- [x] Nenhum dos dois comandos é alcançável pelo trabalhador
- [x] Depois de qualquer dos dois, a guarda continua aplicando as seis invariantes às escritas comuns

## Comments

- 2026-09-12 — Reaberto após review de `75597d6...4eb32c1`. Mover entre diretórios não recalcula os links de saída da página movida. Correção e regressão em [21 — preservar links ao mover](21-preservar-links-ao-mover.md), que também trata a possível duplicação da resolução de destinos apontada no eixo Standards.

- 2026-09-12 — Concluído. Issue 21 corrigiu links de saída ao mover entre diretórios; backlinks, fragmentos e relatório de links quebrados validados pela CLI.
