---
id: criacao-e-gpl-dsl
type: Topic
title: Criação em arte digital e GPL vs DSL
description: Softwares de arte digital com linguagens de domínio específico; vantagens
  das DSLs segundo Deursen e Klint.
tags:
- dsl
- gpl
- linguagens
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 88f1a81cd21ea4c75a86951c4c25364b5b50002fcf488268ce90e7c270040190
source_ids:
- poc-mosaicode
source_versions:
  poc-mosaicode:
    type: pdf
    path: sources/poc-lucas-oliveira-costa.pdf
    content_hash: fb79e5be62bd146453867f80aeb829fb9f40b298b6cb731498305e11e253153d
---


## Criação em arte digital

A criação de arte digital geralmente usa softwares de domínio específico: Photoshop (visual/imagem), Audacity (músicas e sons), Openshot (vídeo). Também há ferramentas onde se **programa a execução** para obter os artefatos: PureData, SuperCollider, Processing e o próprio [Mosaicode](mosaicode.md) — com linguagens desenvolvidas especificamente para sua aplicação.

## GPL vs DSL

- **GPL** (General-Purpose Language): linguagens de propósito geral, consolidadas, para aplicações dos mais diversos tipos e áreas — C, Java entre outras.
- **DSL** (Domain-Specific Language): linguagens criadas para determinados tipos de aplicações, para melhorar o rendimento tanto do programador quanto da aplicação desenvolvida.

Dilema de projeto: usar linguagens de uso geral consolidadas ou criar uma linguagem de domínio específico? Segundo MERNIK; HEERING; SLOANE (2005), DSLs oferecem ganhos substanciais em expressividade e facilidade de uso em seu domínio de aplicação; entretanto, seu desenvolvimento é trabalhoso, exigindo conhecimento do domínio e de desenvolvimento de linguagens.

## Vantagens das DSLs (DEURSEN; KLINT, 2002)

- Expressão no próprio idioma de contexto e nível de abstração do domínio: especialistas podem entender, validar, modificar e desenvolver programas sozinhos;
- Programas concisos, auto-documentáveis e em grande parte reutilizáveis para outros propósitos (reuso);
- Aumento de produtividade, capacidade de manutenção, confiabilidade e portabilidade;
- Incorporação do conhecimento do domínio na linguagem, com conservação e reuso desse conhecimento;
- Validação e otimização no nível de abstração do domínio;
- Melhor testabilidade por serem linguagens de alto nível.

Cada ferramenta é examinada em [ferramentas para criação de arte digital](ferramentas-criacao.md).
