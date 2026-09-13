---
id: groupware-e-ferramentas
type: Topic
title: Repositórios, workspace e ferramentas integradas
description: Conceitos de repositório e workspace, características de workspace e
  ferramentas integradas (IDEs) e seus benefícios.
tags:
- workspace
- repositorio
- ide
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- c06d26510907f1118903afa355e1daeab7eeb9af3a93bfeb6b5f0c409567412e
source_ids:
- poc-mosaicode
source_versions:
  poc-mosaicode:
    type: pdf
    path: sources/poc-lucas-oliveira-costa.pdf
    content_hash: fb79e5be62bd146453867f80aeb829fb9f40b298b6cb731498305e11e253153d
---


## Repositório

Lugar onde se armazenam "coisas" — neste contexto, artefatos de software — que também são compartilhadas na rede nos casos de trabalho em grupo. No gerenciamento de um repositório de componentes é preciso armazenar diferentes componentes de um produto e todas as suas versões de forma segura: gerenciamento de versão, modelagem de produto e gerenciamento de objetos complexos (ESTUBLIER, 2000). Artefatos podem ser arquivos de texto, imagens, multimídia, ferramentas, códigos etc.

## Workspace

Espaço de trabalho onde um software, arquivo ou dado pode ser manipulado ou desenvolvido isolado de outros; uma mesma pessoa pode participar de vários workspaces, e o mesmo vale para grupos. Características desejáveis, segundo SPELLMAN et al. (1997):

- **Persistente**: continue existindo se alguém está "nele" ou não (diferente de ferramentas centradas em reuniões, onde não se deixa algo para quem entra depois);
- **Independente de localização**: pode ser acessado independentemente da localização do usuário;
- **Localização transparente**: possibilita interação com qualquer pessoa sem conhecer sua localização física;
- **Stateful (dinâmico)**: fornece meios para os usuários interagirem uns com os outros e/ou com documentos selecionados.

## Ferramentas integradas (IDEs)

Ambientes construídos para reunir em um único software as ferramentas que o desenvolvedor precisa: compiladores, linkers, bibliotecas, depuradores e, em alguns casos, controle de código-fonte, servindo como repositórios compartilhados dos artefatos de uma equipe e suportando colaboração estruturada (compartilhar, editar e mesclar arquivos coordenadamente sem sair do IDE) (HUPFER et al., 2004). Segundo Booch e Brown (2003), sistemas colaborativos valiosos podem emergir de IDEs com ferramentas aparentemente simples da metodologia [3C](modelo-3c.md). Benefícios de IDEs (OWOSENI; AKANJI, 2016): maximização da produtividade com menos esforço, redução do tempo de desenvolvimento, aplicação dos padrões do projeto ou empresa, e redução do estresse de desenvolvimento.

Esses conceitos fundamentam o [workspace compartilhado proposto no Mosaicode](prototipacao.md).
