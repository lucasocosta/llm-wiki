# 01: Fundação OKF adotada e sem LLM

**What to build:** A base sobre a qual todo o resto lê e escreve: ler e gravar uma página conforme ao OKF, resolver concept-id a partir do caminho, e gerar `index.md` no formato do §8. O parsing, a validação e a geração vêm do reference agent do OKF, que é Apache 2.0, com atribuição preservada. A função que sintetiza descrição de diretório é substituída por uma determinística: ligá-la como vem faria a ferramenta chamar um LLM e violaria o ADR 0002. Não há comportamento de usuário aqui — é o prefactor que torna as fatias seguintes fáceis.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] Uma página com frontmatter válido é lida e regravada sem perda, e as chaves saem sempre na mesma ordem
- [x] Página sem `type` é recusada
- [x] `index.md` gerado segue o §8: sem frontmatter exceto no raiz, corpo em bullets de título, link e descrição
- [x] A descrição de diretório é composta sem chamada de rede, e a suíte inteira roda offline
- [x] A licença Apache 2.0 e a atribuição do código de origem estão preservadas no repositório

## Comments

- 2026-09-12 — Acompanhamento do review de `75597d6...4eb32c1`. A cobertura da fundação contorna o seam único da CLI. Adequação em [23 — testes pelo contrato da CLI](23-testes-pelo-contrato-cli.md). Este achado de validação não demonstrou falha nos critérios funcionais deste ticket, que permanecem marcados.
