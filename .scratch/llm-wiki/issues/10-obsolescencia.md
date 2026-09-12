# 10: Obsolescência por hash de arquivo e por SHA de commit

**What to build:** A wiki passa a saber quando ficou desatualizada, e sabe com exatidão em vez de por chute de calendário. Página derivada de arquivo fica Página Obsoleta quando o hash do conteúdo muda; página derivada de código, quando o commit daquele arquivo muda. Quem lê uma página obsoleta é avisado junto com o conteúdo, para qualificar a resposta em vez de afirmar algo desatualizado com confiança.

**Blocked by:** 07, 08.

**Status:** ready-for-agent

- [ ] Página derivada de arquivo fica obsoleta quando o hash do conteúdo muda
- [ ] Página derivada de código fica obsoleta quando o commit daquele arquivo muda
- [ ] A ferramenta relata o que mudou na Fonte desde a derivação
- [ ] Quem lê uma página obsoleta recebe o aviso junto com o conteúdo
- [ ] A verificação é disparada pela presença de proveniência, não pelo `type`
- [ ] Página sem proveniência verificável não é reportada como obsoleta nem como atual
