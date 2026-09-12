# Spec: llm-wiki

Status: ready-for-agent

## Problem Statement

Uma pessoa acumula material de leitura sobre um assunto — artigos, PDFs, notas em Markdown, o código-fonte de um projeto — e quer que um assistente de código responda perguntas sobre esse material com precisão.

Hoje as duas saídas disponíveis são ruins. Jogar as Fontes no contexto do assistente não escala: o material não cabe, e o que cabe é redescoberto do zero a cada pergunta, sem nada acumular entre sessões. Montar uma wiki à mão funciona, mas morre pela manutenção — o trabalho tedioso não é ler nem pensar, é a escrituração, e ela cresce mais rápido que o valor.

Falta também o outro lado: mesmo com uma wiki pronta em Markdown, um assistente não consegue usá-la de forma barata. Ele lê arquivos inteiros para descobrir que não eram os certos, e o custo em tokens da busca anula o ganho de ter organizado o conhecimento.

## Solution

Uma ferramenta de linha de comando que constrói e mantém um Bundle — uma wiki local de Markdown no formato OKF estendido — a partir das Fontes que a pessoa declarar, e que oferece busca de baixo custo em tokens sobre o resultado.

A construção é orquestrada pela CLI, que nunca chama LLM: ela extrai texto, delimita Trechos, computa a fila de trabalho, valida conformidade e mantém os índices. O julgamento — decidir que conceitos existem e redigir as páginas — fica com o assistente que a pessoa já usa, invocado um Trecho por vez com contexto limpo. Isso torna a ingestão retomável: interromper no meio de um PDF longo não perde progresso, porque o estado vive em disco e não no contexto.

A consulta é o inverso: conversacional, com o assistente no comando. A CLI expõe busca que ranqueia fora do modelo e devolve só os vencedores em forma de metadata, de modo que o índice nunca entra no contexto. O assistente abre por inteiro apenas as páginas que a resposta exigir.

## User Stories

### Declarar o território

1. Como curador de uma wiki, quero declarar minhas Fontes num manifesto versionado, para que qualquer pessoa que clone o repositório saiba que território a wiki cobre.
2. Como curador, quero declarar a língua em que as páginas serão escritas uma única vez para toda a wiki, para que ingestão e consulta não precisem adivinhar e a busca lexical não fracasse por cruzar idiomas.
3. Como curador, quero declarar a língua original de cada Fonte separadamente da língua da wiki, para que material em inglês produza páginas na minha língua sem que eu precise traduzir nada à mão.
4. Como curador de uma wiki sobre um projeto de código, quero declarar uma allowlist explícita de diretórios, para que teste, migração, código gerado e dependência de terceiros não gerem páginas inúteis.
5. Como curador, quero que a ferramenta ignore uma Fonte fora da allowlist e me diga quantos arquivos ficaram de fora, para que a wiki não infle sem eu perceber nem encolha sem eu saber.
6. Como curador de uma wiki sobre código de terceiros, quero apontar para um repositório externo pinado num commit, para que a wiki seja reproduzível sem eu copiar o código para dentro do meu repositório.

### Ingerir

