# Ticket 04: Mensagens de erro de frontmatter apontando a causa próxima

Type: task
Status: resolved
Blocked by: 01

## Contexto

Durante o teste, o worker perdeu retrates por causa de duas mensagens:

- `:` solto em valores YAML (title/description) veio como stack do PyYAML
  ("mapping values are not allowed here") sem indicação do remédio (aspas).
- `content-file` transmitido vazio (buffer não descartado no runner) reportou
  "frontmatter must include a 'type' key", sintoma e não causa ("content-file vazio").

## Trabalho

1. Cercar o parse de frontmatter do `write-page`: erro do PyYAML → mensagem de validação
   prateada ("valor com `:` precisa de aspas; veja conteúdo em <linhas>").
2. Detetá-lo emitir e virar/mensaje explicitamente: "content-file consume apenas
   whitespace" antes da validação de chaves, citando o caminho.
3. Revação de outros caminhos de parse de frontmatter (consolidate, guard) para
   consistência de menssagens.
4. Testes com cada forma de conteúdo reprovável: YAML malformado, arquivo vazio,
   bloqueio de frontmatter sem `type`/`id`.

## Done

- Cada forma comum de conteúdo reprová dei'm erro de uma linha com causa e remédio,
  sem stack interna.

## Answer

Duas melhorias: (1) `parse_page` envelopa `yaml.YAMLError` em `PageError` com
linha + causa + remédio ("quote the value ... when it contains ':'"), sem stack
de PyYAML; (2) `cmd_write-page` distingue draft sem frontmatter (leniência,
como antes) de frontmatter malformado (erro duro com a nova mensagem), e
content-file vazio virou "content-file is empty (<path>): flush the buffer
(f.close()) ..." antes de qualquer validação de chaves. Cobertura:
`test_yaml_colon_message_has_remedy`, `test_empty_content_file_message`.
Exit code: 2 (coerente com průkaz de recusa de escrita).
