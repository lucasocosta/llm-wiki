# 20: Fazer o conteúdo de código externo corresponder ao SHA declarado

**Status:** done
**Priority:** P1
**Blocked by:** None (can start immediately).
**Related:** [08 — Fontes de código](08-fontes-codigo.md), [19 — proveniência de código local](19-proveniencia-codigo-local.md), [spec — manifesto](../spec.md#manifesto).

## Problema

Review de `75597d6...4eb32c1`: `extract_code_source`, em `src/llmwiki/ingestion.py`, lê diretamente o checkout indicado pela localização, sem aplicar ou validar `source.commit`. A escrita registra o SHA declarado mesmo quando o texto pertence a outra revisão.

O ticket 08 exige “Fonte de código externa é pinada por SHA, sem copiar código para dentro do repositório”. O resultado atual não é reproduzível e a proveniência pode ser falsa.

## Reprodução pela CLI

1. Criar repositório externo temporário com dois commits reais A e B, alterando uma função entre eles; manter o checkout em B.
2. Declarar a Fonte externa com `repository`, `location` apontando para esse checkout e `commit` igual ao SHA de A.
3. Executar `ingest next`; comparar o texto entregue com A e B. Gravar uma página e inspecionar o Espelho.

Atual: o trabalhador recebe conteúdo de B, mas a proveniência registra A. Esperado: ler A ou recusar explicitamente a divergência antes de entregar trabalho.

## Critérios de aceitação

- [x] O texto entregue corresponde ao SHA declarado; é aceitável ler a revisão diretamente ou exigir e validar um checkout correspondente.
- [x] Divergência entre revisão declarada e conteúdo nunca gera um item de trabalho ou uma página com proveniência enganosa.
- [x] Alterações locais não commitadas em arquivos incluídos não são atribuídas silenciosamente ao SHA declarado.
- [x] SHA inexistente ou não verificável produz erro que identifica a Fonte e a revisão, sem sucesso parcial enganoso.
- [x] A operação não modifica o checkout externo nem copia a Fonte para o repositório da wiki.
- [x] Testes pela CLI cobrem checkout correspondente, checkout divergente e conteúdo local alterado, usando Git real em diretórios temporários e execução offline.

## Comments

- 2026-09-12 — Em andamento. Validação de checkout externo contra o SHA declarado e arquivos incluídos alterados.

- 2026-09-12 — Concluído. Regressões com Git real cobrem pin correto, checkout divergente, SHA inexistente, conteúdo modificado e alteração entre entrega e escrita; recusas ocorrem antes de gravar a página.
