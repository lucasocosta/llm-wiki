# Ticket 09: `ingest queue` distinguir Trechos cobertos de backlog pendente

Type: task
Status: wontfix
Blocked by: 01

## Contexto (sessão 2 — wiki de código)

Com a wiki de código recém-adicionada e todas as páginas do PDF já escritas,
`ingest queue` devolveu os 59 Trechos dos **dois** fontes — inclusive os 45 do PDF
já cobertos por páginas existentes. O balanço é "todo o material existente", então o
curador não vê o que falta cobrir sem cruzar com os hashes presentes no frontmatter
das páginas manualmente (ou chamar `next` N vezes).

## Trabalho

1. Definir a semântica prioritária: (a) `queue` passa a filtrar pendentes por padrão
   ("sem página que cita o trecho" / backlog category); (b) nova opjação
   `--pending-only` mantendo o default; ou (c) campo `pending: true/false` por
   item no payload mantido, mais sumário `pending_count`.
2. Definir "coberto" de forma alinhada ao ticket 03 (páginas temáticas multi-Trecho
   cobrem vários hashes de uma vez).
3. Implementar + testes: wiki com todas as páginas → queue vazio/pending 0;
   queue listado com um Trecho novo → só o novo pendente.
4. Refletir no `next`: o motor deve considerar o mesmo critério de cobertura que o
   `queue` (hoje parece que `next` também entende os já-cobertos como próximos).

## Done

- Fluxo de trabalho consome a fila de cima: o que aparece em `next`/`queue` coincide
  com o que de fato falta de página.

## Answer (correção de fato)

O ticket nasceu de uma leitura errada do estado: verificado em 2026-09-12,
`compute_queue` **já** filtra pendentes (`done_trecho_hashes` compara os hashes
carimbados e a fila só entra no hash sem página). Matemática real: 44 (PDF) +
28 (código) = 72 trechos, 21 carimbados nas páginas → fila = 51 = exatamente os
pendentes; `ingest next` também parte da mesma lista. A observação original
comparou a fila pré-cobertura (antes do write das páginas). Sem ação.
