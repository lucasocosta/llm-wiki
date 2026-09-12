# 03: Busca lexical sobre o índice de máquina

**What to build:** Perguntar e receber as páginas certas, sem que o índice entre no contexto de quem perguntou. A CLI ranqueia fora do modelo e devolve só os vencedores em forma de metadata; o corpo da página só sai quando alguém pedir a página. É esta fatia que faz a wiki valer o esforço de ter sido construída.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] O índice cobre frontmatter e corpo, com peso maior em título, descrição e tags
- [ ] Cada resultado traz id, título, `type` e descrição, e nunca o corpo
- [ ] Filtro por `type` e por tags
- [ ] O snippet do trecho que casou só aparece com a flag; não é o padrão
- [ ] O índice vive fora do controle de versão e é reconstruído quando as páginas mudam
- [ ] Sobre fixtures conhecidas, a ordem dos resultados é a esperada
- [ ] Busca lexical apenas: nenhum embedding, nenhum índice vetorial, nenhum modelo local
