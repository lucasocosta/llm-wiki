# Ticket 15: Caminho CLI para enumerar TODOS os Trechos atuais de uma Fonte

Type: task
Status: resolved
Blocked by: 01
Related: 14

## Contexto

Durante a migração de layout (tickets 13–14, sessão 2026-09-13) precisou-se de
re-carimbo em massa: era preciso listar os Trechos **atuais** de cada Fonte
(hashes mesmo já carimbados em páginas). A CLI só expõe:

- `ingest next` / `queue` — entregam apenas Trechos **pendentes** (a fila fica
  vazia quando tudo está carimbado — exatamente o caso da migração);
- `[RETRACTED]` pela parte do worker: foi preciso usar o extractor interno
  `_extract_source` (o antipadrão do ticket 01) para mapear
  `{arquivo/símbolo → hash}` e re-carimbar as 24 páginas.

Isso é um buraco de design: curadoria/migração é fluxo legítimo e não tem
caminho sancionado. A telemetria年老 (usage.jsonl perdia o histórico ao mover
manifesto — ticket 14) reforça: migração é um fluxo de primeira classe.

## Trabalho

1. Comando novo (ou opção): `llm-wiki sources list-trechos [SOURCE_ID]` (ou
   `ingest queue --all-source`): JSON com todos os Trechos atuais
   (`source_id`, `trecho_hash`, `anchor`, `source_path`, `trecho_index`) —
   sem placeholder de texto por default (payload pequeno); `--with-text`
   opcional paga o corpo na tela.
2. Uso interno vira uso externo legal: stamp/curation/migration passam a poder
   validar hash antes de write-page sem tocar no extractor interno.
3. Ticket 14 (migração) utiliza este comando na cura post movimentação —
   recabo o uso de `_extract_source` fora do engine.
4. Testes: payload determinístico e completo (mesma Fonte, mesmos hashes),
   filtragem por source_id; usage contabilizado (ticket 05).
5. Docs: reference.md + SKILL (curation path).

## Done

- Re-carimbo pós-migração 100% via CLI, sem imports internos — reproduzível
  por qualquer curador seguindo só a skill.

## Comments

- 2026-09-13: aberto pela auditoria dos tickets desta sessão — o gap custou
  duas gambiarras internas na sessão (re-carimbo do PDF pages e das páginas de
  código após mudança de layout).
