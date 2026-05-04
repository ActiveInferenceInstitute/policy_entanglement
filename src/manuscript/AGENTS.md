# AGENTS.md — `src/manuscript/`

Supporting library for assembling and validating manuscript-facing artefacts from Python (token lists, bibliography hooks, markdown rendering helpers tied to workflow around [`../manuscript/`](../manuscript/) at project root — `config.yaml`, sections, `.bib`). This **Python** tree is tooling; narrative sources remain under the sibling `manuscript/` directory consumed by Layer-1 rendering.

## Modules

| File | Role |
| --- | --- |
| `tokens.py` | Token / lexical helpers for excerpt pipelines. |
| `bibliography.py` | Bibliography bridging for Python-side citation checks. |
| `renderer.py` | Markdown/LaTeX-oriented render helpers used by tooling. |
| `registry.py` | Registry of manuscript fragments or section keys. |
| `validation.py` | Structural validation helpers before render. |

## Rules

Same as parent [`AGENTS.md`](../AGENTS.md): library boundaries documented there, no mocks in consuming tests, 90 % coverage on public APIs.

## See also

- [`README.md`](README.md)
