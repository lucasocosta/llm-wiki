# 12: Grafo e lint

**What to build:** A wiki passa a poder ser inspecionada como grafo: o que aponta para uma página, o que ninguém alcança, o que aponta para o nada, e onde uma página cresceu demais. A linha de corte é o que a verificação exige — tudo aqui é propriedade do grafo ou do tamanho, computável sem julgamento. Detecção de contradição entre páginas exige entender o que elas afirmam e fica fora.

**Blocked by:** 02.

**Status:** done

- [x] Listar os backlinks de uma página
- [x] Relatório de órfãos: página sem nenhuma aresta de entrada, excluídos os `index.md`
- [x] Relatório de links quebrados
- [x] Aviso de página que passou do tamanho configurável, com os cabeçalhos dela na saída para sugerir onde cortar
- [x] Página longa é avisada, nunca recusada