7. Como curador, quero ingerir um arquivo de texto simples, para que o conhecimento nele vire Páginas Conceituais.
8. Como curador, quero ingerir um PDF, para que material que só existe nesse formato entre na wiki.
9. Como curador, quero que um PDF escaneado falhe com erro nomeando o arquivo, para que eu corrija a Fonte em vez de descobrir páginas vazias depois de achar que a ingestão deu certo.
10. Como curador, quero ingerir arquivos Markdown que já escrevi, para que minhas notas antigas se integrem ao mesmo corpo de conhecimento.
11. Como curador, quero ingerir código-fonte como material de leitura, para que a wiki capture por que o código existe e que decisões estão congeladas nele, em vez de virar documentação de API que envelhece a cada commit.
12. Como curador, quero que uma Fonte grande seja quebrada em Trechos por fronteira natural — capítulo, seção, arquivo, função — para que nenhuma página nasça de um corte no meio de um raciocínio.
13. Como curador, quero um teto de orçamento que force o corte quando a fronteira natural é grande demais, para que um capítulo de oitenta páginas não estoure o contexto do trabalhador.
14. Como curador, quero poder sobrepor esse teto sem trocar a estratégia de corte, para que eu ajuste ao assistente que estou usando sem reconfigurar a ingestão.
15. Como curador, quero que uma única Fonte produza quantas Páginas Conceituais o material render, para que a wiki seja organizada por conceito e não espelhe a arbitrariedade de como os arquivos foram divididos.
16. Como curador, quero que cada Fonte ingerida ganhe um Espelho de Fonte em `references/`, para que eu consiga responder de onde uma afirmação saiu mesmo quando a Fonte é um PDF sem URL.
17. Como assistente trabalhador, quero receber o Trecho já extraído junto com uma **shortlist ranqueada** dos conceitos existentes mais próximos daquele Trecho, para que eu reuse ids sem que o índice inteiro entre no meu contexto.
18. Como assistente trabalhador, quero poder buscar na wiki por conta própria quando a shortlist não bastar, para que eu confirme se um conceito já existe antes de criar um id novo.
19. Como assistente trabalhador, quero pedir uma página existente por inteiro quando for augmentá-la, para que eu enriqueça o que está lá em vez de reescrever no escuro.
20. Como assistente trabalhador, quero que criar um id novo seja o caminho de exceção e não o padrão, para que a wiki convirja em vez de se ramificar.
21. Como assistente trabalhador, quero ser proibido de referenciar um id que não existe, para que a wiki não se enche de links que apontam para o nada.
22. Como curador, quero que o código seja lido das folhas do grafo de imports para a raiz, para que quando o trabalhador chegar num módulo de alto nível os conceitos de que ele depende já existam e possam ser referenciados em vez de reexplicados.

### Retomar e não estragar

23. Como curador, quero retomar uma ingestão interrompida sem reprocessar o que já foi feito, para que material longo seja viável mesmo com o contexto do assistente compactando no meio do caminho.
24. Como curador, quero retomar a ingestão em outra máquina, para que trocar de computador não me faça perder progresso.
25. Como curador, quero que a fila de trabalho seja derivada da comparação entre Fontes e wiki em vez de guardada num arquivo de estado, para que duas pessoas ingerindo em paralelo não produzam conflito de merge num arquivo derivado.
26. Como curador, quero que a ferramenta recuse uma escrita que apague conteúdo que ela não pode avaliar, para que um trabalhador sem memória do passe anterior enriqueça a página em vez de degradá-la.
27. Como assistente trabalhador, quero que a recusa venha com a instrução de como corrigir, para que eu consiga completar o trabalho sem intervenção humana.
28. Como curador, quero que a ferramenta recuse gravar uma página cujo frontmatter não tem `type`, para que a wiki permaneça conforme e legível por qualquer ferramenta OKF.
29. Como curador, quero que as chaves do frontmatter saiam sempre na mesma ordem, para que o diff de uma reingestão mostre o que mudou de fato e não um embaralhamento.
30. Como curador, quero que a data e o autor de geração sejam preenchidos pela ferramenta e não pelo assistente, para que a proveniência não dependa de o modelo acertar um timestamp.

### Consolidar

31. Como curador, quero saber quais páginas são Páginas Sujas, para que eu veja onde a colagem de várias leituras precisa virar uma voz só.
32. Como curador, quero disparar um passe de consolidação por vontade própria e não durante a ingestão, para que eu decida coerência só depois de ter todas as Fontes na mão.
33. Como curador, quero que a consolidação releia apenas a página, sem reabrir as Fontes, para que o passe seja barato o suficiente para rodar sobre muitas páginas.
34. Como curador, quero que a consolidação possa fundir seções e encurtar a página, para que unificar vozes seja possível — coisa que a guarda proíbe na escrita comum.
35. Como curador, quero que nem a consolidação consiga perder proveniência, para que a liberdade de reescrever a forma não vire liberdade de apagar rastro.
36. Como curador, quero remover uma entrada de proveniência por comando explícito, para que eu conserte uma citação errada sem desligar a guarda.
37. Como curador, quero mover ou renomear uma página por comando explícito que atualize quem aponta para ela, para que reorganizar a wiki não produza links quebrados.
38. Como curador, quero que o trabalhador não tenha acesso a nenhum desses dois comandos, para que a guarda não tenha chave-mestra.

