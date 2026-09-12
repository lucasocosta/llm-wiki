---
status: accepted
---

# Armazenamento em OKF estendido, não em Markdown próprio

A wiki é armazenada no [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format) — diretório de Markdown com YAML frontmatter, `type` como único campo obrigatório — mas acrescentamos chaves próprias livremente em vez de nos limitarmos ao que o SPEC define. O formato nos dá um esqueleto já pensado para corpus mantido por agente (provenance, ciclo de vida, `index.md`/`log.md` reservados, links como arestas) e a extensão é segura porque o §11 proíbe consumidores de rejeitar chave ou `type` desconhecido.

## Considered Options

Descartamos **Markdown com frontmatter próprio**: teríamos reinventado as mesmas famílias de provenance e ciclo de vida, pior. Descartamos **conformidade estrita ao SPEC**: o `stale_after` do OKF só compara timestamp, e obsolescência de página derivada de código é comparação de commit SHA — conformidade estrita nos obrigaria a mentir sobre isso.

## Consequences

O argumento de compatibilidade com o ecossistema OKF é fraco e não deve ser usado para justificar decisões futuras: em 2026-09 o repositório canônico tinha 6 commits, autor único, nenhuma release, e o próprio README chama o agente e o viewer de "proof of concept". Adotamos o formato pelo desenho dele, não pela promessa de ferramental de terceiros.

Uma parte do OKF fica deliberadamente sem uso: Attested Computations, `executor`, `attester` e o protocolo de runtime não têm papel numa wiki de material de leitura.
