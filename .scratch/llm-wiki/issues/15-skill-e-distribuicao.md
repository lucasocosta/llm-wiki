# 15: Skill e distribuição sem instalação

**What to build:** De dentro do assistente que a pessoa já usa — Kiro, Copilot, Claude — o assistente descobre a wiki e usa a busca do jeito certo: índice fora do contexto, metadata primeiro, página inteira só quando a resposta exigir. A CLI é o denominador comum entre hosts, e a skill é o ponteiro que ensina quando e como chamá-la. Nenhuma chave de API de LLM em ponto algum.

**Blocked by:** 03, 06.

**Status:** done

- [x] A skill descreve quando e como chamar a busca, com descrição em terceira pessoa e termos-gatilho
- [x] Referências a no máximo um nível de profundidade a partir da skill
- [x] Funciona em qualquer host que execute shell, sem chave de API
- [x] Invocação sem instalação prévia
- [x] A ausência de teste automatizado para a prosa da skill está registrada, com a razão

## Comments

- 2026-09-12 — Reaberto após review de `75597d6...4eb32c1`. Embora a exclusão esteja documentada, a suíte fixa palavras da prosa da skill. Remover essas verificações e preservar as verificações técnicas de distribuição em [23 — adequar testes](23-testes-pelo-contrato-cli.md).

- 2026-09-12 — Concluído. Os asserts de redação (`"use when"`) já haviam sido removidos na passada da issue 23; restava registrar a lacuna com a razão. O docstring de `tests/test_15_skill_distribution.py` agora cita a spec (§203) e referencia apenas as verificações estruturais reais: binário sem chave de API, invocação sem instalação e referências da skill a um nível de profundidade. 3 testes passando.
