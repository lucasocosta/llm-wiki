# Ticket 07: Extração de código deve rejeitar arquivo não decodificável

Type: task
Status: resolved
Blocked by: 01

## Contexto (sessão 2 — wiki de código)

Com `allowlist: ["."]`, o scan incluiu os binários de `__pycache__` (`.pyc`) e a fila
estourou durante `order_leaves_first`:

    File "src/llmwiki/code.py", line 145, in order_leaves_first
        src = f.read_text(encoding="utf-8")
    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xcb ...

Erro crudo do Python, sem `IngestionError` e com stack — viola a postura da CLI
(erros de domínio sem stack, via `CommandError`/`IngestionError`). A contagem de
exclusões (`excluded_by_allowlist`) existiu, mas nada protege o工作者 de allowlist
demasiado ampla.

## Trabalho

1. Em `scan_code_source` (ou no primeiro uso do conteúdo), arquivos ilegíveis como
   UTF-8 devem: (a) ser contados como excluídos com justificativa no `ingest report`,
   ou (b) virar `IngestionError` com mensagem de domínio ("arquivo não-UTF-8 na
   allowlist: <path>").
2. Definir e repetir o teste: fixture com binário incluído pela allowlist e saída
   esperada de report/fila/documentação conforme opção.
3. Nice-to-have: ignorar artisticamente diretórios de cache (`__pycache__`) por padrão,
   documentado na skill/reference.

## Done

- `ingest queue`/`report` com binário na allowlist dá erro de domínio ou exclusão
  justificada; nunca mais uma stack cruda do Python.

## Answer

`scan_code_source` agora: (1) pula `.git` e `__pycache__` sempre; (2) valida
UTF-8 de cada arquivo que casou com a allowlist e move o ilegível para
`excluded_unreadable` (justificado no `ingest report`) em vez de estourar
`UnicodeDecodeError` em `order_leaves_first`. Cobertura:
`test_binary_files_excluded_unreadable_and_reported`,
`test_pycache_skipped_entirely`.
