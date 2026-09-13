# Correções da revisão das implementações

Escopo: achados da revisão desde 75597d6, incluindo os commits 4eb32c1 e 89ebb36 e as alterações locais posteriores.

Status: resolved

Os seis tickets foram corrigidos e verificados em 2026-09-13. Validação: 136 testes passaram; a mutação da exclusão de __pycache__ foi detectada pelo teste corrigido. As correções preservam o fluxo de várias escritas por Página Conceitual; hashes de Fontes diferentes precisam ser enviados em escritas separadas.

Preservar a proveniência de cada arquivo de código e Fonte contribuinte; validar os hashes recebidos; conservar os detalhes das citações; corrigir a localização do resumo de uso; tornar os testes de exclusão e manifesto observáveis pela CLI. Aplicam-se CONTEXT.md, ADRs 0001/0002 e Testing Decisions da spec original.

## Tickets

- [01 — Preservar proveniência de arquivos de código idênticos](issues/01-proveniencia-arquivos-identicos.md)
- [02 — Validar hashes de Trechos para todos os tipos de Fonte](issues/02-validar-hashes-por-fonte.md)
- [03 — Preservar os detalhes das entradas de proveniência](issues/03-preservar-detalhes-citacoes.md)
- [04 — Ler métricas de uso na raiz do manifesto](issues/04-usage-bundle-aninhado.md)
- [05 — Tornar efetivo o teste de exclusão de __pycache__](issues/05-teste-exclusao-pycache.md)
- [06 — Verificar o manifesto pelo contrato da CLI](issues/06-teste-manifesto-cli.md)
