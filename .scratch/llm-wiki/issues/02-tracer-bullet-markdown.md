# 02: Tracer bullet — ingerir um Markdown e ler a página de volta

**What to build:** O caminho completo mais fino que existe. Uma pessoa declara uma Fonte Markdown no manifesto e roda a ingestão; a CLI entrega um item de trabalho com o Trecho já extraído; o trabalhador grava uma Página Conceitual; a página é lida de volta inteira. Ao fim a wiki tem uma Página Conceitual, um Espelho de Fonte e um `index.md` navegável. Nenhuma busca, nenhuma fila, nenhuma guarda além do mínimo: só a prova de que o caminho fecha de ponta a ponta.

**Blocked by:** 01.

**Status:** done

- [x] O manifesto declara o diretório do Bundle, o diretório das Fontes, a língua das páginas e uma Fonte de tipo markdown
- [x] A língua da wiki fica gravada no frontmatter do `index.md` raiz, ao lado da versão do formato
- [x] A CLI entrega um item de trabalho contendo o Trecho já extraído
- [x] A página gravada tem `type` `Topic`, e a tool preenche `generated` e o hash do Trecho contribuinte mesmo quando a escrita não os menciona
- [x] O Espelho de Fonte nasce em `references/` com `type` `Reference` e guarda caminho relativo e hash do conteúdo
- [x] Ler uma página devolve frontmatter e corpo inteiros
- [x] O `index.md` regenerado lista a página com sua descrição
- [x] Links entre páginas são relativos ao diretório do documento, nunca iniciados por `/`

## Comments

- 2026-09-12 — Acompanhamento do review de `75597d6...4eb32c1`. O teto de orçamento das histórias 13–14 da spec não foi decomposto nos tickets originais. Implementação e regressões para Markdown em [22 — teto de Trechos](22-teto-orcamento-trechos.md). A preservação de contribuições em escritas sucessivas é tratada em [16 — preservar carimbos](16-preservar-carimbos-augmentacao.md).
