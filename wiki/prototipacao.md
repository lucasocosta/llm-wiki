---
id: prototipacao
type: Topic
title: 'Prototipação: decisões de projeto'
description: Chat em rede local com multicast e unicast, envio de arquivos e workspace
  compartilhado com pastas Shared e Received.
tags:
- prototipo
- multicast
- unicast
- chat
- workspace
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


## Decisões de projeto

Das revisões de CSCW, aplicações de comunicação e compartilhamento com o conceito do [Modelo 3C](modelo-3c.md), ferramentas aparentemente simples podem se tornar poderosas soluções de trabalho colaborativo. Pontos do design: integrar um **chat** para melhor comunicação entre os usuários (a integração de ferramentas aumenta a produtividade) e permitir o **compartilhamento dos artefatos** gerados pelo sistema, exigindo mudanças no formato atual dos arquivos.

### Modos de comunicação

Três modos de endereçamento de dados em redes:

- **Broadcast**: envia a mensagem para todos os usuários da rede;
- **Unicast**: envia a mensagem para um nó específico;
- **Multicast**: cria um grupo de mensagem de determinados indivíduos da rede.

Para o chat em grupo dentro do Mosaicode, multicast é a opção mais atraente: apenas as pessoas do grupo definido na rede interna recebem os dados. Para maior privacidade e praticidade, o chat é **peer-to-peer** (pessoa a pessoa) e todos para todos (canal multicast) — sem servidor central, via rede local.

A tela do protótipo tem: (1) histórico de conversas, (2) lista de pessoas conectadas para mensagens, (3) campo de entrada e (4) botão de enviar.

### Envio de arquivos

Funcionalidade desejada para alcançar cooperação e colaboração: escolhe-se um usuário e um arquivo (XML: um bloco ou um diagrama) e envia-se via conexão entre os dois; o receptor aceita ou não o download; salvo em uma pasta **Received**.

### Workspace compartilhado

Pasta **Shared** em cada aplicação, anunciada por multicast: cada usuário pode importar os arquivos quando quiser; o download do bloco/diagrama vai para a pasta **Received** de quem baixou. O usuário pode atualizar sua lista de arquivos compartilhados (reenviando-a a todos no canal multicast) ou pedir a lista atualizada de todos.

## Implementação

Foram criados dois protocolos de rede: **multicast** (comunicação em grupo) e **unicast** (peer-to-peer). APIs baseadas no Python 2.7 e nas bibliotecas já incorporadas ao Mosaicode: GTK 3.0 (gráfica) e BeautifulSoup (utilitário para XML). Ao final, com os requisitos de mudanças de bloco e workspace cumpridos, a importação do plugin ao sistema será fácil. Detalhes em [protocolo MCSCWP e aplicação](protocolo-mcscwp.md).
