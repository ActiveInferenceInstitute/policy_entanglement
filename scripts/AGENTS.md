# AGENTS.md — `scripts/`

## Constitution (thin-orchestrator rules)

1. **No business logic.**  If a function does math, it belongs in
   [`../src/`](../src/), not here.  This file should be the script's
   *only* logic-bearing layer:
   ```python
   results = src_module.compute(...)
   plt.plot(results)
   plt.savefig(out)
   print(out)
   ```
2. **One script = one workflow.**  Don't bundle independent
   workflows into a single script.  If you'd run them at different
   cadences, they should be different scripts.
3. **Return / print output paths.**  The pipeline collects manifest
   entries by reading stdout.  Print one path per line, no commentary.
4. **Headless matplotlib.**  Set `MPLBACKEND=Agg` before importing
   `pyplot`.
5. **Deterministic outputs.**  Fix seeds; don't use `time` or process
   IDs in filenames.
6. **Output paths under `../output/`.**  This directory is disposable;
   never write into `src/`, `tests/`, or `manuscript/`.

## Adding a script

1. Create `scripts/<verb>_<noun>.py` (e.g. `generate_figures.py`,
   `compute_archetype_table.py`).
2. Top-of-file boilerplate:
   ```python
   import os, sys
   from pathlib import Path
   os.environ.setdefault("MPLBACKEND", "Agg")
   THIS_DIR    = Path(__file__).resolve().parent
   PROJECT_ROOT = THIS_DIR.parent
   sys.path.insert(0, str(PROJECT_ROOT / "src"))
   ```
3. Imports go after the `sys.path` insert (use `# noqa: E402`).
4. End with `if __name__ == "__main__": main()`.
5. Update [`README.md`](README.md) with the new script's row.

## Common workflows

| Want to … | Edit |
|---|---|
| add a manuscript figure | `generate_figures.py` |
| compute in-text variables | `manuscript_variables.py` |
| publish a CSV table | new script `compute_<table>.py` writing to `../output/data/` |

## Anti-patterns

* Hard-coding numerical computations inline (do them in `src/`).
* Writing intermediate `.npy` files into the project tree (use
  `tmp_path` or `output/`).
* Printing logs / debug output mixed with output paths (the
  pipeline parses stdout — keep it path-only).
