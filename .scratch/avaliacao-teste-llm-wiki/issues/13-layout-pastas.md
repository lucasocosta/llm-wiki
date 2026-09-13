# Ticket 13: Padronização de layout — tudo da wiki em uma pasta?

Type: task
Status: resolved
Related: 12

## Contexto (sessão 2026-09-13)

Proposta: `sources/` e `wiki/` deveriam morar dentro de `.llmwiki/` para "não ter
nada fora dessa pasta" (padronização). A intenção é legítima (um lugar só, commits
acidentais menos prováveis), mas entra em conflito com um invariante do desenho
atual **explícito no `.gitignore`**: `.llmwiki/` é estado *derivado sem versionamento*
(índice de máquina, `usage.jsonl` — "reconstrutível a partir das páginas"). O
README diz o oposto para knowledge base: "versione-a no manifesto junto do Bundle
e das Fontes" — a proveniência (hashes/SHA) só reproduce num clone se Fontes e
Bundle estiverem versionados.

## Perguntas para grilling (sem resposta ainda)

1. **O que fica versionado?** Se .llmwiki inteiro for a pasta wiki, o que ancorar
   no `.gitignore`? `!  .llmwiki/wiki` + `! .llmwiki/sources` (exceções, risco de
   semântica confusa) ou revogação da regra " .llmwiki = derivado"?
2. **Fonte de código externa**: por decisão do ticket 08, código pinado é lido
   in-place do checkout — não pode ser copiado para dentro de `.llmwiki/`. O
   layout padrão então **não** engloba todas as Fontes? Como fica a promessa
   "nada fora da pasta"?
3. **Compatibilidade**: mudança de default quebra manifestos existentes
   (`llm-wiki.yml` na raiz? Para dentro de .llmwiki também? Caminhos no
   `source_versions` mudam — Precisava de migração de bundle).
4. **Alternativa a gravação**: manter `wiki/` + `sources/` na raiz mas documentar
   o layout padrão e fornecer mínima ajuda da CLI (ex.: `llm-wiki init` gerando
   `llm-wiki.yml` + `.gitignore` coerente — `sources/` do curador, wiki versionada).
   Padronizar sem mover diretórios.

## Trabalho (após decisão grill)

1. ADR nova substituindo/extinguindo o que determina os caminhos (spec/tickets
   01–02 do tracker original, `docs/adr/`).
2. Implementar o layout decidido: defaults do manifest, `_index_dir` (hoje
   `.llmwiki` no pai do bundle — cuidadoso, colisão de nomes se wiki muda),
   `code_base_path`, referências (Espelhos guardam `path:` relativo), .gitignore
   documentado, migração (ou break documentado).
3. Testes de regressão de paths (fixtures usam bundle_dir/sources_dir
   configuráveis — os defaults são testados em vários lugares).

## Done

- Decisão de layout ADR-ada (com discussão dos dois lados, incluindo o conflito
  com o `.gitignore` atual), implementada com migração ou opt-in, e testes
  cobrindo os novos caminhos padrão.
**Atualização pós-decisão (mesma sessão):** o maintainer pediu mais autocontimento:
o manifesto também mergulhou — `llm-wiki/{llm-wiki.yml, wiki/, sources/, .llmwiki/}`.
Contrato da CLI mantido (`-C llm-wiki`); `location` de Fonte code da própria repo
virou `../src/llmwiki` (relativo à raiz do manifesto); `.llmwiki` continuou na pasta
llm-wiki (padrão de derivado). Trade-offs registrados: (a) telemetria usage.jsonl
antiga se perdeu no viato da mudança (a CLI não Anglicana migrinie log — ** alimenta
** o item do ticket 14 sobre migração); (b) re-carimbo exigido para 24 páginas
(paths de proveniência remapeados ao root novo) — feito com os Trechos do próprio
frontmatter, determinístico; (c) fixture/testes em layouts planos continuam passando
(137). `stale []`, `broken-links []` com -C llm-wiki.

## Answer (decisão do maintainer, 2026-09-13)

Decidido no conversado: **`llm-wiki/{wiki,sources}` na raiz, `.llmwiki/` intocada**
(derivada, ignorada). Resolvido para este repo: (1) `git mv wiki sources →
llm-wiki/`; (2) `llm-wiki.yml` apontando bundle_dir/sources_dir para os novos
caminhos; (3) **bug corrigido de passagem**: `_index_dir` deduzia a raiz como
pai do Bundle — com nesting, o índice teria ido para `llm-wiki/.llmwiki`
(colisão confirmada em produção antes do fix). Agora sobe a árvore até achar o
`llm-wiki.yml`; fallback mantém o comportamento antigo. (4) `usage` unificado
em torno da raiz da CLI (report sumarizava pelo pai do bundle — mismatch corr
igido). (5) `unverifiable/stale` das 21 páginas curado por re-carimbo determin
ístico após o movimento (proveniência ficaria `unverifiable` até commit — como
desenhado; confirmado no commit subsequente do outro agente: `stale []`,
`unverifiable []` antes deste turno). (6) Teste novo
`test_nested_layout_index_lives_beside_manifest` (136 total passed).

O que **não** foi feito aqui (peça separada): comando `llm-wiki init` gerando
manifesto + .gitignore e migração geral de manifestos antigos (ticket 14).

## Comments

- 2026-09-13: aberto pela motivação do incidente 12 (commit acidental incluiu
  sources/wi a origem). Necessária grilling do maintainer antes da execução:
  a resposta honesta da sessão foi que mover wiki/ para .llmwiki/ conflita com o
  invariante " .llmwiki = derivado não-versionado" — opção 4 do grilling
  (documentar layout + `llm-wiki init` + .gitignore padrão) preserva os dois
  invariantes sem dir surgery.
