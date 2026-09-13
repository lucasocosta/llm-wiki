---
id: artefatos-mosaicode
type: Topic
title: Artefatos de software no Mosaicode
description: 'Artefatos gerados no desenvolvimento no Mosaicode: diagrama, código-fonte,
  aplicação e os blocos, com o fluxo de criação.'
tags:
- artefatos
- mosaicode
- diagramas
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 8f6e9eb357ba308a1a3db265f4d8166f7c7cc4803dd852db47b271432c729c70
source_ids:
- poc-mosaicode
source_versions:
  poc-mosaicode:
    type: pdf
    path: sources/poc-lucas-oliveira-costa.pdf
    content_hash: fb79e5be62bd146453867f80aeb829fb9f40b298b6cb731498305e11e253153d
---


Artefatos de software são todos os subprodutos do desenvolvimento: relatórios, documentação, diagramas e até mesmo código-fonte. Gerenciá-los é crítico em ambientes colaborativos: sem esse controle o processo ficaria caótico, pois os artefatos podem ser reutilizados, modificados e atualizados (FUKS; RAPOSO; GEROSA, 2002).

## Fluxo de criação de uma aplicação

Do fluxo do Mosaicode decorrem explicitamente os artefatos:

- **Diagrama** — resultado do processo criativo; o programa final daquele desenvolvimento. É o principal componente com que o usuário interage; é composto por blocos e conexões;
- **Código-fonte** — subproduto do processamento do diagrama (configurações dos blocos e conexões, incluindo os blocos de código estáticos e as propriedades dinâmicas das conexões). É gerado diversas vezes pela ferramenta; o usuário não o cria diretamente;
- **Aplicação** — resultante da compilação ou interpretação do código-fonte (dependendo da linguagem destino); também subproduto do ambiente;
- **Blocos e suas coleções** — as peças mínimas da ferramenta, adquiridas via extensões e bibliotecas de blocos: implicitamente também artefatos importantes.

## Implicação para o compartilhamento

Como o usuário cria diretamente o diagrama (e, por extensão, usa blocos), estes são o núcleo do que se deve versionar e compartilhar; as tags de versionamento em XML propostas ficam em [conclusão e trabalhos futuros](conclusao.md).
