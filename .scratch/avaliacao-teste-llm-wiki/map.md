# Avaliação do teste de ingestão do PDF (monografia Mosaicode)

Resultado da sessão de teste de 2026-09-12: o PDF na raiz do projeto foi ingerido e
transformado em Bundle (`wiki/`) com 14 páginas temáticas, proveniência verificável
(`stale report` limpo) e busca off-model funcionando.

## O que o teste validou

- Guardas e stamping de `write-page` funcionaram (recusas de YAML inválido, links para
  páginas inexistentes, invariantes de apêndice).
- Proveniência verificável ponta a ponta; `stale: False` nas páginas após validação.
- Leitura barata: `search` só-metadados (~0,6k tokens), `read-page` por página (~0,7k tokens),
  10–20× mais barato que dumping do bundle ou do PDF.

## Problemas observados (validados na sessão)

- O extractor interno (`extract_source`) permitiu leitura em bulk de 69k chars,
  contornando o orçamento de 12k por Trecho do `ingest next`.
- Links circulares + validação de `broken-links` na escrita exigiram passada de stubs
  improvisada e depois reescrita com conteúdo cheio.
- Mensagens de erro reportam sintoma, não causa (`:` de YAML sem aspas; content-file vazio
  por buffer não descartado → "sem type").
- Sem métrica real de custo: tokens só como estimativa (~25–35k para construir o wiki;
  ~2,5k por consulta).
- Fluxo 1 página por Trecho + `consolidate` contrasta com o atalho usado (consolidar
  Trechos em páginas temáticas com hashes múltiplos no frontmatter) — decisão de design
  ainda em aberto.

## Tópicos derivados

Cada trabalho futuro virou um ticket em [issues/](issues/).

## Decisions-so-far

- 2026-09-12 — Tickets 01,02,03,04,05,07,08 implementados e testados (119 passed:
  108 pré-existentes + 11 novos em tests/test_23_tickets_avaliacao.py); T06
  measure em [benchmark.md](benchmark.md) (search ~230 tok, dump do bundle ~15k tok
  lokalizada → consultas custam 1–3% de um dump); T09 marcado wontfix por correção
  de fato: compute_queue JÁ filtra pendentes (72 trechos - 21 carimbados = 51 na fila,
  verificado). docs: skill/SKILL.md (Construction notes), skill/reference.md
  (draft_pages INÍCIO, trecho-hash repetível, excluded_unreadable + usage no report),
  README.md (location repo-relativo para código).


### Terceira rodada (avaliando o modo de falha de RAG, 2026-09-12)

Questionamento: com busca lexical, "busca" vs "pesquisa" (semântica idêntica) desliza
para páginas adjacentes; worker pode responder errado com confiança, como um RAG com
retrieval ruim. Defesas pensadas: cadeia de provedor auditável (página → trecho → hash),
`stale` qualifica, leitura de páginas inteiras, múltiplas buscas baratas. Lacunas
genuinas viraram tickets: **10** (protocolo de evidência + resposta "a wiki não sabe" como
saída normal — depende do benchmark 06) e **11** (aliases de paráfrase no frontmatter +
`search --suggest` off-model — depende do ticket 01 no sentido de design do motor).

### Resalva aberta (código sem commit)

As páginas wiki-grafo-lint e wiki-comandos-log (e o Espelho references/llmwiki-src)
ficaram `unverifiable` no stale report porque os arquivos de código mudaram sem
commit — comportamento do desenho (não-inventar-SHA). Após commit das alterações
em src/, re-carimbar essas páginas via `ingest write-page` e a proveniência volta
a ser verificável.

### Demonstração emergente (makerspace da aplicação)

Durante a resolução, editar graph.py/commands/ingest.py fez o stale report apontar
exatamente as páginas afetadas com diff de hash por arquivo; apela o re-carimbo
traindo o ciclo completo do desenho.

- 2026-09-12 (quarta rodada) — Tickets 10 e 11 RESOLVIDOS: `search.py` (aliases
  peso 3.0, `index_version: 2`, `_suggestions()` did-you-mean via difflib sobre o
  vocabulário do índice), `commands/query.py` (`--suggest` → shape
  {"results","suggestions"} — sem flag, payload de lista intacto), skill "Evidence
  protocol". Testes: 123 passed (+4 em test_24_evidence_aliases.py Demonstração
  na wiki real: com aliases em wiki-busca-links, "pesquisa" agora traz a página da
  busca no top-1 (antes deslizei para objetivos-e-metodologia); `--suggest` com typo
  ("pesquisa lexcial axis") devolve termos reais do vocabulário. wiki-busca-links
  re-carimbada com o Trecho de search.py novo (stale []) — `unverifiable` restantes
  continuam explicados pelo estado sem commit.

