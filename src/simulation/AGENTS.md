# AGENTS.md — `src/simulation/`

`inferactively-pymdp==1.0.1`-backed POMDP simulation harness for
coupled-policy active-inference ensembles, using the `pymdp` import/API.
Companion to the analytical mirrors in `src/lean/`.

## Module map

| File | Role |
|---|---|
| `specs.py` | `StreamSpec`, `CoupledEnsembleSpec` — pure data classes (no pymdp dep) |
| `builders.py` | Deterministic Ising K-stream toy + helpers |
| `agents.py` | `pymdp.agent.Agent` adapter from `inferactively-pymdp==1.0.1` (the *only* file that imports pymdp / jax) |
| `inference.py` | Per-stream EFE / policy-posterior + λ-coupled joint + `FreeEnergyBundle` (VFE per stream, expected-EFE under posterior, joint / marginal entropy, total correlation, coupling term, action distribution) + `free_energy_curve` |
| `rollout.py` | `RolloutStep`, `Rollout`, `simulate_coupled_rollout` |
| `sweep.py` | `LambdaSweepResult`, `lambda_sweep`, `total_correlation_curve`, `marginal_trajectory` |
| `statistics.py` | Reduce a list of `FreeEnergyBundle` records to a flat `BundleSummary` and a `QuantileEnvelope` over multi-seed sweeps; emit `[[VAR:...]]`-ready scalars via `summary_to_var_dict`. |
| `logging_utils.py` | Append-only JSONL `RunLogger` for structured pymdp run records; the **only** module in this subpackage that touches disk.  Disabled with `PYMDP_RUN_LOG_DISABLED=1`. |
| `hyperparameters.py` | **Single source of truth** for every grid size, seed, sentinel-λ, rollout horizon, and observation used by the figure / sweep / variable scripts.  Mirror is auto-injected into `output/data/manuscript_variables.json` via `figure_hyperparameter_summary()`. |
| `long_horizon.py` | $T = 100$ coupled-rollout harness with habit-accumulation diagnostics and tail-window KL convergence checks. |
| `multi_k_experiments.py` | $K \in \{3, 4, 5\}$ ensemble sweeps for the multi-stream Ising case (the K > 2 generalization). |
| `revertibility.py` | $m$-projection revertibility witness: two independent code paths on $D_{\mathrm{KL}}(q\,\|\,\hat m(q)) = I(q)$. |
| `robustness.py` | One-axis, two-axis, coupling-ablation, marginal-null-control, and replicate-seed robustness sidecars. |
| `btai_baseline.py` | Branching-Time AIF MCTS-based comparison baseline (shipped §13 empirical harness). |
| `adversarial.py` | Bounded-norm adversarial-perturbation harness with analytical Lipschitz bound (§20 Q11). |
| `cross_references.py` | Prose ↔ equation ↔ Lean cross-reference registry; every public numerical witness mapped to its theorem / equation / section / Lean / Mathlib / dashboard-invariant target. Integrity gated by `tests/test_cross_references.py`. |

## Rules

* `pymdp` is **optional**; `uv sync --group sim` installs
  `inferactively-pymdp==1.0.1`, which provides the `pymdp` import/API.
  Tests skip via the `requires_pymdp` marker when missing.
* Anything that touches `pymdp.agent.Agent` lives in `agents.py`.  The
  rest of the subpackage operates on numpy and the analytical layer
  (`coupling.entangled_posterior`).
* Keep deterministic seeds in every helper that involves randomness.
* The coupled posterior layering is fixed: pymdp provides the
  *mean-field* layer (per-stream `q_pi^k`), the analytical layer adds
  the cross-stream `λ·J` / `γ·λ·K_c` factors on top.  Do not pipe pymdp's
  EFE back into `entangled_posterior` — `coupled_policy_posterior`
  already passes zero-G for that reason.
* Every grid / seed / rollout horizon used by figure scripts must be
  read from `hyperparameters.py`; never write `np.linspace(0, 6, 121)`
  inline.  The constants flow through the JSON mirror into manuscript
  prose via `[[VAR:...]]`.
* `FreeEnergyBundle` is frozen — fields are computed once in
  `free_energy_bundle(spec, obs, lam)` and consumed by the figure
  pipeline (`scripts/simulate_pymdp.py::figure_pymdp_free_energies`)
  and the test suite.  λ = 0 invariants (TC = 0, coupling = 0,
  H(q) = ΣH(q^k)) are asserted by `tests/test_simulation_free_energy.py`.
