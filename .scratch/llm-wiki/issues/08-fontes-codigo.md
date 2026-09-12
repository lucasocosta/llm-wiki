# 08: Fontes de código — allowlist, Âncora de símbolo, SHA

**What to build:** Código entra como material de leitura, não como assunto: a wiki captura por que o código existe e que decisões estão congeladas nele, em vez de virar documentação de API que envelhece a cada commit. A allowlist declarada por Fonte impede que teste, migração e código gerado inflem a wiki, e o relatório diz quantos arquivos ficaram fora, para que a exclusão não passe despercebida.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] A allowlist é declarada por Fonte de código, não globalmente
- [ ] Caminho não listado não é ingerido
- [ ] O relatório de ingestão informa quantos arquivos ficaram de fora por allowlist
- [ ] A Âncora das citações é o nome qualificado do símbolo, nunca número de linha
- [ ] O Espelho de Fonte guarda o commit SHA do arquivo lido
- [ ] Fonte de código externa é pinada por SHA, sem copiar o código para dentro do repositório
