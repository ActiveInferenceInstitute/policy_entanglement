# Coverage gap tests

Intentional meta-tests that drive `src/` modules to ≥95% coverage without mocks.
Each file targets a domain slice; refresh line targets with:

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing -q
```

| File | Domain |
| --- | --- |
| `test_coverage_gaps_pure.py` | Pure Python branches (manuscript, lean mirrors, gates) |
| `test_coverage_push_95.py` | Orchestration and reporting entrypoints |
| `test_coverage_95_final.py` | Residual module surfaces |
| `test_coverage_extras.py` | CLI scripts and edge orchestrators |
| `test_coverage_library_gaps.py` | Library modules below floor after main suites |
| `test_coverage_final_push.py` | Last-mile branches before release |

New gap tests belong here (or a domain sibling under `tests/manuscript/`, etc.)
rather than at the `tests/` root.
