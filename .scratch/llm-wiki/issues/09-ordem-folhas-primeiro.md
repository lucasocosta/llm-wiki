# 09: Ordem folhas-primeiro no grafo de imports

**What to build:** Ler código na ordem alfabética dos arquivos produz páginas rasas, porque um módulo lido sem suas dependências não se explica. A fila passa a sair das folhas do grafo de imports para a raiz, de modo que quando o trabalhador chega num módulo de alto nível os conceitos de que ele depende já existem e podem ser referenciados em vez de reexplicados.

**Blocked by:** 08.

**Status:** done

- [x] A fila de uma Fonte de código sai ordenada das folhas para a raiz
- [x] Ciclo de imports não trava a ordenação nem duplica item na fila
- [x] Um módulo de alto nível encontra na shortlist os conceitos dos módulos que importa
- [x] Arquivo sem import algum aparece antes de qualquer arquivo que o importe
