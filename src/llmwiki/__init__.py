"""llm-wiki: build and maintain an OKF-extended Markdown wiki from declared Sources.

The CLI never calls an LLM. Ingestion is deterministic and orchestrated by the
CLI; the judgement — deciding which concepts exist and writing the pages — is
done by the assistant (the "worker"), invoked one Trecho at a time. See
docs/adr/0002.
"""

__version__ = "0.1.0"
