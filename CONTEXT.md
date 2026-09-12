# llm-wiki

Ferramenta que transforma material de leitura heterogêneo numa wiki local de Markdown, mantida por LLM e armazenada em [OKF](./research/llm-wiki-okf.md), para que um assistente consiga recuperar conhecimento dela gastando poucos tokens.

## Language

### Material de entrada

**Fonte**:
Material bruto de onde o conhecimento é extraído, nunca modificado pela ferramenta. Texto, PDF, Markdown ou código.
_Avoid_: documento, input, corpus, arquivo

**Trecho**:
A porção de uma Fonte que uma única leitura consome de ponta a ponta. Delimitado por fronteira natural da Fonte, não por contagem.
_Avoid_: chunk, pedaço, bloco, fatia

**Âncora**:
A coordenada que localiza uma citação dentro da Fonte. Em código é o símbolo; em texto paginado é a página.
_Avoid_: linha, offset, localização

### Páginas

**Página Conceitual**:
Uma página que explica um conceito. É o produto da leitura, e não corresponde a nenhuma Fonte em particular — uma Fonte rende muitas, e uma delas reúne muitas Fontes.
_Avoid_: nota, artigo, verbete, doc

**Espelho de Fonte**:
Uma página que representa uma Fonte um-para-um e existe para rastreabilidade e citação, não para explicar. Vive em `references/`.
_Avoid_: referência (ambíguo com a citação em si), cópia, stub

**Página Suja**:
Página que recebeu escrita de mais de uma leitura e ainda não foi reconciliada numa voz só.
_Avoid_: página pendente, rascunho, draft

**Página Obsoleta**:
Página cuja Fonte mudou depois de a página ter sido derivada dela. Distinta de página velha: a idade não importa, a divergência importa.
_Avoid_: página stale, página vencida, página expirada

### Vocabulário de `type`

Núcleo pequeno e fixo. `type` é dimensão de busca, não taxonomia de assunto — o assunto vive em `tags`. Extensão é tolerada pelo OKF, mas não é incentivada: tipo que só uma wiki conhece é tipo que ninguém filtra.

**Topic**:
O `type` de uma Página Conceitual. Preferido a `Concept` justamente para não colidir com o sentido mais amplo que o OKF dá à palavra.
_Avoid_: Concept, Knowledge, Article, Note

**Reference**:
O `type` de um Espelho de Fonte.
_Avoid_: Source, Mirror, Citation

### Vocabulário herdado do OKF

**Concept**:
No OKF, qualquer `.md` que não seja arquivo reservado. Termo mais amplo que Página Conceitual: um Espelho de Fonte também é um Concept.
_Avoid_: usar "conceito" e "Concept" como sinônimos

**Bundle**:
A árvore de diretórios que contém a wiki. Uma wiki é um Bundle.
_Avoid_: repositório, catálogo, coleção
