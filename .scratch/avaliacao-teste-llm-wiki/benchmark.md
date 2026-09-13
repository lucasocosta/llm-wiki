# Benchmark T06: custo de contexto por caminho de recuperação

Medido em 2026-09-12 no repo real (wiki com 24 páginas de 2 Fontes; 45+20 Trechos
pendentes). Conversão indicativa: ~4 chars/token para texto técnico.

| Caminho | Chars servidos | Tokens de contexto (~) |
|---|---|---|
| `search "ingest queue pendente"` (10 itens, sem corpo) | 920 | ~230 |
| `search --snippet` | 1.786 | ~450 |
| `read-page` (1 página, média) | 2.792 | ~700 |
| `ingest next` (work item completo + shortlist) | 1.784 | ~450 |
| `ingest queue` (todos os pendentes) | 8.412 | ~2.100 |
| **Dumpar o Bundle inteiro** | 61.565 | ~15.400 |
| **Ler a árvore-fonte inteira (28 arquivos)** | 108.109 | ~27.000 |

Fator de economia do desenho: uma consulta típica custa **1–3%** de um dump do
Bundle e menos de 1% da leitura das Fontes em bruto.

## Limitações

- Os números são de **payload servido (chars)**, não tokens efetivos de contexto
  do worker; a conversão é indicativa. Uma bateria com contagem de tokens real
  exige um runtime de agente que reporte usage por chamada.
- `ingest report` agora traz `usage` (chars servidos por comando, ticket 05),
  cobrindo o lado da ferramenta; o lado do worker sai do runtime do agente.

## Conclusão

A economia prometida na skill ("a busca ranqueia off-model e devolve só
metadados") é coerente com a medição: `search` sem corpo custa ~230 tokens
contra ~15k de um dump. A estimativa anterior em ordem de grandeza (~0,6k por
search, ~0,7k por read-page) permanece correta (diferenças vêm do número de
resultados e do `--snippet`).
