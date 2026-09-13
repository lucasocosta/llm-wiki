# Ticket 08: Location de Fonte de código aceitar caminho repo-relativo/absoluto

Type: task
Status: resolved
Blocked by: 01

## Contexto (sessão 2 — wiki de código)

Para ingerir o código do próprio projeto como Fonte foi necessário um **symlink** de
gambiarra:

    sources/llmwiki-src -> ../src/llmwiki

pois `code_base_path` resolve `location` sempre como `sources_dir / location` — não como
caminho repo-relativo. Testar o "wiki de código" no repo onde a ferramenta mora não é
o caso borde, mas um produto esperado da própria ferramenta ("dar uma pesquisa ao
repositório leve wiki").

## Trabalho

1. Decidir a semântica de `location` para Fonte `code` local: caminho repo-relativo
   (relativo à raiz do projeto, atrás do manifesto), absoluto, ou inalterado (relativo a
   `sources_dir`) — quem quiser outro resultado usa symlink.
2. Validar contra o caso externo (`repository` + `commit`): a mudança não derramou divergência
   no histórico de caminho bombado nos Espelhos (cuidado em regras de estabilidade de `path`
   no `source_versions`).
3. Implementar + tester: Fonte code com location repo-relativo (ex. `src/llmwiki`)
   à` ingestion igual ao do symlink atual; regression para o caso anterior.
4. Atualizar README/skill com a semântica final.

## Done

- Fonte code do próprio projeto declarável sem symlink; proveniência (commit por arquivo)
  permanece verificável; compatibilidade do formato documentada.

## Answer

`code_base_path` para Fonte code local: tenta **relativo à raiz do projeto**
(`root/location`) primeiro; se não existir, mantém o path relativo a
`sources_dir`. Fonte externa (repository+commit) e path absoluto seguem sem
mudança. Com isso `location: src/llmwiki` funciona sem symlink. Cobertura:
`test_repo_relative_code_location`; série antiga (código sob sources/)
continua passando.
