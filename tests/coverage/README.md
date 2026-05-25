# Coverage gap tests

Intentional meta-tests that drive `src/` modules to ≥95% coverage without mocks.
Each file targets a domain slice; refresh line targets with:

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing -q
```

| File | Domain |
| --- | --- |
| `test_manuscript_coverage.py` | Manuscript validation, bibliography, figures, output gates |
| `test_orchestration_coverage.py` | Orchestration, regression gate, readiness, cross-refs, CLI scripts |
| `test_dashboard_coverage.py` | `dashboard_types` and `_interactive_dashboard_local` |

New gap tests belong here (or a domain sibling under `tests/manuscript/`, etc.)
rather than at the `tests/` root.
