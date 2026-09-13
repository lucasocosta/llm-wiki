---
id: protocolo-mcscwp
type: Topic
title: Protocolo MCSCWP e aplicação
description: Mensagens multicast/unicast, cabeçalho do protocolo MCSCWP, entrada no
  grupo, heartbeat com TTL de 300 segundos.
tags:
- protocolo
- redes
- mosaicode
- mcscwp
generated: '2026-09-12'
generated_by: llm-wiki
trechos:
- dfa393d4c11d576ec64a3bd3188fd4bb35e28a0aec93ed9f9647e5027535f745
source_ids:
- poc-mosaicode
source_versions:
  poc-mosaicode:
    type: pdf
    path: sources/poc-lucas-oliveira-costa.pdf
    content_hash: fb79e5be62bd146453867f80aeb829fb9f40b298b6cb731498305e11e253153d
---


Protocolos de rede são conjuntos de regras de comunicação entre dois computadores, garantindo padrão na conversa (como num diálogo onde a resposta à pergunta é esperada e indica mensagem recebida, interpretada e respondida). Os dois protocolos desenvolvidos: **multicast** (grupo) e **unicast** (peer-to-peer).

## Mensagens multicast

- **hello**: enviada para se adicionar à lista de amigos dos outros usuários, e como heartbeat (dizer que ainda está ativo no grupo);
- **goodbye**: dizer que não está mais no grupo e ser removido da lista de usuários dos demais;
- **whosthere**: perguntar quem está ativo na rede; espera-se depois dela a mensagem hello de todos do grupo;
- **sendlist**: envia a lista de arquivos contidos na pasta Shared do usuário;
- **receivelist**: pede a todos os usuários a lista atualizada da pasta Shared deles;
- **chat**: mensagem de chat em grupo, reproduzida na aba de chat em grupo.

## Mensagens unicast

- **chat**: mensagem de chat individual, reproduzida na aba referente ao usuário;
- **sendfile**: enviar um arquivo; espera-se um ok do outro usuário para iniciar a conexão de transferência;
- **ok**: confirmação para realizar transferência de dados entre dois usuários;
- **importfile**: importar um arquivo da lista de arquivos compartilhados na pasta Shared de um usuário; espera-se um ok para realizar a transferência.

## Cabeçalho do protocolo

Nome: **MCSCWP** (Mosaicode Computer Supporting Colaborate Working Protocol), versão 1.0. Cabeçalho de 6 itens:

- **Nome** do protocolo (MCSCWP);
- **Versão** em uso (1.0);
- **IP origem**: IP e porta do computador que envia;
- **IP destino**: IP e porta do computador que receberá;
- **Tipo de mensagem**: hello, goodbye, etc.;
- **Tamanho**: número de bytes dos dados.

## Aplicação

O sistema mantém, por usuário: **IP**, **Nome** e **ListaArquivos** (XML com os arquivos da pasta Shared). Ao entrar, o usuário define seu nome; então são enviadas ao grupo multicast as mensagens hello, whosthere, sendlist e receivelist — atualizando todos os integrantes com nome, IP e lista de arquivos do novo membro, e o novo membro com os dados de quem já estava conectado. Mensagens goodbye removem o remetente de todos os usuários; também são removidos os usuários cujo TTL do heartbeat (hello periódico de atividade) expirar de 300 segundos. O usuário pode enviar a lista atualizada e baixar as listas atualizadas a qualquer momento, pelo botão "Atualizar Listas". Todas as mensagens são resolvidas pela aplicação, desenvolvida na camada de aplicação de rede.
