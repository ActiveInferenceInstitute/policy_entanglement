# Build / Run

## Lean

```bash
cd lean
lake build           # compiles every Mathlib-free module
lake clean           # purge build artefacts
lake env pwsh        # interactive Lean session with the package on the path
```

Expected output: `Build completed successfully (16 jobs).` plus
**14 boundary-form `sorry` warnings** — intentional placeholders
documented in [`../reference/lean_reference.md`](../reference/lean_reference.md).
The constructive sub-fragments `Monotonicity.lean` and
`Constructive.lean` carry only `Float`-arithmetic boundary
placeholders alongside otherwise-clean structural proofs.

### Toolchain

The package pins `leanprover/lean4:v4.29.0` via
[`../lean/lean-toolchain`](../../lean/lean-toolchain).  `lake build` uses
[elan](https://github.com/leanprover/elan) to install the right toolchain
on first invocation.

### Mathlib dependencies

**None.**  The boundary fragment is deliberately Mathlib-free.  The
expected Mathlib import surface for Phase 7 — `Mathlib.Probability.Entropy.Basic`,
`Mathlib.Analysis.SpecialFunctions.Log.Basic`,
`Mathlib.Probability.Information`, `Mathlib.LinearAlgebra.Matrix.SVD` —
is documented in [`../reference/phase7_plan.md`](../reference/phase7_plan.md).

## Python

The project uses [`uv`](https://docs.astral.sh/uv/) with PEP-735
dependency groups.  Core dependencies declared in
[`../../pyproject.toml`](../../pyproject.toml) are `numpy`, `scipy`,
`matplotlib`, `pyyaml`; the `dev` group adds `pytest`, `pytest-cov`;
the `viz` group adds `seaborn`, `networkx`, `plotly`; the `sim` group
adds `inferactively-pymdp==1.0.1` (which pulls in JAX).

### Installation

From the project root:

```bash
uv sync                                        # core + dev + viz
uv sync --group sim --group viz                # full env, with pymdp + viz
```

### Tests + coverage

```bash
cd projects/actinf_policy_entanglement_lean
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90
```

Expected output: `340 passed`, ≥ 90 % coverage on `src/`
(**97.51 %** today across the four subpackages
`lean/`, `simulation/`, `visualizations/`, `manuscript/`).

### Running scripts

```bash
uv run python scripts/generate_figures.py            # 21 PNG figures → output/figures/
uv run python scripts/simulate_pymdp.py              # pymdp harness  → output/figures/, output/simulations/
uv run python scripts/manuscript_variables.py        # JSON facts     → output/data/
uv run python scripts/inject_manuscript_variables.py # rendered MDs   → output/manuscript/
uv run python scripts/validate_outputs.py            # PNG / JSON gate
uv run python scripts/validate_manuscript.py         # token / link / variable gate
uv run python scripts/run_all.py                     # full chain in one shot
```

Each script is **idempotent** — re-running overwrites the previous
outputs.

## Pipeline (full PDF render)

The template provides a 10-stage rendering pipeline driven by `run.sh`
at the parent root:

```bash
# from the parent template root:
./run.sh --project actinf_policy_entanglement_lean --pipeline
```

Stages (per the template's default `pipeline.yaml`):

| # | Stage | What it does for this project |
|---|---|---|
| 0 | Clean | Wipe `output/` |
| 1 | Setup | Validate dependencies, discover the project |
| 2 | Infra tests | Run `tests/infra_tests/` |
| 3 | Project tests | Run `tests/` (this project's no-mocks suite) |
| 4 | Run analysis | Execute `scripts/*.py` to produce figures + variables |
| 5 | Render PDF | Concatenate `manuscript/*.md` + `preamble.md`, render to PDF |
| 6 | Validate output | Check PDF / markdown integrity |
| 7 | LLM review | Optional — disabled in `manuscript/config.yaml` |
| 8 | LLM translations | Optional — disabled |
| 9 | Copy outputs | Stage final deliverables under `output/<project>/` |

## CI

The template's GitHub Actions workflow runs:

```bash
uv run pytest projects/actinf_policy_entanglement_lean/tests/ \
    --cov=projects/actinf_policy_entanglement_lean/src \
    --cov-fail-under=90
```

If you bump the coverage floor, update [`../pyproject.toml`](../../pyproject.toml)
(`tool.coverage.report.fail_under`) to match.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `lake build` errors with `expected token` near `Π` or `λ` | reserved binder used as identifier | rename to `Pol` / `lam` |
| `lake build` reports a build cycle | accidental cross-import between `ActinfPolicyEntanglement` and `FepSketches` | remove the offending `import` |
| `ImportError: attempted relative import with no known parent package` | `from .module import X` in `src/` | use bare `from module import X` (pythonpath is `src`) |
| `coverage failed: 89.x %` | a new function landed without tests | add ≥ 2 tests for the function |
| Figure script writes nothing | `MPLBACKEND=Agg` not set, or `output/figures/` missing | scripts already set both; check working directory |
