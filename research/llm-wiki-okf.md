# llm-wiki em OKF: fundamentação por fontes primárias

> Convenção de notas deste repositório: notas de pesquisa vivem em `research/*.md`. Este arquivo inaugura a convenção — antes dele o repo não tinha padrão para notas. Toda afirmação factual carrega sua fonte inline (URL ou caminho-no-repo); o que é dedução vai marcado `[inferido]`.
>
> **Escopo: pesquisa, não especificação.** Este documento registra o que as fontes primárias afirmam e o que deixam em aberto. Não propõe arquitetura, API, nem escolhas de implementação — decisões de projeto pertencem a uma fase posterior e não devem ser inferidas daqui.

## Resumo executivo

Esta nota levanta o que as fontes primárias estabelecem sobre dois assuntos e o que elas deixam sem responder. **Karpathy** descreve um padrão em que o LLM mantém incrementalmente uma wiki de Markdown sobre fontes cruas imutáveis, em três camadas (raw / wiki / schema) e três operações (Ingest / Query / Lint), lendo o índice antes de descer às páginas, e afirma que isso dispensa RAG por embeddings na escala de ~100 fontes e centenas de páginas (gist Karpathy). **OKF v0.2** é um formato de armazenamento para exatamente esse tipo de corpus: diretório de Markdown com YAML frontmatter, `type` como único campo obrigatório, e provenance/trust/lifecycle como famílias opcionais de frontmatter (`SPEC.md`). A **Anthropic** documenta o mecanismo de progressive disclosure em três níveis que faz uma skill custar pouco: só metadata pré-carregada, corpo ao disparar, arquivos auxiliares a custo zero até serem lidos (docs Anthropic). As duas fontes do enunciado não se conhecem: Karpathy não menciona OKF, e o OKF não prescreve nem oferece camada de busca. O que cada lacuna obriga a decidir está nas seções (d) e (e); **esta nota não decide nada disso.**

## (a) A tese de Karpathy

Fonte única desta seção: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (obtido integralmente; gist de revisão única, criado 2026-04-04).

Tese central: em vez de recuperar de documentos crus a cada query, o LLM "incrementally builds and maintains a persistent wiki"; "the wiki is a persistent, compounding artifact." O problema do RAG é que "the LLM is rediscovering knowledge from scratch on every question. There's no accumulation." E wikis humanos morrem pela manutenção: "The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping"; "Humans abandon wikis because the maintenance burden grows faster than the value."

Vocabulário e estrutura que o gist define:
- **Três camadas:** *raw sources* (imutáveis — "the LLM reads from them but never modifies them"); *the wiki* ("a directory of LLM-generated markdown files... The LLM owns this layer entirely"); *the schema* (um `CLAUDE.md`/`AGENTS.md` que ensina o LLM a manter a wiki — "what makes the LLM a disciplined wiki maintainer rather than a generic chatbot").
- **Operações Ingest / Query / Lint.** Lint = "health-check the wiki. Look for: contradictions between pages, stale claims ... orphan pages ... missing cross-references".
- **`index.md`** ("content-oriented ... a catalog of everything in the wiki") e **`log.md`** ("chronological ... append-only record"), com log parseável por unix (`grep "^## \[" log.md | tail -5`).
- Analogia: "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

