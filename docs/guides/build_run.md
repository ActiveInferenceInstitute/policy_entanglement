# Build / Run

## Lean

```bash
cd lean
lake build           # compiles every Mathlib-free module
lake clean           # purge build artifacts
lake env pwsh        # interactive Lean session with the package on the path
```

Expected output: `Build completed successfully (22 jobs).` with
**0 strict `sorry`, 0 axiom, 0 unsafe/partial/noncomputable, 0 Mathlib
imports** — the 17 boundary submodules under
[`../../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/)
(Basic, BernoulliToy, Constructive, **Convexity** (round-2),
Coupling, Decomposition, FreeEnergy, Geometry, Heterogeneous,
JointDist, **MarkovBlanket** (round-2), Monotonicity, Scalar, Spectral,
**SpectralWitnesses** (round-3), **ConnectionsWitnesses** (round-3),
`FloatRealResidualWitness`)
all compile and type-check on stock Lean 4 v4.29.0. The substantive
stock-Lean algebraic subset is proved in the boundary fragment; analytic
content outside the stock-Lean boundary (KL chain rule, SVD-based rank,
real-analytic continuity, tensor-train rank envelopes, measure
tightness, recursive Bellman) is exposed as **witness-consuming
theorems** whose witnesses are supplied via the `CommScalar` typeclass /
separate MathlibProofs layer, rather than `sorry` placeholders.  The fragment exposes **76 public theorems /
lemmas**, **11 structures**
(round-1 `BoundedQuadraticTax`, `SmallLambdaTolerance`; round-2
`FreeEnergyConvexityWitness`, `LocalConcavityAtZero`,
`MarkovBlanketSeparationWitness`; round-3
`UpperSemicontinuousRankWitness`, `SparsityRankEnvelope`,
`HierarchicalConcentrationWitness`, `SophisticatedInferenceEmbedding`;
round-5 `PythagoreanWitness`; Float↔ℝ scaffold `FloatRealResidualWitness`), **39 defs**, **126 total declarations** (76 + 39 + 11).  The hygiene budget is
enforced by
[`../../scripts/build_lean.py`](../../scripts/build_lean.py) and the
`tests/lean/test_lean_build.py` smoke gate.

### Toolchain

The package pins `leanprover/lean4:v4.29.0` via
[`../lean/lean-toolchain`](../../lean/lean-toolchain).  `lake build` uses
[elan](https://github.com/leanprover/elan) to install the right toolchain
on first invocation.

### Mathlib dependencies

**None.**  The boundary fragment is deliberately Mathlib-free.  The
expected Mathlib import surface for the witness-payload-discharge
plan — `Mathlib.Probability.Entropy.Basic`,
`Mathlib.Analysis.SpecialFunctions.Log.Basic`,
`Mathlib.Probability.Information`, `Mathlib.LinearAlgebra.Matrix.SVD`,
`Mathlib.Topology.Semicontinuous`, `Mathlib.MeasureTheory.Measure.Tight`
— is documented in
[`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).
After round 3, the roadmap is a payload-discharge plan (moving each
`witness` row to `proved` by importing its analytic content from
Mathlib), not a coverage plan — every manuscript theorem already has
a live Lean companion in the boundary fragment.

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
uv sync --group sim --group viz                # full env, with inferactively-pymdp==1.0.1 + viz
```

### Tests + coverage

```bash
cd projects/actinf_policy_entanglement_lean
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=95
```

Expected output: live collection count from `output/reports/test_results.json`, ≥ 95 % coverage
on `src/` across the four subpackages `lean/`,
`simulation/`, `visualizations/`, `manuscript/`.  Round-3 added
35 tests on top of the round-2 baseline, including lock-down tests
for the new `SpectralWitnesses.lean` and `ConnectionsWitnesses.lean`
modules (asserted indirectly via
`test_manuscript_variables_pipeline.py::test_lean_structure_count_is_eleven`,
which now pins `lean_structure_count == 11`); the round-3 sims
(`simulate_multi_k.py`, `simulate_long_horizon.py`,
`simulate_revertibility.py`) and the 47 dashboard invariants are also
locked down.

### Running scripts

```bash
uv run python scripts/build_lean.py                  # lake build + sorry/axiom/unsafe budget gate
uv run python scripts/generate_figures.py            # 15 headline analytical PNGs (Mathlib-free analytical figures only; see scoping note below) → output/figures/
uv run python scripts/manuscript_variables.py        # JSON facts → output/data/manuscript_variables.json
uv run python scripts/dump_archetypes.py             # K=2 Schmidt archetype CSV → output/data/ising_archetypes.csv
uv run python scripts/parameter_sweep.py             # configured λ sweep CSV → output/data/parameter_sweep.csv
uv run python scripts/simulate_pymdp.py              # inferactively-pymdp==1.0.1 / pymdp harness (14 PNGs + free-energy bundle CSV) → output/figures/, output/simulations/
uv run python scripts/simulate_multi_k.py            # configured multi-K Ising sweep (3 PNGs + summary JSON) → output/figures/, output/data/multi_k_summary.json
uv run python scripts/simulate_long_horizon.py       # configured long-horizon rollout (2 PNGs + summary JSON) → output/figures/, output/data/long_horizon_summary.json
uv run python scripts/simulate_revertibility.py      # round-3 m-projection KL identity sweep (1 PNG + summary JSON) → output/figures/, output/data/revertibility_summary.json
uv run python scripts/simulate_robustness.py         # robustness / ablation / replicate / threshold-sensitivity sidecars
uv run python scripts/simulate_btai.py               # shipped BTAI baseline sidecar + figure
uv run python scripts/simulate_adversarial.py        # shipped adversarial sweep sidecar + figure
uv run python scripts/build_dashboard.py             # interactive multi-view dashboard + plaintext invariants (47 invariants) → output/web/, output/reports/
uv run python scripts/generate_index.py              # auto-regenerate manuscript/INDEX.md from registry
uv run python scripts/generate_theorem_map.py        # auto-regenerate per-theorem four-track wiring table
uv run python scripts/inject_manuscript_variables.py # rendered MDs with token substitution → output/manuscript/
uv run python scripts/validate_outputs.py            # PNG / JSON / CSV gate
uv run python scripts/validate_manuscript.py         # token / link / variable / range gate
uv run python scripts/regression_gate.py             # compare current run vs scripts/regression_baseline.json

