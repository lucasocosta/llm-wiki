---
id: conclusao
type: Topic
title: Conclusão e trabalhos futuros
description: 'Recapitulação das três fases e o que ficou para o futuro: tags de versionamento
  em XML, gerenciador de versões, servidor online e mais mensagens de protocolo.'
tags:
- conclusao
- trabalhos-futuros
- versionamento
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- 4bbc56c44d69cf93d8f622e5a6b73ec4782c6c28fa8e894b893df2f3615ee972
source_ids:
- poc-mosaicode
source_versions:
  poc-mosaicode:
    type: pdf
    path: sources/poc-lucas-oliveira-costa.pdf
    content_hash: fb79e5be62bd146453867f80aeb829fb9f40b298b6cb731498305e11e253153d
---


O trabalho propôs o estudo de formas de compartilhamento dos artefatos gerados pelo Mosaicode e o desenvolvimento de ferramentas para que a colaboração fosse efetiva entre os usuários — os artefatos não são usuais e não havia regra geral de colaboração como em ferramentas estabelecidas, como o desenvolvimento em conjunto com o GitHub.

## Recapitulação por fases

1. **Estudo** (fase i): o que é trabalho colaborativo em computadores e como usar essas técnicas em sistemas voltados a arte digital; análise de exemplos do mercado de arte digital e suas ferramentas. Percepção: pequenas ferramentas com o conceito do [3C](modelo-3c.md) resolvem o problema proposto.
2. **Definição** (fase ii): o que compartilhar e as modificações no formato do sistema; definição do workspace com as pastas **Shared** e **Received** e propostas de ferramentas de comunicação **peer-to-peer** e em grupo, sem servidor centralizado ([prototipação](prototipacao.md)).
3. **Implementação** (fase iii): um protocolo de rede no Mosaicode para comunicação e compartilhamento de arquivos ([protocolo MCSCWP](protocolo-mcscwp.md)) e protótipos para uso futuro do sistema.

Com isso, os objetivos foram alcançados seguindo a metodologia estipulada no início ([objetivos e metodologia](objetivos-e-metodologia.md)).

## Trabalhos futuros

- As propostas de modificação das tags de XML ainda estão sendo analisadas para implementar as ferramentas no Mosaicode;
- Ao implementar, será necessário criar um **gerenciador de versionamento dos artefatos**, para que blocos e diagramas sejam identificados como diferentes apesar do mesmo nome;
- Expandir a ferramenta para um número maior de pessoas: criar um **servidor e repositório online** para compartilhar criações com o mundo;
- Anexar mais mensagens ao protocolo, como criar **grupos de trabalho** e workspaces compartilhados em servidor local;
- Anexar ferramentas de **controle** à ferramenta: as desenvolvidas cobriram comunicação e colaboração.

## Tags de XML propostas para blocos

O XML é marcação: tags podem ser adicionadas ao corpo para definir propriedades do bloco. As tags propostas, para evitar conflito na importação de novos blocos:

- `<author>` — o autor do bloco: nome de usuário do criador;
- `<ver>` — versão do bloco: se atualizado, a versão se incrementa para controle;
- `<date>` — data e hora de publicação do bloco;
- `<last-modified>` — data e hora da última atualização;
- `<sub-author>` — o usuário que fez a última modificação publicada.
