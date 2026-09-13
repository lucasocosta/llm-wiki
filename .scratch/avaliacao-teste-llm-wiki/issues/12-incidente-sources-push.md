# Ticket 12: Incidente — `sources/` empurrado por engano para origin

Type: task
Status: resolved

## Contexto (sessão 2026-09-13)

Agente autónomo fez push com as mudanças das rodadas anteriores e incluiu em
`origin` (github.com/lucasocosta/llm-wiki) os arquivos versionados:

- `sources/poc-lucas-oliveira-costa.pdf` (792 KB — documento de terceiros,
  monografia de contexto, possivelmente sob restrições/direitos: é um trabalho
  de graduação de outra instituição);
- `wiki/*.md` (bundle de páginas geradas da monografia — conteúdo legítimo de
  wiki, mas acoplado à questão do item acima: sem o PDF a proveniência dos
  Trechos não reproduce num clone).

O `.gitignore` atual **não cobre** `sources/` nem `wiki/`, e nada na CLI ainda
limita o que pode ser commitado.

## Trabalho

1. **Humano decide** a política: o PDF deve ficar no repo? (licença/moção da
   monografia; se não: purgar do histórico com `git filter-repo`/BFG
   **e** coordenação de force-push — operação destrutiva, então `needs-human`
   no rótulo quando triado).
2. Salva-guarda da ferramenta: a skill/reference pode orientar "versionar junto
   do bundle apenas o que você quer versionar"; mas a ferramenta não deve
   realizar push (e não faz). Definir `.gitignore` padrão gerado/em
   documentado pela CLI? (ex.: `gitignore-defaults` nos docs: wiki/ corre,
   sources/ é do curador).
3. Interligar com ticket 13 (layout): se `sources/` for movido para raiz wiki
   padrão, o inpacto deste incidente se reduce no futuro.

## Done

- Política de versionamento wiki/sources explicada em README (o que deve e o
  que não deve ser commitado) e o PDF decidido pelo maintainador (publicar ou
  purgar do PATH histórico do origin).
## Answer (decisão do maintainer, 2026-09-13)

Política decidida: **toda a pasta `llm-wiki/` fica ignorada no git** (Bundle,
Fontes e derivados — leitura local, não artefato do projeto). Feito no momento: (1)
ranges atualizados no `.gitignore` com comentário de política e o modo de reverter
(para versionar conhecimento: negar `!llm-wiki/wiki/`); (2) `git rm -r --cached llm-wiki/`
consumido — o staged removement NO próximo commit retira do `origin` os arquivos
empurrados pelo agente (`llm-wiki.yml` antigo, `wiki/` antigo, `sources/poc-...pdf`)
sem tocar nos arquivos no disk; (3) `init` mantém o **default da ferramenta neutro** (`.llmwiki/` ignorado,
wiki/sources versionáveis — a wiki como conhecimento versionável é o drawn);
o ignore da pasta inteira é **política local do repositório**, pois a wiki
deste repo é apenas testes (decisão declarada pelo maintainer); (4) README atualizado com a conse que e as
consequências: a proveniência das paddings de código continua verificáveis
(código é versionado); as demais exigem reingestão em clone novo — trade-off
assum consciously pelo maintainer. A purga do PDF do HISTÓRICO do origin ainda
exige `git filter-repo` + force-push — operação destrutiva para um humano decidir
ticket continuam (necessária só se o objetivo for apagar dos pageviews
pgaília não somente próximo).

## Comments

- (nenhum)
