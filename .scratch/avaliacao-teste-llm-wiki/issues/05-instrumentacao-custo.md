# Ticket 05: Instrumentação de custo (payload servido por operação)

Type: task
Status: resolved
Blocked by: 01

## Contexto

O teste só possibilitou estimar custo (~25–35k tokens para construir o wiki; ~2,5k tokens
por consulta de busca). Não há métrica real na ferramenta — o que impede comparar fluxos
objetivamente (ex.: 1:1 + consolidate vs. páginas temáticas).

## Trabalho

1. Definir a métrica: caracteres servidos por operação (`next`, `next` shortlist,
   `search`, `search --snippet`, `read-page`, `write-page`) e registrar no
   `.llmwiki/` (ex.: log de uso) sem alterar a saída analisada pela CLI.
2. Comando ou `ingest report`/`stale report` a incluir resumo de uso (por fonte,
   por dia, por comando).
3. Testes: a contagem é determinística dada a mesma operação; regressão não muda os
   JSONs de saída dos comandos.
4. Documentar como interpretar a métrica (aproximação de custo de contexto).

## Done

- Curador consegue relatar "quantos caracteres a ferramenta serviu nesta sessão",
  comparável entre fluxos de ingestão/consulta.

## Answer

Módulo `llmwiki/usage.py`: cada payload (search, read-page, next, queue) soma
uma linha JSONL em `.llmwiki/usage.jsonl` (falha de telemetria nunca quebra o
comando); `ingest report` inclui `usage` = `{"total_chars","events",
"by_command"}` quando há eventos. O índice de máquina nunca vê o log. Cobertura:
`test_usage_recorded_and_summarized_in_report`. Medição lado worker (tokens
reais) segue no benchmark T06.
