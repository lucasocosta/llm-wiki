---
okf_version: '0.2'
language: pt-BR
---

- [references](references/index.md) — references: 2 itens.
- [Colaboração e história da arte digital](arte-digital.md) — Origens da arte digital (Memex, Fluxus, E.A.T.-1966), interatividade artista-público (teamLab, WiiBand) e benefícios da colaboração artística.
- [Artefatos de software no Mosaicode](artefatos-mosaicode.md) — Artefatos gerados no desenvolvimento no Mosaicode: diagrama, código-fonte, aplicação e os blocos, com o fluxo de criação.
- [Colaboração em Arte Digital com o Mosaicode](colaboracao-arte-digital-mosaicode.md) — Visão geral da monografia: estudar formas de compartilhar os artefatos do Mosaicode e desenvolver ferramentas de colaboração entre seus usuários.
- [Colaboração em ambientes de software e em arte digital](colaboracao-e-interacao.md) — Ferramentas colaborativas em ambientes de software (CDEs) e as bases interdisciplinares da colaboração em arte digital.
- [Conclusão e trabalhos futuros](conclusao.md) — Recapitulação das três fases e o que ficou para o futuro: tags de versionamento em XML, gerenciador de versões, servidor online e mais mensagens de protocolo.
- [Criação em arte digital e GPL vs DSL](criacao-e-gpl-dsl.md) — Softwares de arte digital com linguagens de domínio específico; vantagens das DSLs segundo Deursen e Klint.
- [CSCW — Trabalho Cooperativo Auxiliado por Computador](cscw.md) — Definição, histórico multidisciplinar do CSCW e a distinção com groupware.
- [Ferramentas para criação de arte digital](ferramentas-criacao.md) — Suporte colaborativo existente em PureData, SuperCollider, Processing e Unity, como base de ideias para o Mosaicode.
- [Repositórios, workspace e ferramentas integradas](groupware-e-ferramentas.md) — Conceitos de repositório e workspace, características de workspace e ferramentas integradas (IDEs) e seus benefícios.
- [Modelo 3C — Comunicação, Cooperação e Coordenação](modelo-3c.md) — Os três pilares do groupware, com comunicação síncrona/assíncrona, workflow e equipes virtuais.
- [Ambiente Mosaicode](mosaicode.md) — Ambiente de programação visual para artes digitais, formado por blocos, conexões, portas e extensões, que gera código-fonte a partir de diagramas.
- [Objetivos e metodologia do trabalho](objetivos-e-metodologia.md) — Objetivos específicos do estudo e metodologia em 3 fases e 8 etapas.
- [Protocolo MCSCWP e aplicação](protocolo-mcscwp.md) — Mensagens multicast/unicast, cabeçalho do protocolo MCSCWP, entrada no grupo, heartbeat com TTL de 300 segundos.
- [Prototipação: decisões de projeto](prototipacao.md) — Chat em rede local com multicast e unicast, envio de arquivos e workspace compartilhado com pastas Shared e Received.
- [Benchmark de custo por caminho](wiki-benchmark-custo.md) — Medição de chars servidos por caminho — search ~920, read-page ~2,8k, dump do Bundle ~61,5k.
- [Busca lexical, shortlist e resolução de links](wiki-busca-links.md) — Ranking off-model que nunca devolve corpo, shortlist no work item e resolução de links relativos aplicando as regras do ADR 0001.
- [llm-wiki: visão geral do código](wiki-codigo-visao-geral.md) — Arquitetura geral: CLI como único test seam, motor determinístico sem LLM, Trecho como unidade de entrega.
- [Comandos CLI e log.md](wiki-comandos-log.md) — Comandos de ingestão, consulta e curadoria, e o log append-only legível por humanos.
- [Extração de Trechos e ingestão de código](wiki-extracao-codigo.md) — Como o motor transforma Fontes em Trechos: markdown/texto por seções, código por módulos com ordem leaves-first e âncora de símbolo qualificado.
- [Grafo de links e lint](wiki-grafo-lint.md) — Backlinks, orphans, broken-links e lint — propriedades computáveis do grafo, sem LLM.
- [Manifesto e Espelho de Fonte](wiki-manifesto-references.md) — Um manifesto YAML na raiz declara Bundle e Fontes; cada Fonte tem um Espelho em references/ com a versão que foi lida.
- [Páginas OKF e index.md](wiki-okf-paginas.md) — Leitura/escrita de páginas com frontmatter, invariantes de contribuição e geração determinística de índices.
- [Proveniência, staleness e guard](wiki-proveniencia-staleness.md) — Provenância via Git sem tocar no checkout, relatório de obsolescência, páginas sujas e o guard de escrita.
- [Uso e dados de custo](wiki-uso-custo.md) — Instrumentação de payload (usage.py) e a conta de chars/tokens por caminho.
