# AGENTS.md — `tests/coverage/`

- These tests exist to close measured gaps, not to restate covered behavior.
  Add a case here only when a specific uncovered branch has no natural home in
  the module's own test file.
- The no-mocks rule applies: real arrays, real files under `tmp_path`, real
  subprocesses. No `MagicMock`, no `mocker.patch`, no `unittest.mock`.
- Run `uv run pytest tests/coverage --cov=src` and keep the aggregate floor of
  95% intact; do not lower it to make a gap test pass.
- When a gap is closed, move the test next to the module it covers if that file
  exists.
- Parent rules: [../AGENTS.md](../AGENTS.md).