### Perceber obsolescência

39. Como curador, quero que uma página derivada de código seja marcada Página Obsoleta quando o commit daquele arquivo mudar, para que a obsolescência seja uma verificação exata e não um chute de calendário.
40. Como curador, quero que uma página derivada de arquivo mude de estado quando o hash do conteúdo mudar, para que editar um PDF ou uma nota invalide o que dela derivou.
41. Como curador, quero saber o que mudou na Fonte desde a derivação, para que a reingestão releia só a parte afetada.
42. Como curador, quero que citações de código usem o símbolo como Âncora, e não o número de linha, para que a referência sobreviva a mover-se de arquivo e a reindentação.
43. Como curador, quero saber quais páginas ficaram órfãs, para que conhecimento que ninguém alcança não fique escondido na wiki.

### Consultar

44. Como assistente consultando, quero uma busca que ranqueie fora do meu contexto e me devolva só os candidatos vencedores, para que eu não gaste o orçamento de tokens lendo o índice para descobrir o que ler.
45. Como assistente consultando, quero que cada resultado traga id, título, `type` e descrição, para que eu escolha informado a página a abrir sem pagar o corpo dela.
46. Como assistente consultando, quero poder pedir um snippet do trecho que casou, para que perguntas factuais se resolvam no próprio recorte sem abrir a página.
47. Como assistente consultando, quero que o snippet seja opcional e não o padrão, para que consultas comuns não paguem por um recurso que só uma minoria aproveita.
48. Como assistente consultando, quero filtrar a busca por `type` e por tags, para que eu estreite o resultado quando já sei a natureza do que procuro.
49. Como assistente consultando, quero ler uma página inteira de uma vez, para que eu não precise saber que seções ela tem antes de pedir.
50. Como assistente consultando, quero navegar a hierarquia um nível por vez, para que eu me situe num Bundle grande sem carregá-lo inteiro.
51. Como assistente consultando, quero descobrir o que aponta para uma página, para que eu siga o grafo de conhecimento em vez de repetir buscas.
52. Como assistente consultando, quero ser avisado quando uma página que abri está obsoleta, para que eu qualifique a resposta em vez de afirmar algo desatualizado com confiança.

### Ler como humano

53. Como leitor humano, quero abrir a wiki no GitHub e navegar pelos links, para que eu não precise de ferramenta nenhuma instalada para ler.
54. Como leitor humano, quero abrir a wiki no Obsidian, para que eu use o grafo e a busca que já conheço.
55. Como leitor humano, quero um `index.md` por diretório com título e uma linha de descrição por item, para que eu escolha o que ler sem abrir tudo.
56. Como leitor humano, quero um registro cronológico do que a ferramenta fez, para que eu audite a evolução da wiki sem ler o histórico do git.

### Usar de dentro do assistente

57. Como pessoa usando Kiro, Copilot ou Claude, quero chamar a ferramenta de dentro do assistente, para que eu não precise de chave de API de LLM nenhuma.
58. Como pessoa usando um assistente qualquer, quero que a ferramenta funcione onde houver shell, para que eu não fique preso a um host específico.
59. Como pessoa instalando, quero invocar a ferramenta sem instalação prévia, para que ela funcione em máquinas que eu não configurei.
60. Como pessoa usando o assistente, quero uma skill que ensine quando e como chamar a busca, para que o assistente use a wiki sem eu explicar a cada sessão.

## Implementation Decisions

### Armazenamento

