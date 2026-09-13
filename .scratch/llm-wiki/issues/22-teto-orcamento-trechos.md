# 22: Implementar teto de orçamento configurável para Trechos

**Status:** done
**Priority:** P2
**Blocked by:** None (can start immediately).
**Related:** [02 — Markdown](02-tracer-bullet-markdown.md), [07 — PDF e texto](07-fontes-pdf-texto.md), [08 — código](08-fontes-codigo.md), [spec — histórias 12 a 14](../spec.md#ingerir).

## Problema

Review de `75597d6...4eb32c1`: os extratores em `src/llmwiki/extract.py` e `src/llmwiki/code.py` produzem Trechos por seção, parágrafo, página ou arquivo, sem teto de orçamento. Uma fronteira natural grande demais pode exceder o contexto do trabalhador.

A spec pede “um teto de orçamento que force o corte quando a fronteira natural é grande demais” e “sobrepor esse teto sem trocar a estratégia de corte” (histórias 13 e 14). Esses requisitos não ganharam critério próprio nos 15 tickets originais.

## Reprodução pela CLI

1. Declarar uma Fonte Markdown com um único cabeçalho e conteúdo muito grande abaixo dele, ou texto simples com um parágrafo muito grande.
2. Executar `ingest next` e inspecionar o tamanho do texto entregue.
3. Consultar as opções da CLI e do manifesto: não existe configuração que limite esse Trecho.

Atual: toda a unidade é entregue, independentemente do tamanho. Esperado: fronteiras naturais continuam sendo a primeira escolha, com corte adicional determinístico quando necessário.

## Critérios de aceitação

- [x] Definir e documentar unidade de medida, valor padrão e forma de sobrepor o teto, sem chamada a LLM ou serviço externo. A escolha exata pode ser resolvida na implementação.
- [x] O teto se aplica a Markdown, texto simples, PDF e código, incluindo uma única fronteira natural maior que o limite.
- [x] Sobrepor o teto não troca a estratégia de delimitação natural; subdivisão adicional ocorre quando ela é necessária para respeitar o orçamento.
- [x] Nenhum conteúdo é descartado silenciosamente; os Trechos mantêm Âncoras rastreáveis à Fonte e identidade determinística para a mesma Fonte/configuração.
- [x] Configuração inválida é recusada com mensagem útil; o item entregue respeita a unidade e o teto documentados.
- [x] Testes pela CLI usam limites pequenos para verificar corte forçado, sobreposição do teto, conteúdo preservado e retomada com a mesma configuração, incluindo PDF real.
- [x] A interface escolhida e sua relação com a retomada são documentadas junto do contrato de uso da CLI.

## Comments

- 2026-09-12 — Em andamento. Definir teto em caracteres Unicode, padrão de 12000 por Trecho, com override --max-trecho-chars e configuração no manifesto; preservar fronteiras naturais e conteúdo.

- 2026-09-12 — Concluído. Teto padrão 12000 caracteres Unicode, manifesto e override CLI implementados. 22 testes de orçamento, extração e ordem de código passaram; limites pequenos comprovam texto/Âncoras preservados e retomada. Contrato e efeito de mudar o teto documentados no README.
