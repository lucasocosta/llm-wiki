# llm-wiki

CLI para construir um Bundle de Markdown em OKF estendido e consultar seu
conhecimento por busca lexical. A CLI não chama LLM; o assistente recebe um
Trecho, redige páginas e devolve cada escrita para validação.

## Execução

Com Python 3.10+ e `uv`, execute a partir deste projeto, sem instalação permanente:

```sh
uvx --from . llm-wiki -C /caminho/do/projeto/llm-wiki ingest next
```

`-C` aponta para o diretório do manifesto (`llm-wiki.yml`). O layout padrão
deixa `bundle_dir` e `sources_dir` livres: um projeto pode consolidar wiki e
Fontes numa mesma subpasta (ex.: `llm-wiki/wiki` + `llm-wiki/sources`), como
neste próprio repositório — o índice de máquina continua em um único
`.llmwiki/` junto do manifesto, resolvido subindo a árvore a partir do Bundle.

Os exemplos seguintes usam `llm-wiki` como abreviação dessa invocação. O diretório
indicado por `-C` contém o manifesto `llm-wiki.yml`:

```yaml
bundle_dir: wiki          # ex.: llm-wiki/wiki (aninhado, como neste repo)
sources_dir: sources        # ex.: llm-wiki/sources
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
da CLI não altera o manifesto. Versionar ou não a pasta da wiki é decisão do curador: o `llm-wiki init`
instala a regra `.llmwiki/` (derivados devem ser ignorados) e deixa
`wiki/`/`sources/` versionáveis. Neste repositório a wiki é apenas **teste da
ferramenta**, então todo o `llm-wiki/` está ignorado — reingestão em clone
novo; páginas de código continuam verificáveis (o `src/` é versionado).

`--trecho-hash` pode ser repetido para gravar vários Trechos da mesma Fonte numa
Página Conceitual. Todos os hashes são validados contra o conteúdo atual da Fonte
indicada por `--source-id`, inclusive para texto, Markdown e PDF. Para reunir
Fontes diferentes, faça uma escrita por Fonte na mesma página; hashes de outra
Fonte ou de Trechos que já mudaram são recusados antes de gravar o Bundle.

## Proveniência e obsolescência

A tool preserva os carimbos anteriores mesmo quando o rascunho do trabalhador
omite metadados automáticos. Cada Página Conceitual registra as versões das
Fontes que a produziram. Atualizar o Espelho de Fonte ou reingerir outra página
não atualiza esse registro. `read-page ID` devolve o conteúdo e o estado de
obsolescência; `stale report` lista páginas obsoletas e proveniência não verificável.

Os detalhes de entradas existentes em `sources`, como Âncora e URI, são
preservados quando omitidos na ingestão ou consolidação. Novos campos podem ser
acrescentados; mudar um valor já registrado exige a remoção explícita da entrada
pelo curador e sua inclusão corrigida. Arquivos de código com conteúdo idêntico
conservam suas versões individuais, para que mudanças em qualquer um deles sejam
detectadas.

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


## Fonte de código do próprio projeto

Uma Fonte `code` local resolve `location` primeiro **relativo à raiz do projeto**
(e depois relativo a `sources_dir`), então uma wiki sobre o próprio código não
precisa de symlink dentro de `sources/`:

```yaml
sources:
  - id: meu-codigo
    type: code
    location: ../src/pacote   # relativo à raiz do manifesto (llm-wiki/)
    allowlist: ["*.py"]
```

Diretórios de cache (`__pycache__`, `.git`) nunca são ingeridos; arquivos da
allowlist que não decodificam como UTF-8 ficam fora da ingestão e aparecem como
`excluded_unreadable` no `ingest report`.