- O Bundle é OKF v0.2 **estendido**: respeitamos a estrutura e acrescentamos chaves próprias quando o SPEC não cobre a necessidade. Registrado em ADR 0001. O §11 do SPEC proíbe consumidores de rejeitar chave ou `type` desconhecido, o que torna a extensão segura.
- `type` é dimensão de busca, não taxonomia de assunto. Núcleo fixo e pequeno: **`Topic`** para Página Conceitual, **`Reference`** para Espelho de Fonte. Assunto vive em `tags`. `Topic` foi preferido a `Concept` para não colidir com o sentido mais amplo que o OKF dá à palavra.
- Obsolescência **não** usa `stale_after`, que só sabe comparar timestamp. Página derivada de código compara commit SHA; página derivada de arquivo compara hash de conteúdo. Ambas em chaves nossas.
- O disparo da verificação de obsolescência é a presença da chave de proveniência, não o `type`. `type` descreve o que a página é para quem lê, não como ela é mantida.
- Links entre páginas são **relativos ao diretório do documento**, nunca iniciados por `/`. O SPEC §6 recomenda o oposto, mas a implementação de referência do OKF proíbe explicitamente o `/` inicial por quebrar a renderização no GitHub, e o exemplo real do próprio repositório segue a implementação. A normalização para id absoluto acontece só dentro do índice de máquina.
- `index.md` segue o §8 à risca: sem frontmatter exceto no raiz, corpo em bullets de título, link e descrição. É o único ponto onde a conformidade dá retorno imediato, porque é a porta de entrada humana.
- `log.md` existe e é **só história legível**, nunca estado. Estado em arquivo versionado reintroduz o conflito de merge que a fila computada elimina.
- A língua da wiki é declarada uma vez no frontmatter do `index.md` raiz, ao lado de `okf_version`. É propriedade da wiki, não da página: wiki com páginas em línguas misturadas quebra busca lexical.
- Termos técnicos consagrados não são traduzidos, qualquer que seja a língua da wiki, porque são exatamente os termos que serão buscados.

### Arquitetura

- Duas metades com regimes opostos, registrado em ADR 0002: **ingestão determinística** orquestrada pela CLI, **consulta conversacional** conduzida pelo assistente. A CLI não chama LLM em nenhum dos dois casos.
- A unidade de trabalho da ingestão é o **Trecho**, não a página. Uma invocação recebe um Trecho e produz quantas páginas ele render. A implementação de referência do OKF usa um concept por invocação, mas pode: a fonte dela é metadado de tabela, pequeno e um-para-um com o concept. Prosa não tem nenhuma das duas propriedades, e invocar por página faria o texto-fonte ser pago uma vez por página.
- Um trabalhador por Trecho, com contexto limpo, para que a qualidade da página cinquenta seja igual à da página um.
- A fila de trabalho é **computada** comparando Fontes com o estado da wiki, não persistida. Consequência: retomável em qualquer máquina, sem arquivo de estado para conflitar.
- A tool de escrita implementa uma **guarda de augmentação**: recusa escrita que remova conteúdo que ela não pode avaliar, e a recusa vem como instrução de correção em vez de exceção. Isso é estrutural, não refinamento — como um conceito aparece em Trechos distintos, a mesma página será escrita por trabalhadores que não se conhecem.
- A guarda protege **proveniência e cobertura, nunca prosa**. Reescrever um parágrafo é livre; perder rastro não é. As invariantes são estas seis, e são o contrato que os testes verificam:
  1. **`sources` é append-only.** A escrita nova é unida à lista existente por `id`; remover uma entrada exige comando explícito de remoção, não uma escrita comum.
  2. **Cabeçalhos não desaparecem.** Todo cabeçalho de seção presente antes tem de estar presente depois. Renomear é remover mais adicionar, e portanto é recusado.
  3. **Footnote referenciada resolve.** Todo label de footnote citado no corpo tem de casar com um `id` de `sources`. Corpo com citação órfã é recusado.
  4. **Identidade é imutável na escrita comum.** `type` e id de uma página existente não mudam por escrita; mudança exige comando próprio, que move a página e atualiza quem aponta para ela.
  5. **Encolhimento acima do limiar é recusado.** Corpo que perde mais que uma fração configurável do seu tamanho não passa.
  6. **Links de saída são append-only.** Link para um concept existente que estava presente antes tem de continuar presente. Adicionar é livre; remover não.
- **Não existe marcador de escape por escrita.** O escape é o *modo de operação*, e o modo é determinado por qual comando está rodando, nunca por uma chave que o modelo possa setar. São dois:
  - **Modo ingestão**, o único disponível ao trabalhador que processa Trechos: valem as seis invariantes, sem exceção.
  - **Modo consolidação**, disponível somente ao comando de consolidação, que só uma pessoa dispara: as invariantes 2, 5 e 6 são substituídas por uma única, mais frouxa na forma e igualmente rígida no rastro — **toda entrada de `sources` citada antes tem de continuar citada por alguma footnote depois**. Isso libera fundir seções, encurtar e podar link duplicado, que é exatamente o trabalho de unificar vozes, e mantém impossível perder proveniência. As invariantes 1, 3 e 4 continuam valendo nos dois modos.