Afirmações do gist sobre leitura, ingestão e busca:
- **Leitura em duas etapas:** "the LLM reads the index first to find relevant pages, then drills into them" — e isso "works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for embedding-based RAG infrastructure."
- **Cardinalidade fonte→página:** "A single source might touch 10-15 wiki pages."
- **Respostas viram páginas:** "good answers can be filed back into the wiki as new pages."
- **Busca local sem embeddings:** o gist aponta **qmd** — "a local search engine for markdown files with hybrid BM25/vector search and LLM re-ranking, all on-device. It has both a CLI ... and an MCP server" (https://github.com/tobi/qmd). Sobre frontmatter: "If your LLM adds YAML frontmatter to wiki pages (tags, dates, source counts), Dataview can generate dynamic tables and lists."
- **Wiki como repo git** ("version history, branching, and collaboration for free").

Evidência empírica de terceiros nos comentários (não do autor — verifiquei que nenhum comentário é do próprio Karpathy), registrando experiência de implementação:
- kriss-b: "the agent navigates with grep/sed/ls rather than embeddings — cheap, exact, and it doesn't go stale the way a vector index does" — https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6338122#gistcomment-6338122
- wy-cats: "Citations are links. Parsing [@citekey] into the same edge table as [[wikilink]] gave backlinks, the graph, pending-state and lint checks for free"; "'Pending ingest' is better as a computed state than a flag." — https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6362239#gistcomment-6362239
- ShootJackal/Cortex: "the production shortlist uses BM25 over full note text under explicit context budgets" (aposentaram o ranking sobre resumos de uma linha) — https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6365460#gistcomment-6365460

## (b) O formato OKF de fato

Fonte lida (repositório canônico): `git clone https://github.com/GoogleCloudPlatform/open-knowledge-format`, commit `ad30107c31c06aec8a7d5636e0d1058118604e6f` (data do commit `2026-08-21T13:08:36-07:00`). Licença Apache 2.0. Spec: OKF **v0.2** (`SPEC.md:3`, https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).

> O lar canônico do OKF é **`GoogleCloudPlatform/open-knowledge-format`** — os caminhos e URLs desta seção apontam para lá. Existe um snapshot congelado e não-mantido em `GoogleCloudPlatform/knowledge-catalog/okf/` cujo `SPEC.md` é byte-idêntico ao canônico (mesmo tamanho, `diff` zero); isso está registrado na seção (f), que não repito aqui.

O que é: "an open, human- and agent-friendly format for representing *knowledge*: the metadata, context, and curated insight that surrounds data and systems ... intentionally minimal: a directory of markdown files with YAML frontmatter. There is no schema registry, no central authority, and no required tooling" (`SPEC.md` §intro). Alvos: legível por humanos sem tooling, parseável por agentes sem SDK, diffável em VCS, portátil (§1). A tese da v0.2: como um corpus agora é "continuously written and maintained by agents", ela torna provenance, trust, freshness, lifecycle e attestation cidadãos de primeira classe no frontmatter (§1).

Estrutura de arquivos (`SPEC.md` §2, §3):
- Um **bundle** é uma árvore de diretórios de Markdown; a organização é livre (domain-independent).
- Um **concept** = um documento Markdown. O **concept id** = caminho dentro do bundle sem `.md`.
- **Arquivos reservados** (não podem ser concepts): `index.md` (listagem de diretório, §8) e `log.md` (histórico, §9). Todo outro `.md` é concept.
- Segmentos do concept-id são validados na implementação de referência contra `[A-Za-z0-9_][A-Za-z0-9_.\-]*` (`src/reference_agent/bundle/paths.py`, repo canônico). Nomes reais são slugs minúsculos (ex. `revenue-ytd.md`) — convenção, não regra do SPEC.
- Distribuível como repo git (recomendado), tarball/zip, ou subdiretório de um repo maior.

Corpo (`SPEC.md` §4.2): Markdown livre, preferindo estrutura. Cabeçalhos convencionais (não obrigatórios): `# Schema`, `# Examples`, `# Computation`. Atribuição por-alegação usa footnotes Markdown cujo label = um `sources[].id` (ex. `[^rev-policy]`), casados por chave e não por posição.

Cross-linking (`SPEC.md` §6): links Markdown normais; caminho absoluto bundle-relative (`/tables/customers.md`) recomendado sobre relativo. Links são arestas dirigidas sem tipo (a relação é dita na prosa). Consumidores DEVEM tolerar links quebrados (podem ser conhecimento ainda-não-escrito). `references/` é subdir convencional para espelhar material/código externo como concepts (§6.3).

`index.md` (§8) e `log.md` (§9): `index.md` sem frontmatter (exceto o do root, que PODE ter `okf_version`); corpo = seções de bullets `* [Title](url) - description`. `log.md` = lista agrupada por data, mais novo primeiro, cabeçalhos ISO `YYYY-MM-DD`. (Nota: o `bundles/acme_retail/log.md` real usa `type: Log` no frontmatter, excedendo levemente a descrição "sem frontmatter" do SPEC.)

Conformance (`SPEC.md` §11): um bundle é conforme se (1) todo `.md` não-reservado tem YAML frontmatter parseável, (2) cada um tem `type` não-vazio, (3) reservados seguem §8/§9. Consumidores NÃO PODEM rejeitar por: campo opcional ausente, `type` desconhecido, chave desconhecida, link quebrado, `index.md` ausente. Versionamento (§12): `okf_version: "0.2"` só no frontmatter do `index.md` do root. **Não existe JSON Schema nem validador standalone** — o SPEC em prosa é o artefato normativo. Há, porém, validação *em código* na implementação de referência: `REQUIRED_FRONTMATTER_KEYS = ("type",)` e `OKFDocument.validate()`, que levanta `OKFDocumentError` por chave obrigatória ausente, YAML inválido, frontmatter não-mapping ou bloco não terminado (`src/reference_agent/bundle/document.py:24,56-95`, repo canônico — verificado neste commit; ver seção (f)).

### Tabela de campos do frontmatter (OKF v0.2, `SPEC.md` §4.1, §5, §7, §10)

| Campo | Obrigatoriedade | Tipo / vocabulário | Nota |
|---|---|---|---|
| `type` | **REQUIRED** (o único sempre obrigatório) | string curta (ex. `Metric`, `Playbook`, `Reference`, `Attested Computation`) | não há registro central; consumidores toleram tipos desconhecidos |
| `title` | recomendado | string | — |
| `description` | recomendado | string (uma frase) | "Used by index.md generators, search snippets, and previews" (OKF README) |
| `resource` | recomendado | URI canônico do ativo | ausente em conceitos abstratos |
| `tags` | recomendado | lista de strings | — |
| `sources` | opcional (§5) | lista de `{resource*, id?, title?, author?, usage_count?, last_modified?}` | `resource` obrigatório dentro da entrada; `id` = chave estável p/ footnote; irmão `usage_window: {from,to}` |
| `generated` | opcional (§5) | `{ by*, at }` | `by` obrigatório (um actor); `at` = ISO 8601 UTC da última mudança relevante |
| `verified` | opcional (§5) | lista de `{ by, at }` | mapping avulso é tratado como lista de 1 elemento |
| `status` | opcional (§5.4) | `draft \| stable \| deprecated` | ausente ⇒ `stable` |
| `stale_after` | opcional (§5.5) | instante ISO 8601 | stale quando `now >= stale_after` |
| `runtime` | REQUIRED p/ `Attested Computation` (§10) | ex. `bigquery`, `dbt`, `python`, `postgres`, `Looker` | — |
| `parameters` | opcional (§10) | lista de `{name, type, required}` | — |
| `computation` | opcional (§10) | caminho p/ arquivo | senão o fence `# Computation` no corpo é autoritativo |
| `executor` | opcional (§10) | `{ resource, receipt: [...] }` | — |
| `attester` | opcional (§10) | `{ resource }` | — |

Convenção de **actor** (vocab controlado, §7): `<producer>/<version>` p/ agentes (ex. `reference_agent/gemini-2.5-pro`); `human:<id>`; `process:<id>`. **Trust tiers** derivados (não armazenados, §5.3): sem `verified` ⇒ *unverified*; `verified` só por não-`human:` ⇒ *machine-confirmed*; qualquer verificador `human:` ⇒ *human-reviewed*.

Timestamps: sempre ISO 8601 com offset UTC explícito (ex. `2026-06-30T14:00:00Z`).

### Exemplo real (verbatim, truncado)

Caminho: `bundles/acme_retail/computations/revenue-ytd.md` — https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/bundles/acme_retail/computations/revenue-ytd.md

```markdown
---
type: Attested Computation
title: Revenue for a fiscal year
description: Sanctioned SQL that produces the recognized-revenue figure for a given fiscal year, per Acme's FY2026 Revenue Recognition Policy.
tags: [finance, revenue, attested]
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: attesters/sql_equality.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-30T14:00:00Z }
verified:
  - { by: human:jsmith@acme, at: 2026-07-01T09:00:00Z }
status: stable
stale_after: 2026-12-31T00:00:00Z
sources:
  - id: revenue-policy
    resource: policies/revenue-recognition.md
    title: Revenue Recognition Policy (FY2026)
    author: human:jsmith@acme
    last_modified: 2026-06-15T00:00:00Z
  - id: orders-table
    resource: tables/orders.md
    title: Customer Orders (BigQuery table)
    author: team:data-platform
    last_modified: 2026-07-01T00:00:00Z
---

# Computation

```sql
SELECT SUM(...) AS revenue_usd
FROM `acme.sales.orders` AS o
WHERE o.order_status = 'delivered'
  AND EXTRACT(YEAR FROM o.order_ts) = @year
```

This computation implements the four rules of the FY2026 Revenue Recognition Policy: [^revenue-policy]
[^revenue-policy]: Revenue Recognition Policy (FY2026)
```
(SQL truncado; texto completo no arquivo. Note que os `resource` aqui usam caminho bundle-relative *sem* `/` inicial — o SPEC recomenda `/`-rooted mas permite relativo.) Bundles prontos em `bundles/`: `ga4/`, `stackoverflow/`, `crypto_bitcoin/`, `acme_retail/` (este é o mais rico; exercita Attested Computations). O Appendix A do SPEC traz uma migração v0.1→v0.2 completa.

**`samples/` vs `bundles/` (repo canônico, ausente do snapshot).** São coisas distintas: `samples/<name>/` é a *receita* — só `README.md` + `seeds.txt` (verificado em `samples/ga4_merch_store/`, que contém exatamente esses dois arquivos); `bundles/<name>/` é o *resultado* — a árvore OKF já enriquecida, com `index.md` por nível e `viz.html`. Há assimetria: o sample `ga4_merch_store` corresponde ao bundle `ga4`, e `bundles/acme_retail` **não tem** sample correspondente (`ls samples/` = `crypto_bitcoin ga4_merch_store stackoverflow`; `ls bundles/` = `acme_retail crypto_bitcoin ga4 stackoverflow`) — o motivo de `acme_retail` não ter receita não está documentado (ver seção (e)).

Tooling no repo (não faz parte do formato): o **reference agent** Python (`src/reference_agent/`, entry point `reference-agent = "reference_agent.cli:main"` em `pyproject.toml`) é um produtor declaradamente proof-of-concept (`README.md:22`). A CLI tem dois subcomandos, via `argparse` (`src/reference_agent/cli.py:77,159`):
- **`enrich`** — "Enrich concepts from a source into an OKF bundle". Flags principais (`cli.py:80-157`): `--source` (**required**, `choices=_SOURCES`), `--dataset`, `--billing-project`, `--out` (**required**), `--concept` (repetível), `--model` (default `gemini-flash-latest`), o bloco `--web-seed`/`--web-seed-file`/`--web-max-pages` (default 100)/`--web-allowed-host`/`--web-allowed-path-prefix`/`--web-denied-path-substring`/`--web-max-depth` (default 2), e `--no-web`.
- **`visualize`** — "Generate a self-contained HTML graph view of an OKF bundle"; flags `--bundle` (**required**), `--out` (default `<bundle>/viz.html`), `--name`; chama `generate_visualization` (`cli.py:159-190`).

**Que fontes o ferramental ingere hoje (responde à pergunta de fundo).** Só **uma**: `_SOURCES = ("bq",)` (`cli.py:28`); passar outro valor cai em `SystemExit` no `_build_source` (`cli.py:31-38`). A única implementação concreta da interface `Source` é `BigQuerySource` (`src/reference_agent/sources/bigquery.py:43`) — não há adaptador de arquivos locais, texto, PDF, Markdown ou código-fonte. A interface `Source` (`src/reference_agent/sources/base.py:34`) obriga `list_concepts()` e `read_concept()` (metadados estruturados por conceito) e oferece `sample_rows()` opcional (default `None`); modela **catálogo de metadados**, não conteúdo bruto de arquivo. Sobre o passe web: `fetch_and_parse` (`web/fetcher.py:76`) **rejeita content-type não-HTML** (`web/fetcher.py:87`, `raise FetchError("non-HTML content-type: ...")`) e converte HTML→markdown com `markdownify` truncando em 40 KiB (`web/fetcher.py:99-100`, `_MAX_MARKDOWN_BYTES = 40 * 1024` em `:25`) — logo PDF/JSON não entram. **Conclusão factual:** hoje o ferramental ingere apenas metadados **BigQuery** + um passe **web HTML**; não ingere texto/PDF/md-local/código.

**Geração de `index.md` é código real, não só descrição do SPEC.** `regenerate_indexes(bundle_root, model, synthesize)` (`bundle/index.py:63`) percorre o bundle e escreve um `index.md` por diretório; descrições de diretório vêm de `synthesize_description` (`bundle/synthesizer.py:38`), que instancia `genai.Client()` do Gemini com fallback textual em exceção (`synthesizer.py:60-66`); `index.md` é reservado e nunca vira conceito (`index.py:85`).

**Amarração a Google Cloud/Gemini está no ferramental, não no formato.** As dependências (`pyproject.toml`) são `google-adk>=2.0`, `google-cloud-bigquery>=3.20`, `pyyaml>=6.0`, `pydantic>=2.0`, `markdownify>=0.11`; `DEFAULT_MODEL = "gemini-flash-latest"` (`agent.py:30`); `generated.by` default é `reference_agent/<model>`. O `README.md:8-9` afirma que o **formato** é "universal, vendor-neutral ... not tied to any" agente/framework/modelo/serving, enquanto o agente e o viewer são rotulados "proof of concept" (`README.md:22,165-166`). O que os testes garantem sobre a implementação está na seção (f).

**Connector.** `connectors/gcp-knowledge-catalog.md` (presente só no repo canônico) documenta um round-trip de bundle OKF para o Google Cloud Knowledge Catalog via `kcmd`, ferramenta que vive no **outro** repo (`toolbox/mdcode` de `knowledge-catalog`, não neste). Limitações declaradas (`connectors/gcp-knowledge-catalog.md:114+`): só 7 chaves de frontmatter são carregadas; **só arquivos `.md`** (imagens/HTML/CSV ignorados); cross-links relativos são gravados verbatim e "resolve to nothing"; renomes órfãos e deletes deixam entradas para trás, "no merge story"; sem access control por entrada; escala "untested beyond the 14-file demo".

## (c) O mecanismo de progressive disclosure

O mecanismo canônico é o dos Agent Skills da Anthropic, em três níveis carregados em momentos distintos:
- **Nível 1 — Metadata (sempre carregado):** só o YAML frontmatter (`name` + `description`), ~100 tokens por skill; "until a Skill is triggered, only its name and description occupy context." — https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview
- **Nível 2 — Instructions (ao disparar):** o corpo do SKILL.md (< 5k tokens) só entra quando a `description` casa; lido via bash sob demanda. — mesma fonte.
- **Nível 3 — Resources/code (sob demanda):** arquivos auxiliares custam zero tokens até serem lidos; scripts rodam via bash e só a saída entra no contexto ("The rest stay on the filesystem and cost zero tokens"). — mesma fonte.

Regras de redação (https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices): `description` em terceira pessoa, específica, com termos-gatilho (o quê + quando); corpo < 500 linhas; **referências a no máximo um nível de profundidade** a partir do SKILL.md (senão o agente faz leituras parciais tipo `head -100` e pega info incompleta); arquivos de referência > 100 linhas devem ter ToC no topo; `grep` sobre referências é o padrão de busca barata mostrado ("`grep -i "revenue" reference/finance.md`"). Requisitos de campo (overview): `name` ≤64 chars (minúsculas/dígitos/hífens); `description` não-vazia, ≤1024 chars, sem XML.

O OKF descreve o mesmo mecanismo aplicado a uma wiki de arquivos: "use frontmatter for the few fields you want to query, filter, or index on (`type`, `resource`, `tags`, `generated`, `status`); use the markdown body for the prose, schemas, and example queries" e "**Progressive disclosure built in.** Auto-generated `index.md` files let an agent or human navigate the hierarchy one level at a time instead of loading the entire bundle into context." — OKF README, https://github.com/GoogleCloudPlatform/open-knowledge-format. O SPEC ainda diz que um consumidor "can synthesize [a view] at consumption time by scanning frontmatter" (§8, §3.1) — isto é, um índice derivado do frontmatter não viola conformidade.

Padrão empírico neste repositório (medido em 37 SKILL.md sob `/home/lucas/projects/llm-wiki/.agents/skills/`):
- Tamanho da linha `description:`: mín. 49 bytes (`implement-spec/SKILL.md`), mediana ~130, máx. 434 (`code-review/SKILL.md`) — todas bem abaixo do teto de 1024. O índice sempre-carregado por item é pequeno na prática.
- Formato "faz X. Use when <gatilhos>" — ex. `code-review/SKILL.md`, `diagnosing-bugs/SKILL.md`, `research/SKILL.md`.
- Referências a um nível por link Markdown relativo — ex. `codebase-design/SKILL.md:113-114` → `DEEPENING.md`/`DESIGN-IT-TWICE.md`; `tdd/SKILL.md:16` → `tests.md`/`mocking.md`; scripts Nível 3 como `git-guardrails-claude-code/scripts/block-dangerous-git.sh`.
- `writing-for-agents/SKILL.md` (deste repo) teoriza o mecanismo com vocabulário útil: **"context pointer"** (a `description` é um; a *redação* do ponteiro, não o alvo, decide quando/quão confiável o material é alcançado) e "Progressive disclosure is the move down the ladder ... loaded only when the pointer fires."

### O que as fontes estabelecem sobre um índice de frontmatter

Sem propor implementação, é isto que já está dito nas fontes e que qualquer desenho terá de levar em conta:
- **É possível separar metadata de corpo na leitura:** o frontmatter é um bloco YAML delimitado no topo do arquivo, e a implementação de referência do OKF o parseia parando no segundo `---` sem consumir o corpo (`OKFDocument.parse`, `src/reference_agent/bundle/document.py:56-79`).
- **O OKF já divide os campos por finalidade:** "use frontmatter for the few fields you want to query, filter, or index on (`type`, `resource`, `tags`, `generated`, `status`); use the markdown body for the prose, schemas, and example queries" (OKF README).
- **O SPEC autoriza sintetizar views ao consumir:** um consumidor "can synthesize [a view] at consumption time by scanning frontmatter" (`SPEC.md` §8, §3.1) — ou seja, um índice derivado não viola conformidade.
- **`description` é consumida verbatim por geradores de índice:** "This is used verbatim in auto-generated `index.md` files, so keep it tight and informative" (`prompts/reference_instruction.md`, seção Frontmatter).
- **`status` e `stale_after` são os campos de ciclo de vida disponíveis para filtrar,** com `status` ausente ⇒ `stable` e stale quando `now >= stale_after` (`SPEC.md` §5.4, §5.5).
- **Trust tier não é armazenado, é derivado** de `verified` (`SPEC.md` §5.3) — qualquer filtro por confiança é computado, não lido.

Nenhuma fonte especifica a forma das tools de busca; ver seção (e) e a evidência negativa na seção (f).

Uma observação documentada que vale registrar sobre a redação da metadata, já que é ela que decide se um item é encontrável a baixo custo: a doc da Anthropic exige `description` em terceira pessoa, específica, contendo o quê **e** quando usar, com termos-gatilho (best-practices), e `writing-for-agents/SKILL.md` (deste repo) sustenta que é a *redação do ponteiro*, não o alvo, que determina se e quando o material é alcançado.

## (d) O que o OKF deixa sem especificar

Áreas que o próprio SPEC/README declara fora de escopo ou deixa livres (`SPEC.md` §1 non-goals, §11, §12). Ficam registradas como pontos em aberto, sem decisão tomada aqui:
- **Slug/nomeação de arquivos:** o SPEC só define concept-id = caminho − `.md`; a impl de referência restringe o charset de segmento a `[A-Za-z0-9_.\-]`. Não há esquema de slug prescrito para entradas heterogêneas (PDFs, código).
- **Derivação de conteúdo:** como transformar PDF/código/texto em concept, chunking, e onde ficam as fronteiras de "um concept por arquivo" — não especificado. (Karpathy só observa a cardinalidade: uma fonte toca ~10-15 páginas.)
- **Vocabulário de `type`:** freeform, sem registro central; consumidores toleram tipos desconhecidos.
- **Índice/busca:** `index.md` serve a progressive disclosure, não a query. O SPEC autoriza sintetizar views ao consumir, mas não define índice nem interface de busca. Confirmado por evidência negativa no repo canônico: `grep -riE 'embedding|bm25|vector|semantic|full-text|inverted index|faiss|elasticsearch'` nas fontes retorna zero; "retrieval" aparece uma vez no SPEC (`SPEC.md:213`) como *design rationale*, "search index" na SPEC é consumidor hipotético, e a única "search box" real é filtro client-side no `viz.html` (ver seção (f)).
- **Protocolo de runtime / Attested Computations:** receipt/verdict wire formats, ABI/sandbox do attester, cache de atestação, templates de semantic-layer — todos "considered and deferred" (§12).
- **Empacotamento de executor/attester:** o SPEC "fixes the interface, not the packaging".
- **Validação:** não há JSON Schema nem validador standalone; o §11 enuncia 3 regras de conformidade em prosa, e a impl de referência checa apenas `type` (ver (b) e (f)).

Pontos que os comentários do gist levantam e que também seguem em aberto: se `[[wikilinks]]` e citações devem cair na mesma tabela de arestas; se "pending ingest" é estado computado ou flag; se o shortlist deve rodar BM25 sobre corpo completo ou sobre resumos curtos — os três aparecem como relato de experiência de terceiros na seção (a), não como recomendação de fonte primária.

## (e) Lacunas e perguntas abertas — não verificado em fonte primária

- ~~**SPEC canônico atual do OKF**~~ — **LACUNA FECHADA.** Ver seção (f): o `SPEC.md` do repo canônico é byte-idêntico ao do snapshot. Nenhuma divergência de formato.
- **Karpathy não menciona OKF.** O gist não cita "OKF" nem o repo do Google; a ponte entre as duas fontes é do enunciado, não do texto de Karpathy. Não há endosso do autor a nenhuma implementação de terceiros (qmd é mencionado no texto, mas não como endosso a implementações externas).
- **Nenhuma fonte prescreve uma interface de busca** — a Anthropic descreve *comportamento* (o agente usa `bash`/`grep`/`cat`), não uma API; o OKF explicitamente NÃO prescreve infraestrutura de serving/query (§1 non-goals) e não traz tool de leitura (seção (f)). Qualquer forma de tool é decisão de projeto, fora do escopo desta nota.
- **Eficácia de recuperação não medida:** que descrições curtas melhoram seleção é apoiado pela doc Anthropic + padrão empírico do repo, mas não medimos taxa de acerto.
- ~~**Não inspecionamos em detalhe o código do reference agent**~~ — **em grande parte fechada.** As seções (b) e (f) documentam CLI, `sources/`, `bundle/`, `web/`, `viewer/`, `tests/`, prompts e `pyproject.toml` do repo canônico, com citações `caminho:linha`.
- **Vitalidade/cadência não aferível pelo conteúdo:** o repo canônico tem 6 commits (2026-08-14 a 2026-08-21, ~7 dias), autor único (Amir Hormati), sem tags, sem releases, sem CI (`git log --oneline`, `git tag` vazio no clone de `ad30107`). "Vivo/estável" não pode ser afirmado além de "SPEC v0.2, HEAD 2026-08-21, agente/viewer rotulados proof-of-concept"; se houve atividade posterior à data deste clone, não foi verificado.
- **Issues/PRs abertos no GitHub não consultados:** não usei a API/web do GitHub; o estado da discussão viva (issues abertas, PRs pendentes) fica em aberto.
- **Estado atual de `knowledge-catalog/toolbox/mdcode`** (onde vive o `kcmd` que o connector usa) não foi inspeccionado neste ciclo.
- **Por que `bundles/acme_retail` não tem sample correspondente** em `samples/` não está documentado no repo.
- **Suíte de testes não executada:** as invariantes na seção (f) foram lidas do texto dos testes, não de uma execução (dependências `google-adk`/`google-cloud-bigquery`/`markdownify` não instaladas).

## (f) Verificação do repo canônico e a superfície real de tools do OKF

Adendo apurado diretamente no repo canônico, após a pesquisa inicial. Fonte: `git clone --depth 1 https://github.com/GoogleCloudPlatform/open-knowledge-format`, commit `ad30107c31c06aec8a7d5636e0d1058118604e6f` (data do commit `2026-08-21T13:08:36-07:00`).

**O formato não divergiu.** Snapshot (`knowledge-catalog/okf/SPEC.md`, commit `1f20c1a`) e canônico (`open-knowledge-format/SPEC.md`, commit `ad30107`) têm 1006 linhas cada e `diff -u` retorna **zero** linhas alteradas — byte-idênticos, ambos "**Version 0.2**" (SPEC.md:3). Logo, tudo na seção (b) vale para o formato canônico. O repo canônico tem, porém, conteúdo extra ausente do snapshot: `connectors/gcp-knowledge-catalog.md`, `samples/` (`crypto_bitcoin`, `ga4_merch_store`, `stackoverflow`), `tests/` e `pyproject.toml` com entry point `reference-agent = "reference_agent.cli:main"`.

**Governança e vitalidade (fatos observáveis).** Licença Apache 2.0 (Google LLC 2026). `CONTRIBUTING.md` define **duas trilhas de revisão**: mudanças no formato (`SPEC.md`) são "held to a higher bar" e exigem abrir uma issue antes do PR; contribuições de tooling/samples seguem PR normal; **todo submission exige review** e **CLA obrigatório** (`CONTRIBUTING.md:5-10,31-40`). Não há `GOVERNANCE.md` nem processo de RFC formal. Histórico: 6 commits entre 2026-08-14 e 2026-08-21, autor único (Amir Hormati), sem tags/releases (`git log`, `git tag` no clone de `ad30107`) — a cadência de longo prazo não é aferível daqui (ver seção (e)). O `README.md` rotula agente e viewer como "proof of concept" (`README.md:22,165-166`) e o formato como "universal, vendor-neutral" (`README.md:8-9`).

**O OKF não oferece nenhuma tool de busca — só de escrita/ingestão.** A superfície LLM-facing completa do reference agent, enumerada por `grep -hnE "^def " src/reference_agent/tools/*.py`, é:

| Tool | Arquivo | Papel |
|---|---|---|
| `read_existing_doc(concept_id)` | `tools/bundle_tools.py:87` | lê doc existente antes de escrever; retorna `{frontmatter, body}` ou `None` |
| `write_concept_doc(concept_id, frontmatter, body)` | `tools/bundle_tools.py:104` | única forma de persistir; retorna `{path, bytes}` |
| `list_concepts()` | `tools/source_tools.py:32` | lista concepts do bundle (usada para cross-linking) |
| `read_concept_raw(concept_id)` | `tools/source_tools.py:44` | metadados estruturados da fonte crua |
| `sample_rows(concept_id, n=5)` | `tools/source_tools.py:59` | amostra de dados quando o metadado é escasso |
| `fetch_url(url)` | `tools/web_tools.py:24` | busca web sob allowlist (`WebState.allowed_hosts`, `max_pages`, `max_depth`) |

Isso **confirma como fato** o que a seção (c) tratava como lacuna: a metade de *leitura barata* (índice de frontmatter, busca, backlinks) não existe no OKF nem é prescrita por ele. É evidência negativa útil — não há interface upstream com a qual se conformar. A única "busca" no repo é client-side e puramente visual: o `viz.html` gerado carrega o grafo inteiro no navegador e a caixa de busca só faz *dim* de nós cujo `label`+`id`+`tags` não contêm a query (`viewer/static/viz.js`), com backlinks montados em JS no navegador (`viewer/static/viz.js`); não é índice/busca server-side. O `viz.html` "auto-contido" ainda depende de rede em runtime, puxando `cytoscape@3.28.1` e `marked@12.0.0` do CDN jsdelivr (`viewer/templates/viz.html`). Não há lint nem detector de órfãos em Python — esses termos aparecem só na nota do Karpathy (seção (a)), não neste repo.

**Padrões observados no código** (`tools/bundle_tools.py`), registrados como fato sobre a implementação de referência:
- **`generated` é preenchido pela tool, não pelo LLM:** o default é `{by: reference_agent/<model>, at: <now UTC, timespec=seconds>}` (linhas ~170-180).
- **Ordenação determinística de frontmatter:** `_reorder_frontmatter` aplica `_PREFERRED_KEY_ORDER` antes de serializar (`bundle_tools.py:76`).
- **Erro-como-instrução:** falhas retornam `{"error": ...}` dizendo ao agente como recuperar ("Re-call `write_concept_doc` with the complete frontmatter dict"), em vez de lançar exceção.
- **Augmentation guard:** no passe web, a escrita é recusada se o novo `# Schema` perder campos que o passe anterior populou a partir de metadados reais; a mensagem lista os campos faltantes (até 10). O comentário no código enuncia a regra: "The BQ pass populates these from real metadata; the web pass must augment, not replace."
- **Uma invocação = um concept:** "Each invocation enriches exactly **one** concept and finishes by calling `write_concept_doc` exactly once" (`prompts/reference_instruction.md:1-3`).

**A "camada schema" do Karpathy tem um análogo concreto no OKF, em forma de prompt.** `src/reference_agent/prompts/reference_instruction.md` (106 linhas) e `web_ingestion_instruction.md` (269 linhas) cumprem o papel do `AGENTS.md`/skill: workflow numerado de 5 passos, campo-por-campo do frontmatter, ordem obrigatória das seções do corpo (prosa → `# Schema` → `# Common query patterns`), regras de atribuição por footnote, regras de cross-linking e regras de estilo ("Do not invent fields, partitions, or shard counts that are not in the raw metadata"). Licença Apache 2.0.

**O prompt de ingestão web codifica a decisão criar-vs-atualizar.** `src/reference_agent/prompts/web_ingestion_instruction.md` (269 linhas) instrui o agente ADK a, por página, escolher entre (a) enriquecer concept existente, (b) *mint* uma reference nova sob `references/<slug>`, ou (c) *skip* — "when in doubt, skip". *Mint* só passa se satisfizer quatro gates (topic shape; não ser meta bundle-level como overview/quickstart/changelog; passar no "citation test"; passar no "reuse test"). Regras de augmentação não-negociáveis: `write_concept_doc` é *full replacement*, então o frontmatter novo deve conter todas as chaves do existente, com `type`/`title`/`resource` copiados verbatim (a URL vai em `sources`, nunca em `resource`), e `tags`/`sources` são **união**; no corpo, toda heading `#` existente deve reaparecer na mesma ordem, proibido dropar/renomear heading ou encolher o `# Schema` populado no passe BQ. Extrações concept-shaped são obrigatórias: métricas viram `references/metrics/<slug>.md` com SQL concreto e citação de volta numa seção `# Metrics` das tabelas contribuintes; join paths viram `references/joins/<a>__<b>.md`; "orphan é bug, não deliverable". Só registrar em `sources` URLs realmente fetched ("Do not invent URLs").

**O que os testes garantem (`tests/`, lidos, não executados — ver (e)).** `pyproject.toml` fixa `testpaths=["tests"]`, `pythonpath=["src"]`. Invariantes extraídas do texto: em `test_document.py` — round-trip preserva frontmatter+body, `validate()` rejeita ausência de `type` e aceita só `type`, `is_stale` só dispara com datetime ISO **com offset** (date-only/sem-offset são ignorados); em `test_bundle_tools.py` — no passe web recusa encolher `# Schema` de `BigQuery Table` e recusa encolher `sources`, mas augmentar com nova seção `# Metrics` passa, e fora do passe web encolher schema é permitido; em `test_web_tools.py` — allowlist/prefixo/substring/`max_depth` cortam, e URL não retornada por nenhuma página é rejeitada ("not reachable from a seed"); em `test_web_fetcher.py` — rejeita não-HTML, trunca ~40 KB, descarta `mailto:`/`javascript:`; em `test_viewer.py` — `index.md` não vira nó, cross-links viram arestas dirigidas, alvo inexistente é ignorado; em `test_bigquery_source.py` — tabelas shardadas colapsam num conceito wildcard e `sample_rows` usa `list_rows` (TABLE) ou `query ... LIMIT n` (VIEW).

**Conflito SPEC × implementação de referência.** Sobre a forma dos links entre concepts as duas fontes discordam, e o conflito é real, não aparente:
- SPEC §6 recomenda caminho absoluto bundle-relative, iniciado por `/` (ex. `/tables/customers.md`).
- O prompt do reference agent proíbe exatamente isso: "Use file-relative paths only. **Never start a link with `/` (that breaks GitHub rendering)**", e manda usar caminhos relativos ao diretório do doc (`[users](users.md)`, `[dataset](../datasets/<slug>.md)`) — `prompts/reference_instruction.md`, seção "Cross-linking".

O exemplo real do `revenue-ytd.md` citado em (b) usa caminho sem `/` inicial, isto é, segue o prompt e não o SPEC. Fica registrado como divergência a resolver, sem escolha feita aqui.
