# AGENTS.md — `src/manuscript/output_gates/`

- Add a required figure or variable to `constants.py` only; validators read the
  lists from there.
- A validator reads the real artifact under `OUTPUT_DIR` and raises on a missing
  or malformed file. Do not return a default on absence.
- Keep the package free of mocks and of time-dependent checks; tests use real
  files under `tmp_path`.
- Run `uv run pytest tests/ --cov=src --cov-fail-under=95` after a change here.
- Parent rules: [../AGENTS.md](../AGENTS.md).
