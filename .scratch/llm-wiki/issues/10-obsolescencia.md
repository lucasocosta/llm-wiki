# 10: Obsolescência por hash de arquivo e por SHA de commit

**What to build:** A wiki passa a saber quando ficou desatualizada, e sabe com exatidão em vez de por chute de calendário. Página derivada de arquivo fica Página Obsoleta quando o hash do conteúdo muda; página derivada de código, quando o commit daquele arquivo muda. Quem lê uma página obsoleta é avisado junto com o conteúdo, para qualificar a resposta em vez de afirmar algo desatualizado com confiança.

**Blocked by:** 07, 08.

**Status:** done

- [x] Página derivada de arquivo fica obsoleta quando o hash do conteúdo muda
- [x] Página derivada de código fica obsoleta quando o commit daquele arquivo muda
- [x] A ferramenta relata o que mudou na Fonte desde a derivação
- [x] Quem lê uma página obsoleta recebe o aviso junto com o conteúdo
- [x] A verificação é disparada pela presença de proveniência, não pelo `type`
- [x] Página sem proveniência verificável não é reportada como obsoleta nem como atual

## Comments

- 2026-09-12 — Reaberto após review de `75597d6...4eb32c1`. Reingerir uma página atualiza o Espelho compartilhado e esconde a obsolescência das outras; código local sem SHA falha durante a consulta. Correções em [17 — versão por página](17-versao-fonte-por-pagina.md) e [19 — código local](19-proveniencia-codigo-local.md). A [spec](../spec.md#armazenamento) esclarece onde registrar a versão usada na derivação. A validação deve usar o estado realmente persistido pela CLI, conforme [23 — adequar testes](23-testes-pelo-contrato-cli.md).

- 2026-09-12 — Concluído. Issues 17 e 19 concluídas; versões por página/arquivo, avisos na leitura e relatórios de histórico desconhecido validados pela CLI.
