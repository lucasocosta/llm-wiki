# Ticket 10: Protocolo de evidência do worker (anti modo de falha RAG)

Type: task
Status: resolved
Blocked by: 06

## Contexto

Na avaliação da busca (sessão 2026-09-12) ficou demonstrado o modo de falha clássico
de RAG: pergunta por paráfrase ("pesquisa") desliza o ranking para páginas adjacentes
(`recuperar informação` → CSCW em vez de `wiki-busca-links`) e uma resposta errada
pode sair com confiança alta. As defesas hoje são disciplina do executor (ler os
vencedores inteiros, qualificar com `stale`), mas nada sistémico obriga a cadeia de
evidência — nem impede resposta "plausível" sem página de suporte.

## Trabalho

1. Na skill (`skill/SKILL.md`), definir protocolo de evidência: toda resposta fática
   cita os `read-page` consultados; zero página relevante → responder
   explicitamente "a wiki não responde isso" com os termos tentados (nada é
   preferível a adjacente). Considerado step explícito de autoverificação:
   os termos da resposta aparecem no texto citado.
2. Avaliar suporte da ferramenta: p. ex. `search` poderia devolver `no_results: true`
   de forma distint a (hoje: lista vazia) para o worker distinguir "nada casa" de
   "fui eu que não entendi".
3. Testes: (a) skill menciona o protocolo e o caso "não respondo"; (b) se item 2
   implementado, cli robusto da flag com fixture de disappea; (c) nenhum JSON
   abrangente modifica o payload atual sem opçao.

## Done

- O fluxo de consulta tem resposta honesta por construção ("não sei" é uma saída
  normal) e um protocolo de evidência na skill, não só boa vontade do modelo.

## Answer

Implementado o protocolo na skill: nova seção "Evidence protocol (ask the wiki
like a curator, not a retriever)" — (1) toda resposta fática cita os `read-page`
usados, sem página não há afirmação; (2) resultado vazio/vagamente casado é
resposta ("a wiki não responde isso"), com os termos tentados e sugestão de
termo real do material; (3) ler vencedores inteiros, nunca responder por
metadata/snippet; (4) qualificar sempre com `stale`/proveniência. O
`no_results` tool-side ficou de fora do payload (opção quatro (c) do ticket:
nenhuma mudança de shape sem flag); `--suggest` (ticket 11) cobre o item 2.
Cobertura: suite de consulta existente; texto verificado na skill

(*) Limitação declarada: o protocolo é disciplina da skill, não mecanismo
de enforcement — o enforcement dependeria de um runtime do agente (assim
como tokens reais).
