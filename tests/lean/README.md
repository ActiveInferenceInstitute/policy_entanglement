# `tests/lean/` — Lean boundary-fragment smoke tests

This directory holds the Python-side tests that exercise the Lean 4
boundary fragment under
[`../../lean/`](../../lean/).  Their job is to keep the *Python
view* of the Lean codebase honest: the hygiene budget, the lake
build, and the structural invariants that every other test in
`tests/` implicitly assumes are still true.

## What lives here

| File | Purpose |
|---|---|
| `test_lean_build.py` | Runs `lake build` as a subprocess and asserts a green exit, scans every `.lean` file under `lean/ActinfPolicyEntanglement/` and `lean/FepSketches/`, and fails if any of: a strict `sorry`, an explicit `axiom`, or any of `unsafe`/`partial`/`noncomputable` is found in the boundary fragment. |

## When to run

Locally:

```bash
uv run pytest tests/lean/test_lean_build.py -v
```

The test is also part of the default `tests/` discovery, so a full
`uv run pytest tests/` runs it.  Allow ~30–60 s for the lake compile
step on a cold build (subsequent runs hit the `lean/.lake/` cache and
finish in a few seconds).

## Why a Python test calls into a Lean build

The pipeline is multi-language by design (Python ↔ Lean ↔ manuscript),
and the load-bearing invariant of the framework is that the Lean
fragment ships **zero strict `sorry`, zero axioms beyond stock Lean,
and zero `unsafe` / `partial` / `noncomputable`** declarations.
Surfacing that invariant as a Python test makes it visible to the same
CI gate that exercises `src/`: a regression on either side fails the
same `pytest` run.

The hygiene gate is also exposed as the standalone script
[`../../scripts/build_lean.py`](../../scripts/build_lean.py); the two
must agree on what counts as a violation.  When you tighten the
hygiene budget (e.g. extending the scan to a new keyword), edit
**both** places.

## Adding a new Lean-side smoke test

1. Add the test file as `test_<topic>.py` in this directory.
2. Use `subprocess.run(["lake", "build", ...], cwd=LEAN_DIR)` for the
   build step — do not mock or shell-substitute.  Tests must observe
   what the actual Lean toolchain reports.
3. Mark long-running cases with `@pytest.mark.slow` so the fast loop
   (`pytest -m "not slow"`) stays sub-minute.
4. Do not delete the `lean/.lake/` cache from a test — a clean build
   can take many minutes and the cache is shared with developer
   workflows.

## See also

* [`../../lean/AGENTS.md`](../../lean/AGENTS.md) — Lean track rules.
* [`../../lean/ActinfPolicyEntanglement/AGENTS.md`](../../lean/ActinfPolicyEntanglement/AGENTS.md) — per-module conventions.
* [`../../scripts/build_lean.py`](../../scripts/build_lean.py) — the CI-level hygiene gate.
* [`../README.md`](../README.md) — the broader test suite.
