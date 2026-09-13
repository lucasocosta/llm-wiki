# 08: Fontes de código — allowlist, Âncora de símbolo, SHA

**What to build:** Código entra como material de leitura, não como assunto: a wiki captura por que o código existe e que decisões estão congeladas nele, em vez de virar documentação de API que envelhece a cada commit. A allowlist declarada por Fonte impede que teste, migração e código gerado inflem a wiki, e o relatório diz quantos arquivos ficaram fora, para que a exclusão não passe despercebida.

**Blocked by:** 02.

**Status:** done

- [x] A allowlist é declarada por Fonte de código, não globalmente
- [x] Caminho não listado não é ingerido
- [x] O relatório de ingestão informa quantos arquivos ficaram de fora por allowlist
- [x] A Âncora das citações é o nome qualificado do símbolo, nunca número de linha
- [x] O Espelho de Fonte guarda o commit SHA do arquivo lido
- [x] Fonte de código externa é pinada por SHA, sem copiar o código para dentro do repositório

## Comments

- 2026-09-12 — Reaberto após review de `75597d6...4eb32c1`. Código local sem `commit` declarado não recebe SHA real e sua leitura falha; código externo lê o checkout sem aplicar ou validar o pin. Correções em [19 — código local](19-proveniencia-codigo-local.md) e [20 — pin externo](20-validar-pin-codigo-externo.md). O requisito de orçamento também ganha trabalho próprio em [22 — teto de Trechos](22-teto-orcamento-trechos.md).

- 2026-09-12 — Concluído. Issues 19 e 20 concluídas com commits reais e consulta pela CLI; proveniência local e pin externo verificados.
