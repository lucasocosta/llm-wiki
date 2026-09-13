# Ticket 11: Aliases de paráfrase e did-you-mean no motor de busca

Type: task
Status: resolved
Blocked by: 01
Related: 10

## Contexto

Na mesma sessão da busca: "busca" e "pesquisa" são semelhantes semanticamente, mas a
busca é lexical e eram o paráfrase não encaixa no vocabulário da wiki. O worker
compensa expandindo a query (o custo por busca é baixo), mas a ferramenta pode oferecer
suporte de primeira classe a duas pontas, **sem chamar LLM** (coerência com ADR 0002):

1. **Aliases curados**: frontmatter `aliases:` (lista de paráfrases colocadas de
   propósito pelos curadores/lavour de páginas) participando do peso lexical.
2. **`did-you-mean`**: quando a busca devolve pouco/nada, a ferramenta sugere termos
   e conceitos próximos que já estão no índice (tokónomia), para o worker redirecionar
   a consulta.

## Trabalho

1. Especificar `aliases:` no frontmatter (novas chaves do OKF: validação opcional,
   impacto em `search`/`shortlist`/índice de máquina, guard de invariantes).
2. Implementar no `search.py`/índice: aliases com peso (decidir: peso de tag? menor
   que título? igual a description?).
3. Implementar suggestion: `search --suggest` (ou flag automática quando `results
   <= 1`), off-model de verdade — listando tokens do índice com maior histórico
   de correspondência parcial (dice/jaccard simples sobre tokens).
4. Testes: (a) alias eleva a página perdedora ao top do ranking; (b) `--suggest`
   devolve termos existentes no índice, nunca alucinados; (c) determinismo da
   pontuação (mesmo índice, mesmo ordem) e (d) reload das medidas de payload
   (ticket 05) para busca/aliases não deteriorar o custo dos resultados.
5. Atualizar skill/reference/README.

## Done

- "pesquisa" encontra "busca" quando a página declara o alias (ou sugere termos
  existentes com `--suggest`), sem LLM na ferramenta e sem custo de payload extra.

## Answer

Motor (`search.py`), sem LLM alguma dívida:

- **aliases**: frontmatter `aliases:` list; cada termo tokenizado com peso
  3.0 (igual a `description`; menor que o título). Índice ganhou
  `index_version: 2` — cache incompatível é rebuilt (chaves velhas REBUILT).
- **did-you-mean**: `_suggestions()` — vocabulário = chaves do `df` do
  índice (por definição existente), candidatos via difflib.get_close_matches
  (cutoff 0.6), ordenados por similaridade, desempate por frequência. O
  `--suggest` muda o shape para `{"results": [...], "suggestions": [...]}`
  (sem flag, payload v/lista — inalterado).
- **Taala de custo**: contas de usage/chars registradas como antes; a sugestão
  com peso não altera o shape do default.

Cobertura de tests/test_24_evidence_aliases.py: alias joga a página para
top-1; sugestões são apenas tokens do vocabulário e ≤5, únicos; shape default
inalteração; determinismo entre rebuilds. **Monografia em produção real**:
com `aliases: [pesquisa, ...]` em wiki-busca-links, a consulta "pesquisa"
agora coloca a página da busca no top-1 (antes: a página adesiva
"objetivos-e-metodologia").