- Essa separação é o que faz a guarda ser guarda. Um marcador que o trabalhador pudesse setar seria chave-mestra, e uma trava sem escape nenhum tornaria a consolidação impossível, porque unificar vozes funde seções por definição.
- A recusa nomeia a invariante violada e o que foi perdido — quais entradas de `sources`, quais cabeçalhos, quais links — para que o trabalhador corrija sem intervenção humana. É o padrão de erro-como-instrução observado na implementação de referência do OKF.
- **Dois escapes legítimos existem e são comandos próprios, não escritas:** remover uma entrada de `sources`, e mover ou renomear uma página. O segundo atualiza quem aponta para ela na mesma operação. Ambos são operações de curador, indisponíveis ao trabalhador, e ambos precisam de teste — uma guarda implementada como trava absoluta passaria na suíte sem eles.

### Contrato do trabalhador

- O trabalhador é invocado com **um Trecho já extraído** e uma **shortlist ranqueada** de conceitos vizinhos daquele Trecho. A shortlist obedece à mesma regra do lado de leitura: o índice não entra no contexto, só os vencedores. Entregar o índice inteiro, como a implementação de referência do OKF faz com `list_concepts()`, funciona no Bundle pequeno dela e quebra numa wiki grande.
- Além disso o trabalhador tem à disposição: buscar na wiki, ler uma página inteira, e gravar página. Nada mais. Ele não enfileira trabalho, não gera índice e não decide o que vem depois.
- **A tool carimba a contribuição, não o trabalhador.** Como a CLI entregou o item de trabalho, ela sabe qual Trecho está sendo processado e grava isso na página junto com a escrita, pelo mesmo motivo e do mesmo jeito que preenche `generated`: se o registro dependesse do modelo lembrar, uma omissão faria a página parecer limpa para sempre. O carimbo é o hash do Trecho, não sua posição, para que reordenar a Fonte não invalide páginas à toa.
- Esse registro é o que torna a Página Suja computável sem arquivo de estado. A consolidação, ao terminar, grava na página o conjunto de Trechos contribuintes naquele instante; **suja é a página cujo conjunto atual difere do conjunto registrado na última consolidação**. Página nunca consolidada e tocada por mais de um Trecho é suja; tocada por um só, não.
- A consolidação é passe separado e opt-in, com unidade igual à **Página Suja**, e relê só a página.
- Ordem de leitura de código: folhas do grafo de imports primeiro, subindo para a raiz.

### Manifesto

- Arquivo **único, YAML, versionado, na raiz do repositório**. YAML por coerência com o frontmatter, para não introduzir um segundo dialeto de configuração.
- Declara, no nível da wiki: o diretório do Bundle, o diretório das Fontes, e a língua das páginas — esta última também gravada no frontmatter do `index.md` raiz, que é onde a consulta a lê sem precisar do manifesto.
- Declara, por Fonte: um id estável, o tipo (`text`, `pdf`, `markdown`, `code`), a localização, e a língua original. Fonte de tipo `code` declara também repositório e commit quando for externa.
- **Uma wiki abrange muitas Fontes, sempre.** Wiki sobre um único projeto é o caso particular em que as Fontes por acaso vêm todas de um repositório — não um modo diferente. Isso mantém o manifesto com uma forma só e a allowlist como propriedade da Fonte, não da wiki.
- **A allowlist é por Fonte de código**, não global, e é uma lista de caminhos incluídos. Caminho não listado não é ingerido, e o relatório de ingestão diz quantos arquivos foram ignorados por esse motivo, para que a exclusão silenciosa não passe despercebida.

### Extração

