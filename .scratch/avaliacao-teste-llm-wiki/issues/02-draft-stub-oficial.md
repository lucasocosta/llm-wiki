# Ticket 02: Página "draft"/stub oficial com links pendentes

Type: task
Status: resolved
Blocked by: 01

## Contexto

`write-page` valida links de saída (`broken-links`) na escrita, então páginas que se
referenciam mutuamente não podem ser criadas em qualquer ordem. No teste foi preciso
improvisar duas passadas: criar todas como stubs sem links e depois reescrever com o
conteúdo cheio — retrates evitáveis.

## Trabalho

1. Desenhar o mecanismo de página pendente: ex. frontmatter `draft: true` aceitando
   links quebrados, com verificação completa ao remover o flag (ou outro desenho a
   validar contra o ADR 0001/0002).
2. Implementar na CLI (`ingest write-page`, `stale report` / `graph lint` merecem
   listar páginas em draft).
3. Testes: página com link para página inexistente + `draft: true` grava; confirmar
   que o índice e `search`/`graph` se comportam de forma coerente com draft.
4. Documentar no skill o fluxo recomendado para construção com links circulares.

## Done

- Curador consegue criar páginas interdependentes num fluxo oficial, sem passadas
  improvisadas de stub; lint lista o que ainda está pendente.

## Answer

Frontmatter `draft: true` desarma a regra "sem link para página inexistente" no
guard (outros invariantes continuam valendo); abolir o flag revalida os links
na próxima escrita. `graph lint` passou a reportar `draft_pages` (a to-do de
curadoria) junto de `long_pages`. Cobertura: `test_draft_page_accepts_broken_link_and_lint_lists_it`,
`test_dropping_draft_revalidates_links`.
