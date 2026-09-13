---
id: mosaicode
type: Topic
title: Ambiente Mosaicode
description: Ambiente de programação visual para artes digitais, formado por blocos,
  conexões, portas e extensões, que gera código-fonte a partir de diagramas.
tags:
- mosaicode
- vpl
- programacao-visual
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- f97f5715c0126ee9961bbb3491a2b9be3013bd388d8642ee92865223d20f3736
source_ids:
- poc-mosaicode
source_versions:
  poc-mosaicode:
    type: pdf
    path: sources/poc-lucas-oliveira-costa.pdf
    content_hash: fb79e5be62bd146453867f80aeb829fb9f40b298b6cb731498305e11e253153d
---


O Mosaicode é um ambiente de programação visual para atender demandas das artes digitais, permitindo que artistas desenvolvam aplicações sem precisar de conhecimento em linguagens de programação. Sua base são diagramas gráficos de caixas e conexões que, ao final, geram um código-fonte executável na linguagem desejada.

## Blocos e conexões

- **Blocos** são as peças mínimas do fluxo e possuem propriedades **estáticas** (definidas por quem criou o bloco, por exemplo o tamanho de um elemento na tela) e **dinâmicas** (definidas pela interação entre blocos, através de conexões);
- **Conexões** são feitas pelas portas de entrada e saída dos blocos no editor do diagrama; os valores de entrada e saída devem ser do mesmo tipo, definido pelo próprio bloco gerador;
- Um **diagrama** é uma coleção de blocos e conexões; mudar uma conexão gera um novo diagrama e, portanto, um código-fonte diferente, com resultados possivelmente distintos.

## Extensibilidade

O environment é extensível: extensões adicionam blocos, portas e padrões de código às bibliotecas de blocos. Componentes (Blocos, Portas e Padrões de Código) podem ser classes Python ou arquivos XML (em espaço de usuário ou instalados com o sistema). O carregamento segue a ordem: classes Python instaladas com o sistema, XMLs instalados com o sistema e XMLs no espaço do usuário — o usuário personaliza blocos na sua instância sem senha especial. O plugin *Library Manager* é uma extensão que cria um item de menu para gerenciar bibliotecas.

## Artefatos

O desenvolvimento no ambiente gera os artefatos descritos em [artefatos de software no Mosaicode](artefatos-mosaicode.md), que será proposto compartilhar via [protótipos](prototipacao.md).