### Quarta rodada (incidente de push + layout, 2026-09-13)

Agente antecessor empurrou para origin `sources/poc-…pdf` (792 KB, documento de
terceiros) e `wiki/` — `git ls-files` confirma versioneção; `.gitignore` já explicava
`.llmwiki/` como estado derivado não-versionado. Tickets: **12** (incidente: purga
do PDF do histórico é decisão humana com force-push; proteger com política
documentada do que versionar) e **13** (now layout — grilling: mover wiki/ para
dentro de .llmwiki/ conflita com o invariante derivado-não-versionado e com Fonte
code externa lida in-place; alternativa registrada: documentar layout padrão +
`llm-wiki init` + `.gitignore` scaffolding, sem dir surgery). Fronteira após triagem.

- 2026-09-13 (quinta rodada) — Ticket 13 RESOLVIDO por decisão do maintainer: recom
  oposição consiate no layout: `llm-wiki/{wiki,sources}` versionado na raiz, `.llmwiki/`
  derivada intocada. Implementado na hora: `git mv`, manifesto remapeado; **bug de
  `_index_dir`** (path pai do bundle → colisão `llm-wiki/.llmwiki` em produção) resol
 vido resolvendo a raiz pelo `llm-wiki.yml` (subida na árvore, fallback antigo); uso
 (**usage**) unificado na raiz da CLI; 21 páginas re-carimb var/actualizadas post-move
 (migração sem commit vira `unverifiable` — design). Suite 136 yede passed→136
 (nested-layout test novo). Sobrou o produto do padrão no ticket 14
 (`llm-wiki init` + migração). `unverifiable: []` após commit do outro agente;
 novo `unverifiable` apenas para as mudanças desta rodada — Archive/commit pendente.

Manifest também migrou para llm-wiki/ (um lugar só, pergunta do mantenedor);
trade-offs e o warn da telemetria registrados no ticket 13; suite 137 passed.
trade-offs e o warn da telemetria registrados no ticket 13; suite 137 passed.
- 2026-09-13 — Ticket **15** aberto: enumerar TODOS os Trechos atuais da Fonte pela
  CLI (`queue`/`next` só dão pendentes; migração ficou sem caminho sancionado
  e forçou uso do extractor interno duas vezes"). Fronteira atual após triagem
  pode começar por 14 ou 15 (ambos blocked somente via design 01).

- 2026-09-13 (validação de ciclo completo) — Tickets 14 e 15 IMPLEMENTADOS e resolvidos;
  depois validação pedida pelo maintainer: **limpeza total do Bundle** (`llm-wiki/wiki`
  rebuilt from scratch) e reingestão do PDF + código via *só CLI*: `ingest report/queue`,
  `sources list-trechos --with-text` (corpo ily lido via o novo comando, 75 Trechos),
  24 páginas escritas com o fluxo draft→full (tickets 02/03), validações: broken-links
  [], lint/draft_pages [], stale []. Pendência honesta: 52 Trechos ainda não curados
  (peças limias e módulos de código secundários — a fila fica para uma próxima curadoria);
  unverifiable: exatamente os 2 arquivos modificados nesta sessão sem commit
  (search.py, commands/ingest.py) — comportamento por desenho.
- 2026-09-13 — Ticket 12 RESOLVIDO por decisão: .gitignore passa a ignorar a
  pasta `llm-wiki/` inteira (wiki + sources + .llmwiki = estado local), com o
  desenho de reverter documentado no comentário do próprio arquivo; os arquivos
  antigos (incl. PDF) têm `git rm --cached` ja agendado no próximo commit.
  README atualizado; trade-off assumido: clone novo ← reingestão para páginas
  PDF; páginas de código continuam verificáveis por commit do src.
- 2026-09-13 — Precisa o escopo: o ignore da pasta inteira é **política local,
  não o default da tool** (a wiki deste repo é apenas teste). `init` voltou ao default
  neutro (só `.llmwiki/` + comentário orientando as duas políticas); README agora
  distingue o gênero (decision) do curador vs. o caso deste repo. Suite 141 passed;
  git untrack caged no próximo commit (histórico de páginas/PDF: ver ticket 12).
