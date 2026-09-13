---
id: ferramentas-criacao
type: Topic
title: Ferramentas para criação de arte digital
description: Suporte colaborativo existente em PureData, SuperCollider, Processing
  e Unity, como base de ideias para o Mosaicode.
tags:
- ferramentas
- puredata
- supercollider
- processing
- unity
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- db789f4584e33875319b737f0894de530e76372e46880367113fa0d9b8e1fc95
source_ids:
- poc-mosaicode
source_versions:
  poc-mosaicode:
    type: pdf
    path: sources/poc-lucas-oliveira-costa.pdf
    content_hash: fb79e5be62bd146453867f80aeb829fb9f40b298b6cb731498305e11e253153d
---


Levantamento de softwares de criação de arte digital e seu suporte ao trabalho cooperativo, de onde se extraem ideias para o cenário do Mosaicode:

## PureData

Linguagem de programação visual para desenvolvedores de multimídia; muito em comum com o Mosaicode por ter ambiente gráfico com componentes pré-definidos e ser expansível por plugins. TSOUKALAS (2011) criou um fluxo de colaboração usando PD como framework; por PD não possuir ferramentas de colaboração, sugere funcionalidades conforme as experiências vividas:

- **Post-it**: estrutura de edição de texto com histórico e assistência possível de imagem/vídeo;
- **TODO**: lembrete de informação com avisos de janela flutuante por patch e sub-patch;
- **Structure Chart**: diagramas de sub-patches e abstrações incluídas em um patch, com rastros de conexões não existentes entre patches (como enviar-receber);
- **Controle de Log**: visualização/log de dados minerados de entrada e de qual usuário selecionou as variáveis, para investigação e experimentação de parâmetros.

## SuperCollider

Plataforma de síntese de áudio e composição algorítmica (linguagem de programação musical + servidor), extensível, usada principalmente em **live-coding**: em tempo de execução alteram-se parâmetros criando diferentes sons, tornando performances interativas. Extensões de performance colaborativa:

- **TROOP** (KIRKBRIDE, 2017): editor/ambiente cooperativo para colaborar simultaneamente no mesmo código de máquinas separadas; open-source (Python 2 e 3); todos compartilham o mesmo código, cada usuário com uma cor, e relógio do servidor compartilhado — a sincronização dos dispositivos é essencial;
- **SuperCopair** (JUNIOR; LEE; ESSL, 2015): colaboração de código pelo SuperCollider através da nuvem, com Pusher como serviço; compartilha o mesmo código e pode desenvolver/tocar/parar a música de três maneiras: somente no seu sistema, somente no sistema dos amigos ou em todos os sistemas.

## Processing

"Caderno de esboços" (*sketchbook*) de software e linguagem para aprender a codificar no contexto das artes visuais; desde 2001 promove a alfabetização em software nas artes visuais e a visual dentro da tecnologia, usada por dezenas de milhares de estudantes, designers, artistas, pesquisadores e amadores. A princípio sem ferramentas de colaboração, mas por ser extensível: Joel Moniz integrou-a ao GitHub com o plugin **Git Manager**, instalável pelo gerenciador de plugins do próprio ambiente. Funcionalidades: git init, commit, push, pull, revert, reset, log e status — as facilidades Git integradas ao ambiente.

## Unity

Ferramenta de desenvolvimento gráfico para simuladores, jogos, filmes, projetos arquitetônicos etc., com **Assets** pré-fabricados (texturas, scripts etc.) distribuídos pela Asset Store (pagos e gratuitos). Oferece o **Collab** (ativo do Unity 2017.1 em diante): pequenas equipes salvam, compartilham e sincronizam projetos em nuvem, com Cloud Build — desenvolvido para dar suporte a times multidisciplinares (desenvolvedores, artistas, especialistas de som e vídeo). Proprietário: sem mais detalhes técnicos públicos.

## Mosaicode

Ambiente de programação visual para artistas desenvolverem aplicações; à época, ainda não possuía nenhuma ferramenta de colaboração desenvolvida — lacuna que os [protótipos](prototipacao.md) pretendem preencher.
