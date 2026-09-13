# Ticket 01: Fechar o bypass do orçamento por Trecho

Type: task
Status: resolved

## Contexto

Durante o teste de ingestão do PDF, o worker acessou `llmwiki.ingestion.extract_source`
diretamente via Python e leu os 44 Trechos (~69k chars) de uma vez, contornando o
orçamento de 12k por Trecho do `ingest next`. Funcionou, mas só coube porque a sessão
era longa; o mecanismo de orçamento foi inefetivo.

## Trabalho

1. Mapear quem importará/exporta `extract_source` e funções de extração além da CLI
   (`rg "extract_source" src/llmwiki/`).
2. Decidir e implementar uma das alternativas: (a) restringir o acesso externo
   (usar como api pública apenaoir `ingest next/queue`); (b) manter acesso, mas registrar
   aviso/log quando chamado fora do fluxo oficial; (c) outra proposta avaliada no ADR.
3. Teste: tentativa de extração fora do fluxo deve ser bloqueada ou registrar aviso,
   conforme decisão.
4. Atualizar `skill/SKILL.md` documentando que bulk-extraction fora do `next` é antipadrão
   (se for a decisão).

## Done

- Não é mais possível (ou é visível) contornar o teto de `max_trecho_chars` por Trecho
  durante a ingestão; a decisão está documentada e testada.

## Answer

O extractor virou interno: `extract_source` → `_extract_source` (ingestion.py,
3 call sites atualizados); a API pública para obter Trechos continua sendo a CL
(`ingest next`/`queue`). A docstring aponta a decisão e a skill recebe uma
seção "Construction notes" marcando bulk-extraction como antipadrão. Cobertura:
`test_extractor_is_module_private` (tests/test_23_tickets_avaliacao.py).
Escolha pela opção (b): restrição por nome, sem mecanismo de teardown —
barreira mochila suficiente para o worker que segue a skill, sem invenção.