- **Sem OCR na v1.** Uma Fonte cujo texto extraído fique abaixo de um mínimo por página é **recusada com erro nomeando o arquivo**, e não entra na fila. PDF escaneado, portanto, falha de forma alta e explícita em vez de produzir páginas vazias — que é o modo de falha caro, porque parece sucesso.
- Extração que produz zero texto é sempre erro, nunca uma Fonte de zero Trechos.
- A **Âncora** é gravada na entrada de `sources` que a footnote referencia, e sua forma depende do tipo da Fonte: **símbolo** (nome qualificado da função ou classe) para código, **número de página** para PDF, **caminho de cabeçalhos** para Markdown. Texto corrido sem cabeçalho nenhum usa o **índice do Trecho dentro da Fonte**, que é estável porque o Trecho é identificado por hash e não por posição. A citação no corpo continua sendo footnote com label igual ao `id` da entrada, que é o mecanismo que o próprio OKF define para atribuição por alegação.

### Busca

- O índice de máquina **nunca entra no contexto**. A CLI ranqueia e devolve apenas os vencedores. Esta é a decisão central da metade de leitura: se o modelo lê o índice para escolher, já pagou o custo que a wiki existia para evitar.
- O índice de ranqueamento cobre **frontmatter e corpo**, com peso maior para título, descrição e tags. Indexar o corpo não custa token nenhum porque o índice mora em disco. Ranquear só por descrição joga fora o sinal que decide relevância.
- Payload padrão por resultado: id, título, `type`, descrição. Snippet do trecho que casou fica atrás de flag.
- Busca **lexical apenas** na primeira versão. Sem embeddings, sem índice vetorial, sem modelo local. Não é a única opção viável sem API — o qmd citado pelo gist faz busca híbrida com re-ranking inteiramente on-device — mas é a mais simples de construir e a única cujo resultado errado você consegue explicar. Depurabilidade e simplicidade são a razão; ausência de alternativa não é. O gancho para híbrido fica previsto, não pago.
- Leitura é de **página inteira**. Manter a página curta é invariante da ingestão, e a mecânica é aviso, não recusa: página que passa de um tamanho configurável é reportada pelo lint como candidata a divisão, com os cabeçalhos dela na saída para sugerir onde cortar. Recusar seria pior que o problema, porque forçaria o trabalhador a truncar conhecimento para caber. Recuperação por seção só compensaria se as páginas crescessem, e se crescerem o problema real é a granularidade da Página Conceitual — que é o que o aviso expõe.
- **Detecção de órfãos está dentro do escopo**, ao contrário da detecção de contradição. A distinção é o que a verificação exige: órfão é uma propriedade do grafo de links, computável sem ler o conteúdo e sem julgamento — página sem nenhuma aresta de entrada, excluídos os `index.md`. Contradição exige entender o que duas páginas afirmam. O Lint do Karpathy junta as duas coisas; nós partimos pela linha do que é determinístico.
- Dois índices com papéis distintos: `index.md` materializado e versionado, porque é conteúdo humano que o OKF espera; índice de máquina em cache fora do controle de versão, reconstruído quando os arquivos mudarem. A diferença não é "derivado versus não derivado" — `index.md` também é derivado e vai para o git. É quem edita e quem lê: `index.md` é lido por humano e revisado em diff, o índice de máquina é lido só por programa e reconstruído inteiro, então versioná-lo só produziria conflito em arquivo que ninguém inspeciona.
- **`index.md` é derivado do frontmatter das páginas, não do manifesto.** O manifesto declara Fontes; o `index.md` lista concepts. As descrições por item saem do `description` de cada página, e a descrição de um diretório é composta a partir dos itens que ele contém, sem LLM.

### Superfície e distribuição

- A CLI é o motor e as tools são a fachada. A lógica de busca não mora no adaptador, para poder ser testada sem LLM e reaproveitada depois por outro transporte.
- Python, distribuído para execução sem instalação prévia. A escolha é pelo reaproveitamento: o parsing de frontmatter, a validação e a geração de `index.md` do reference agent do OKF são Apache 2.0 e já conformes, e entram com atribuição.
- **Atenção ao reaproveitar a geração de `index.md`:** ela sintetiza as descrições de *diretório* chamando o Gemini. As descrições por página vêm do frontmatter e não usam LLM, mas a de diretório usa. A função de síntese é um parâmetro injetável com default, e já existe um fallback determinístico no próprio código, então substituí-la é injeção e não cirurgia. Ligar essa geração sem trocar a função faria a CLI chamar um LLM e **violaria o ADR 0002** — é o erro mais fácil de cometer nesta base de código.
- Uma skill acompanha a ferramenta e é o ponteiro que ensina o assistente quando e como chamar a busca.
- As Fontes vivem no mesmo repositório que a wiki, em diretório à parte, e o Espelho de Fonte guarda caminho relativo e hash. Código de terceiros entra pinado por SHA, sem cópia.

