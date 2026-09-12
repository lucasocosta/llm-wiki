# 13: Escapes de curador — remover proveniência, mover página

**What to build:** A guarda impede o trabalhador de perder rastro, mas uma pessoa às vezes precisa consertar uma citação errada ou reorganizar a wiki. Esta fatia dá os dois escapes legítimos como comandos próprios, de pessoa, inacessíveis ao trabalhador — que é o que mantém a guarda sendo guarda em vez de sugestão. Sem estes testes, uma guarda implementada como trava absoluta passaria na suíte.

**Blocked by:** 04, 12.

**Status:** ready-for-agent

- [ ] Remover uma entrada de `sources` por comando explícito
- [ ] Mover ou renomear uma página por comando explícito, atualizando quem aponta para ela na mesma operação
- [ ] Depois de mover, o relatório de links quebrados sai vazio
- [ ] Nenhum dos dois comandos é alcançável pelo trabalhador
- [ ] Depois de qualquer dos dois, a guarda continua aplicando as seis invariantes às escritas comuns
