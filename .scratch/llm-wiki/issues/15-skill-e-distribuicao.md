# 15: Skill e distribuição sem instalação

**What to build:** De dentro do assistente que a pessoa já usa — Kiro, Copilot, Claude — o assistente descobre a wiki e usa a busca do jeito certo: índice fora do contexto, metadata primeiro, página inteira só quando a resposta exigir. A CLI é o denominador comum entre hosts, e a skill é o ponteiro que ensina quando e como chamá-la. Nenhuma chave de API de LLM em ponto algum.

**Blocked by:** 03, 06.

**Status:** ready-for-agent

- [ ] A skill descreve quando e como chamar a busca, com descrição em terceira pessoa e termos-gatilho
- [ ] Referências a no máximo um nível de profundidade a partir da skill
- [ ] Funciona em qualquer host que execute shell, sem chave de API
- [ ] Invocação sem instalação prévia
- [ ] A ausência de teste automatizado para a prosa da skill está registrada, com a razão
