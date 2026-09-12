---
status: accepted
---

# Ingestão determinística, consulta conversacional

A escrita da wiki é orquestrada por uma CLI que nunca chama LLM: ela extrai texto, delimita Trechos, mantém o índice, valida conformidade e computa a fila de trabalho. O assistente é o trabalhador, invocado um Trecho por vez, com contexto limpo. A leitura é o oposto: conversacional, com o assistente no comando, chamando tools de busca conforme a pergunta pedir.

A razão é exaustão de contexto, não elegância. Como não chamamos API de LLM — a ferramenta roda de dentro de um assistente como Kiro, Copilot ou Claude — não controlamos quando a janela de contexto compacta. Se o estado da ingestão vive no contexto, uma sessão interrompida no meio de um PDF longo perde o que já fez, e na pior hipótese sobrescreve páginas boas com versões piores. Estado em disco e invocações estreitas tornam a ingestão retomável por construção.

## Consequences

Uma mesma página será escrita por trabalhadores que não se conhecem, porque um conceito aparece em Trechos distintos. Isso torna estrutural o *augmentation guard* observado na implementação de referência do OKF: a tool de escrita deve recusar mecanicamente escrita que apague conteúdo cuja qualidade ela não pode avaliar. Sem essa guarda, a ingestão degrada páginas em vez de enriquecê-las.

A coerência de voz de uma página tocada por vários Trechos não é resolvida na ingestão. Fica para um passe de consolidação separado, cuja unidade é a Página Suja.
