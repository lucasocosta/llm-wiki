# Ticket 14: `llm-wiki init` com scaffolding de layout e migração

Type: task
Status: resolved
Blocked by: 13

## Contexto

Ticket 13 (resolvido para este repo, 2026-09-13) decidiu/fatuou o layout aninha:
`llm-wiki/{wiki,sources}` com `.llmwiki/` como estado derivado na raiz. O
mantenedor quer padronalização — um lugar só para a wiki no root — sem dir
surgery manual. O passo que falta é o produto virar comando: inicializar um
projeto novo (ou migrar um layout pré-123) com tudo coerente.

## Trabalho

1. `llm-wiki init [DIR]`: cria (ou detecta) manifesto com defaults
   `bundle_dir: llm-wiki/wiki`, `sources_dir: llm-wiki/sources`; cria pastas;
   nunca sobrescreve manifesto existente (refusa).
2. Gerar/auger `.gitignore` entries: `.llmwiki/` (derivados) e um comentário
   orientando versionar Bundle/Fontes — o incidente 12 mostrou que sem
   scaffolding o commit acidental acontece.
3. Migração: `--migrate` movendo bundle/sources declarados no manifesto atual
   para o layout padrão, atualizando o manifesto e re-carimbando as páginas
   (`source_versions` paths mudam; determinismo dos hashes preserva os
   Trechos). `stale report` deve sair limpo pós-migração.
4. Testes: init em diretório vazio; init idempotente recusa overwrite;
   migração em fixture com páginas existentes mantém busca e proveniência;
   caminhos dos Espelhos atualizados.

## Done

- Nova wiki começa com `llm-wiki init` num comando; layoutპ difusão resolv ужас;
  migração de um repo como este (nível pré-13) é scriptada pela CLI.

## Answer

Implementado e testado (`tests/test_25_init_migration.py`; suite 141 passed):

- **`llm-wiki init [DIR]`** — scaffolding autocontido `DIR/llm-wiki/{llm-wiki.yml, wiki, sources}`; recusa sobrescrever (exit 2, mensagem de domínio); garante regra `.llmwiki/` no `.gitignore` (aparece só se ausente) — proteção direta ao incidente 12;
- **`init --migrate`** — move o layout flat (`wiki/`, `sources/`, `.llmwiki/` na raiz) para dentro de `llm-wiki/`, carrega a telemetria (`usage.jsonl`) junto, reescreve o manifesto (`-C llm-wiki` a partir daí), regenera e recusa colisões (`llm-wiki/` existente com conteúdo). Validado ao vivo em fixture e na sua reingestão do zero (o repo real já vive no layout migrado);
- **`sources list-trechos [SOURCE] [--with-text]`** (ticket 15 na implementação junto) — caminho sancionado para enumerar todos os Trechos atuais (incluindo carimbados), substituindo o acesso interno ao extractor; foi o caminho usado na reingestão de zero desta validação.

Limitação restante: migração de Fontes `code` com paths não padrão é a reescrita heurística (relpath do checkout) — caso externo (`repository`+`commit`) continua intacto por desenho.
