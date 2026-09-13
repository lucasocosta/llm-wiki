# Ticket 03: Consolidar Trechos em páginas temáticas como caminho de primeira classe

Type: task
Status: resolved
Blocked by: 01

## Contexto

O fluxo atual implica 1 página por Trecho e depois `consolidate`. No teste, o worker
consolidou diretamente os 44 Trechos da monografia em 14 páginas temáticas, com múltiplos
hashes no frontmatter `trechos:` — bundle 3× menor, rastreabilidade preservada, uma
etapa a menos. Isso foi feito fora do trilho oficial.

## Trabalho

1. Avaliar contra o design (ADR 0002 e spec): o caminho "páginas temáticas a partir de
   vários Trechos" deve virar caminho suportado (ex.: `ingest next --group THEME` ou
   `write-page` aceitando lista de hashes) ou permanecês-lo como antiprática documentada.
2. Implementar a decisão (meios: opção de grupo em `next`/`queue`, aceitação de múltiplos
   `--trecho-hash`, ou ambas).
3. Testes cobrindo: proveniência de múltiplos Trechos, retomada com teto alterado,
   invariante de apêndice de `trechos` em reescrita.
4. Alinhar `skill/SKILL.md` e `reference.md` com o caminho escolhido.

## Done

- Existe um fluxo oficial (documentado e testado) que produz o bundle temático do teste
  sem fora da CLI oficial.

## Answer

Caminho temático oficial via CLI: `--trecho-hash` é repetível (argparse append),
`stamp_write` aceita lista, deduplica, valida todos contra a Fonte e atualiza a
versão por arquivo para código. A frente `trechos` sobrou ainda mais append-only.
`next --group` ficou fora (YAGNI: a shortlist + múltiplos hashes cobrem o caso
temático). Cobertura: `test_write_page_accumulates_multiple_trecho_hashes`,
`test_single_hash_writes_still_work`. Documentado em skill/reference/README.