## Testing Decisions

Um bom teste aqui afirma sobre **comportamento observável**: arquivos que apareceram em disco, conteúdo de frontmatter, corpo de `index.md`, código de saída, e o que a busca devolveu. Nunca sobre como o score foi calculado, como o texto foi extraído ou que estrutura de dados o índice usa.

**Um único seam: o contrato da CLI.** Os testes montam um Bundle temporário com manifesto e Fontes, invocam o entry point por `argv` no mesmo processo — mesmo contrato, execução rápida — e afirmam sobre disco e stdout. Alguns testes por subprocess garantem que o binário está de fato ligado.

Isso é possível porque a CLI não chama LLM. A superfície de ingestão dela é "me dê o próximo item de trabalho" e "guarde esta página escrita", ambas determinísticas, então **o teste faz o papel do trabalhador**: escreve as páginas que um assistente escreveria, inclusive versões deliberadamente piores para provar que a guarda de augmentação recusa. Não há mock de LLM em nenhum ponto da suíte.

Cobertura pelo mesmo seam: fila computada a partir da comparação Fontes/wiki; delimitação de Trecho por fronteira natural e por teto de orçamento; as seis invariantes da guarda de augmentação, cada uma com seu caso de recusa e a mensagem que nomeia o que foi perdido; **os dois modos de escrita** — que uma fusão de seções é recusada em modo ingestão e aceita em modo consolidação, e que a perda de citação de uma entrada de `sources` é recusada nos **dois**; **os dois escapes de curador**, remover proveniência e mover página, este último incluindo a atualização de quem apontava para ela, porque sem esses testes uma guarda implementada como trava absoluta passaria na suíte; que o trabalhador não alcança nenhum dos dois comandos; recusa de frontmatter sem `type`; ordem determinística das chaves; carimbo de Trecho aplicado pela tool mesmo quando a escrita não o menciona; `index.md` conforme o §8, derivado do frontmatter e com descrição de diretório gerada sem LLM; ordem de resultados da busca sobre fixtures conhecidas; forma do payload com e sem snippet; conteúdo da shortlist entregue ao trabalhador; detecção de obsolescência por SHA e por hash; cálculo de Página Suja antes e depois de uma consolidação; aviso de página longa com os cabeçalhos na saída; recusa de Fonte cuja extração fica abaixo do mínimo; relatório de arquivos ignorados por allowlist; recusa de link para id inexistente; detecção de órfãos; ordem folhas-primeiro na leitura de código.

**O que o seam não alcança, e não vamos fingir que alcança.** A *preferência* por reusar um id em vez de criar um novo é julgamento do trabalhador, induzido por prosa de skill: não há assert honesto para ela. O que é testável é o mecanismo que a sustenta — que a shortlist entregue contém os candidatos certos, e que um link para id inexistente é recusado. Testes de duplicação semântica ficariam verificando o modelo, não a ferramenta.

**Recusamos deliberadamente dois seams internos.** Extração de PDF e ranqueamento são os candidatos óbvios a teste unitário, e ambos são observáveis pela CLI com fixture pequena. Testá-los por dentro congelaria a implementação justamente onde ela mais vai mudar: o ranqueamento será reajustado várias vezes, e teste acoplado ao cálculo impede a melhoria. Afirmamos "esta pergunta traz esta página primeiro", não como o score saiu.

Fixtures: um punhado de Markdown, um arquivo de código com imports para exercitar a ordem de leitura, e um PDF minúsculo real — esse caminho não pode ser fingido.

**Prior art:** nenhuma neste repositório, que não tem suíte de testes nem manifesto de projeto. A referência é a suíte do reference agent do OKF, que fixa os caminhos de teste e de código no manifesto e cobre, em teste dedicado ao parser de frontmatter, o que ele aceita e rejeita. Herdamos pytest e essa organização junto com o código reaproveitado.

