# llm-wiki

CLI para construir um Bundle de Markdown em OKF estendido e consultar seu
conhecimento por busca lexical. A CLI não chama LLM; o assistente recebe um
Trecho, redige páginas e devolve cada escrita para validação.

## Execução

Com Python 3.10+ e `uv`, execute a partir deste projeto, sem instalação permanente:

```sh
uvx --from . llm-wiki -C /caminho/do/projeto ingest next
```

Os exemplos seguintes usam `llm-wiki` como abreviação dessa invocação. O diretório
indicado por `-C` contém o manifesto `llm-wiki.yml`:

```yaml
bundle_dir: wiki
sources_dir: sources
language: pt-BR
max_trecho_chars: 12000
sources:
  - id: notes
    type: markdown
    location: notes.md
    language: pt-BR
```

## Orçamento e retomada

`max_trecho_chars` é um inteiro positivo, em caracteres Unicode, com padrão
12.000. Vale para Markdown, texto, PDF e código. A extração escolhe fronteiras
naturais primeiro; somente uma unidade maior que o teto é subdividida. O corte
prefere uma quebra de linha ou espaço próximo do limite e, quando necessário,
corta entre caracteres. Ele preserva todo o texto extraído, a Âncora e a
rastreabilidade do arquivo de código. Esse teto mede texto, não tokens; reserve
contexto adicional para instruções, shortlist e páginas que o trabalhador abrir.

É possível sobrepor o teto sem editar o manifesto:

```sh
llm-wiki ingest next --max-trecho-chars 6000
llm-wiki ingest queue --max-trecho-chars 6000
llm-wiki ingest write-page --max-trecho-chars 6000 \
  --page-id assunto --source-id notes --trecho-hash HASH \
  --content-file pagina.md
```

Use o mesmo teto ao pedir trabalho, gravar e retomar. Com as mesmas Fontes e
configuração, os Trechos e seus hashes são determinísticos, inclusive em outra
máquina. Mudar o teto pode mudar os hashes e gerar trabalho novamente. A opção
da CLI não altera o manifesto. Para compartilhar a configuração, versione-a
no manifesto junto do Bundle e das Fontes.

## Proveniência e obsolescência

A tool preserva os carimbos anteriores mesmo quando o rascunho do trabalhador
omite metadados automáticos. Cada Página Conceitual registra as versões das
Fontes que a produziram. Atualizar o Espelho de Fonte ou reingerir outra página
não atualiza esse registro. `read-page ID` devolve o conteúdo e o estado de
obsolescência; `stale report` lista páginas obsoletas e proveniência não verificável.

Para código local, a revisão é o último commit que alterou cada arquivo
contribuinte. Conteúdo sem revisão verificável, como arquivo novo ou alterado
sem commit, não recebe um SHA inventado: a consulta informa `unverifiable` e
`stale: null` quando não há evidência suficiente. Páginas antigas sem versão de
derivação também permanecem explicitamente não verificáveis até a reingestão.

Uma Fonte de código externa declara `repository`, `location`, `commit` e
`allowlist`. `location` aponta para um checkout existente. A CLI exige que seu
HEAD corresponda ao SHA declarado e que os arquivos incluídos correspondam ao
conteúdo commitado, tanto na entrega quanto na escrita. Uma divergência produz
erro; o curador deve preparar o checkout correto. A CLI não muda o checkout nem
copia a Fonte para o repositório da wiki.

## Desenvolvimento

```sh
uv sync --extra dev
uv run pytest
```

Os testes exercitam a CLI por `argv` e verificam disco/stdout; os testes de
distribuição também executam o binário por subprocesso. A prosa da skill não é
avaliada por asserts de palavras ou por simulação de julgamento do modelo.