# Re-check gate metrics without re-running the full pytest suite (uses existing test_results.json):
REGRESSION_GATE_USE_EXISTING_TEST_REPORT=1 uv run python scripts/regression_gate.py
uv run python scripts/run_all.py                     # canonical order from scripts/run_all.py
                                                     # (live count exposed as [[VAR:run_all_script_count]])
uv run python scripts/run_all.py --with-pdf          # full pipeline plus PDF render/validation
uv run python scripts/run_all.py --with-pdf --with-mathlib  # release path incl. optional MathlibProofs gate
uv run python scripts/validate_pdf.py                # PDF text / TeX / LaTeX log / margin gate
uv run python scripts/readiness_report.py            # write output/reports/release_readiness.md
```

Each script is **idempotent** — re-running overwrites the previous
outputs.

### Figure-count scoping

The number of PNG artifacts depends on which slice of the pipeline
you run.  Three different counts appear in the docs because they
report three different scopes:

| Scope | Count | What's included |
|---|---|---|
| `scripts/generate_figures.py` (headline analytical) | **15** | Pure-numpy analytical figures produced from the Mathlib-free closed forms (15 `figure_*` functions).  Does *not* include `simulate_pymdp.py` or the round-3 sim outputs. |
| `scripts/generate_figures.py` + `scripts/simulate_pymdp.py` (analytical + pymdp dashboards/joints) | **29** | Adds the pymdp grounding suite: total-correlation curve, three joint snapshots (`pymdp_joint_lambda_{0,2,4}`), coupled rollout, plus the free-energy dashboards (`pymdp_vfe_decomposition`, `pymdp_efe_under_posterior`, `pymdp_entropy_decomposition`, `pymdp_action_distribution`, `pymdp_summary_panel`, `pymdp_action_entropy`, `pymdp_kl_to_lambda_zero`, `pymdp_marginal_entropy_per_stream`, `pymdp_free_energy_panel`). |
| `scripts/generate_figures.py` + `scripts/simulate_pymdp.py` + round-3 sims (`simulate_multi_k.py`, `simulate_long_horizon.py`, `simulate_revertibility.py`) | **35** | Adds the round-3 experiments: `multi_k_total_correlation`, `multi_k_aligned_mass`, `multi_k_tt_rank_profile`, `long_horizon_marginals`, `long_horizon_steady_state`, `revertibility_witness`. |
| Figure suite through `scripts/simulate_robustness.py` | **44** | Adds the robustness expansion: TC envelopes, half-saturation, decomposition residuals, coupling ablation, marginal-null control, interaction robustness, long-horizon replicate envelope, seed diagnostics, and threshold sensitivity. |
| Full figure suite including `scripts/simulate_btai.py` and `scripts/simulate_adversarial.py` | **46** | Adds the shipped BTAI baseline panel and adversarial-perturbation panel. |
| `scripts/simulate_gnn.py` | 1 diagnostic PNG | Writes `gnn_bernoulli_roundtrip.png`; validated as an output and discussed in S08, but not registered as a numbered manuscript figure. |
| `manuscript/refs/labels.yaml::figures` (all registry entries) | **46** | Every paper-facing figure registered for cross-reference; auto-derived via `len(labels.figures)`. The GNN diagnostic PNG is validated separately, outside the numbered figure registry. |

The 15 / 29 / 35 / 44 / 46 paper-facing counts, the extra GNN
diagnostic PNG, and the 46 registry total should *not* be reconciled
into one number — they document distinct delivery surfaces.  The
authoritative paper-facing registry is
[`manuscript/refs/labels.yaml::figures`](../../manuscript/refs/labels.yaml).

Three of the scripts above are *utility* steps consumed inside
`run_all.py`:

| Script | What it produces | Why it's separate |
|---|---|---|
| `dump_archetypes.py` | `output/data/ising_archetypes.csv` (17 λ values × Schmidt modes for the K=2 Ising toy) | Independent CSV artifact for downstream tools; called from `run_all.py` |
| `parameter_sweep.py` | `output/data/parameter_sweep.csv` (configured `PARAMETER_SWEEP_LAMBDAS` rows × 13 columns: closed-form / empirical MI, free energy at three utility levels, joint / marginal entropy, Schmidt rank, entanglement entropy, phase tag) | Reproducibility artifact + sanity rail for Lean proofs; grid is sourced from `simulation.hyperparameters.PARAMETER_SWEEP_LAMBDAS` |
| `generate_index.py` | `manuscript/INDEX.md` regenerated from the section registry | Keeps the ToC in sync with `manuscript/refs/labels.yaml` so a section rename only requires a registry edit |

## Project-local PDF and readiness gates

For this project, prefer the local wrappers:

```bash
uv run python scripts/build_pdf.py
uv run python scripts/validate_pdf.py
make readiness
```

`build_pdf.py` regenerates the injected manuscript, combines the
rendered sections, and runs local Pandoc/XeLaTeX/BibTeX rendering.
`validate_pdf.py` scans the combined PDF text, TeX, LaTeX log, and
compact-margin contract. `make readiness` runs the full project gates,
then writes `output/reports/release_readiness.md`.

## Legacy Template Pipeline (Not Required)

Older checkouts could be rendered through an external template pipeline.
This standalone checkout does not require that path; use the local
commands above for release PDF work. If you intentionally run the
external template pipeline, treat it as an integration check outside the
project-local release contract:

```bash
# from the parent template root:
./run.sh --project actinf_policy_entanglement_lean --pipeline
```

Stages (per the template's default `pipeline.yaml`):

| # | Stage | What it does for this project |
|---|---|---|
| 0 | Clean | Wipe `output/` |
| 1 | Setup | Validate dependencies, discover the project |
| 2 | Infra tests | Run the parent-template infra suite at `../../tests/infra_tests/` (relative to this project dir; **not** project-local — it lives at the parent-template root, not under `projects/actinf_policy_entanglement_lean/`) |
| 3 | Project tests | Run this project's `tests/` (its no-mocks suite, under `projects/actinf_policy_entanglement_lean/tests/`) |
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
    --cov-fail-under=95
```

If you bump the coverage floor, update [`../pyproject.toml`](../../pyproject.toml)
(`tool.coverage.report.fail_under`) to match.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `lake build` errors with `expected token` near `Π` or `λ` | reserved binder used as identifier | rename to `Pol` / `lam` |
| `lake build` reports a build cycle | accidental cross-import between `ActinfPolicyEntanglement` and `FepSketches` | remove the offending `import` |
| `ImportError: attempted relative import with no known parent package` | running a module outside the package context, or `from .module import X` in a script | use namespaced imports from the `src/` root, e.g. `from lean.coupling import X` or `from simulation.specs import X` |
| `coverage failed: 89.x %` | a new function landed without tests | add ≥ 2 tests for the function |
| `lake build` exits with `13 jobs`, `17 jobs`, or `19 jobs` instead of `21` | stale Lean cache from before `SpectralWitnesses.lean` / `ConnectionsWitnesses.lean` (round 3) or `Convexity.lean` / `MarkovBlanket.lean` (round 2) landed | `lake clean && lake build` |
| Figure script writes nothing | `MPLBACKEND=Agg` not set, or `output/figures/` missing | scripts already set both; check working directory |