Fica **sem teste automatizado** a skill que ensina o assistente a usar a CLI: é prosa que governa julgamento de modelo, e não existe assert honesto para isso.

## Out of Scope

- **Attested Computations** e todo o subsistema de `runtime`, `executor` e `attester` do OKF. Não têm papel numa wiki de material de leitura, e o próprio SPEC deixa os protocolos de runtime deferidos.
- **Busca híbrida, embeddings e índice vetorial.** O gancho fica previsto; nada é implementado. A afirmação de que lexical basta na escala de ~100 Fontes e centenas de páginas é do gist do Karpathy e é a aposta desta versão.
- **Detecção de contradição entre páginas.** É parte do Lint que o Karpathy descreve e é reconhecidamente o mecanismo pelo qual wikis apodrecem, mas detectá-la exige reler grupos inteiros de páginas, o oposto de tudo que decidimos sobre economia de contexto. Exclusão consciente, não esquecimento.
- **Servidor MCP.** A CLI é o denominador comum entre hosts; MCP é otimização posterior, se algum host justificar.
- **Recuperação por seção** da página.
- **Wiki multilíngue.** Uma wiki tem uma língua.
- **Ativos que não sejam Markdown** dentro do Bundle: imagem, HTML e CSV não são ingeridos nem indexados.
- **Interface gráfica** ou visualizador de grafo.
- **Documentação de API gerada a partir de código.** A wiki captura conhecimento extraído do código, não a superfície dele.

## Further Notes

O documento de pesquisa que fundamenta estas decisões está em `research/llm-wiki-okf.md`, com fonte primária citada por afirmação. Ele registra explicitamente o que foi verificado e o que não foi.

Duas cautelas herdadas da pesquisa e que convém não esquecer.

A primeira: a adoção do OKF **não** deve ser justificada por compatibilidade com ecossistema. Em setembro de 2026 o repositório canônico tinha seis commits, autor único, nenhuma release, e o próprio README chamava agente e viewer de "proof of concept". O formato foi adotado pelo desenho, e o ferramental dele hoje ingere apenas BigQuery e páginas HTML — tudo que este spec descreve sobre texto, PDF, Markdown e código é terreno novo, assim como a metade de busca, que não existe em nenhuma forma upstream.

A segunda: o connector do OKF para o Knowledge Catalog documenta as limitações que os próprios autores encontraram construindo algo desta classe — só um punhado de chaves de frontmatter carregadas, só arquivos Markdown, cross-links relativos que não resolvem do outro lado, renomes deixando órfãos, ausência de estratégia de merge, e escala não testada além de uma demonstração de quatorze arquivos. Serve como mapa dos lugares onde esse tipo de ferramenta quebra.

Uma ponta ficou sem decisão, e é pequena de verdade: o comportamento da primeira ingestão numa wiki vazia, quando a shortlist de conceitos vizinhos é necessariamente vazia e toda criação de id é criação nova. Resolvível na implementação sem afetar nada acima.

### Revisão

Esta spec passou por revisão independente depois de escrita, e a revisão encontrou seis impedimentos e cinco correções, todos endereçados aqui. Vale registrar os que eram erro de fato, não omissão:

A versão original entregava ao trabalhador "o índice de conceitos existentes", contradizendo frontalmente a decisão central da metade de leitura de que o índice nunca entra no contexto. Virou shortlist ranqueada por Trecho, e o contrato do trabalhador — que antes só existia implicitamente na seção de testes — está explícito.

A versão original afirmava que busca lexical era a única opção sustentável sem API. Falso: o qmd, citado no próprio gist que fundamenta a pesquisa, faz híbrido on-device. A decisão continua a mesma; a justificativa foi corrigida para as razões verdadeiras.

A versão original prometia reaproveitar a geração de `index.md` do OKF sem notar que ela chama o Gemini para descrever diretórios. Como a função de síntese é injetável, a adaptação é trivial — mas ligá-la sem trocar a função violaria o ADR 0002, e isso agora está dito onde o implementador vai ler.

A guarda de augmentação estava no nível de abstração do ADR, o que criava circularidade: os testes prometidos não eram escrevíveis sem as invariantes. As cinco invariantes estão especificadas, e a Página Suja deixou de ser circular ao ganhar o registro de Trechos contribuintes que a torna computável.
