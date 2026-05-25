# pymdp 1.0.1 POMDP simulation harness

The `simulation` subpackage under `src/simulation/` exercises the
manuscript's λ-deformation framework inside a fully grounded POMDP —
turning the closed-form algebra of `lean/coupling.py` and the
analytical decomposition theorem into a runnable end-to-end pipeline.

The harness is intentionally layered:

1. **`simulation/specs.py`** — pure-NumPy record types
   (`StreamSpec`, `CoupledEnsembleSpec`).  No pymdp dependency, so
   they can be constructed and validated on every CI lane.
2. **`simulation/builders.py`** — deterministic constructors for the
   K-stream Ising toy and helpers for the `A`/`B` matrices that mirror
   the Bernoulli example in the manuscript (`§6`).
3. **`simulation/agents.py`** — pymdp 1.0.1 `Agent` adapter; the
   *only* module that imports `pymdp`/`jax`.  Gracefully degrades
   when the `sim` group is not installed.
4. **`simulation/inference.py`** — per-stream EFE / policy-posterior
   plus the λ-coupled joint via `coupling.entangled_posterior`.
5. **`simulation/rollout.py`** — deterministic `simulate_coupled_rollout`
   driving `K` agents through `T` time steps under a fixed seed.
6. **`simulation/sweep.py`** — λ-sweep aggregation (one
   `LambdaSweepResult` per λ value) and `total_correlation_curve`.

## Install

`inferactively-pymdp==1.0.1` is the optional package dependency surfaced
via the `sim` group; it provides the `pymdp` import/API used below:

```bash
uv sync --group sim --group viz   # pymdp + matplotlib helpers (full suite)
uv sync                           # core only (Lean / closed-form analytical track; pymdp tests skip)
```

The default stream count is **K = 2** for the Ising toy
(`make_ising_ensemble(num_streams=2, ...)`); higher K is supported and the
configured multi-K sweep is exercised by
[`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py),
emitting the figures `multi_k_total_correlation`,
`multi_k_aligned_mass`, `multi_k_tt_rank_profile`.

**JAX float32 precision boundary.** `inferactively-pymdp==1.0.1`
pulls in JAX, which uses **float32 by default**.  The closed-form
analytical track in `lean/*.py` runs in **float64** (numpy default).
This precision mismatch is why the pymdp-vs-closed-form agreement
tolerance is `PARAMETER_SWEEP_AGREEMENT_TOLERANCE`, not the stricter
symbolic tolerances used for exact algebraic checks.  The boundary is documented
inline in `manuscript/4C_pymdp_harness.md`; tests in
`tests/test_simulation_pymdp.py` apply the float32-aware tolerance
budget.

## Layered design

The harness deliberately separates *mean-field* inference (delegated
to pymdp) from *coupling* (handled by `coupling.entangled_posterior`):

```
                  ┌──────────────────────┐
   observations → │  pymdp Agent (×K)    │ → q_pi^k (mean-field marginals, EFE-baked)
                  └──────────────────────┘
                              │
                              ▼
                  ┌──────────────────────┐
              λ → │  entangled_posterior │ → coupled joint q_λ(π¹,…,π^K)
                  │  (J, K_c, γ, λ)      │
                  └──────────────────────┘
```

At λ=0 the coupled joint *is* the outer product of the per-stream
pymdp posteriors — the mean-field baseline.  At λ>0 the analytical
layer adds the cross-stream `λ·J` (habit) and `γ·λ·K_c` (preference)
factors on top, following the entanglement decomposition theorem
tracked in [`docs/reference/_theorem_map.md`](../reference/_theorem_map.md).

## Method contracts

This is the contract to preserve when modifying `src/simulation/`:

| Contract | Implementation | Verification |
|---|---|---|
| Exactly one adapter imports `pymdp` / JAX. | [`src/simulation/agents.py`](../../src/simulation/agents.py) imports `pymdp.agent.Agent`, constructs batched `float32` JAX arrays, and exposes `pymdp_available()`. | `tests/test_simulation_pymdp.py::test_pymdp_available_returns_true_when_imported`; static review of imports. |
| Per-stream inference is real pymdp, not a mock. | [`_run_pymdp_per_stream`](../../src/simulation/inference.py) calls `agent.infer_states(...)` then `agent.infer_policies(qs)` for each stream. | `tests/test_simulation_pymdp.py`, `tests/test_simulation_free_energy.py`, and JSONL runtime records from `simulate_pymdp.py`. |
| EFE is not double-counted. | `coupled_policy_posterior` feeds pymdp's posterior marginals to `entangled_posterior` and passes zero per-stream `G`, because pymdp has already used `γ·G` internally. | `test_coupled_policy_posterior_lambda_zero_is_outer_product` and the λ=0 free-energy-bundle baseline tests. |
| λ=0 recovers mean field. | The analytical coupling layer is neutral at `lam=0`, so the joint posterior is the outer product of pymdp's per-stream policy posteriors. | `tests/test_simulation_pymdp.py::test_coupled_policy_posterior_lambda_zero_is_outer_product`. |
| `FreeEnergyBundle` is one-source-per-λ. | `free_energy_bundle` computes the joint posterior, marginals, EFE vectors, VFE, entropy, total correlation, coupling term, and action distribution from one pymdp pass plus one analytical coupling pass. | `tests/test_simulation_free_energy.py` and the `pymdp_free_energy_bundle.csv` output gate. |
| All manuscript-facing grids and seeds flow from one file. | [`src/simulation/hyperparameters.py`](../../src/simulation/hyperparameters.py) owns sweep grids, rollout horizons, seeds, sentinel λ values, and tolerances. | `tests/test_hyperparameters.py`, `scripts/manuscript_variables.py`, and hardcoded-literal validation. |

The adapter is checked against this installed package surface:

```text
inferactively-pymdp==1.0.1
jax 0.9.2
Agent(..., policy_len=1, gamma=1.0, inference_algo='fpi', batch_size=1, ...)
Agent.infer_states(observations, empirical_prior, ...)
Agent.infer_policies(qs) -> (q_pi, G)
```

That matches the adapter calls in `agents.py` and `inference.py`.

## Quick example

```python
from simulation.builders import make_ising_ensemble
from simulation.inference import coupled_policy_posterior
from simulation.sweep import lambda_sweep

spec = make_ising_ensemble(num_streams=2, gamma=1.0, coupling_amplitude=1.0)
results = lambda_sweep(spec, observations=[0, 0], lams=[0.0, 0.5, 1.0, 2.0])
for r in results:
    print(r.lam, r.total_correlation, r.is_pmf)
```

Output (representative):

```
0.0  0.000000000000  True
0.5  0.061401192337  True
1.0  0.173019296138  True
2.0  0.315358742156  True
```

The total-correlation curve grows monotonically from the mean-field
baseline 0 toward the configured sweep saturation, bounded above by
`log 2` in this binary K=2 setting.  This is the empirical witness of
Prop 7.3 inside a grounded POMDP.

## Reproduction

```bash
uv run python scripts/simulate_pymdp.py
```

Emits, among other free-energy dashboard artifacts:

* `output/simulations/pymdp_lambda_sweep.csv`
* `output/simulations/pymdp_free_energy_bundle.csv`
* `output/simulations/pymdp_summary.json`
* `output/figures/pymdp_total_correlation_curve.png`
* `output/figures/pymdp_joint_lambda_{0.00,2.00,4.00}.png`
* `output/figures/pymdp_coupled_rollout.png`
* `output/figures/pymdp_{vfe_decomposition,efe_under_posterior,entropy_decomposition,action_distribution,free_energy_panel,action_entropy,kl_to_lambda_zero,marginal_entropy_per_stream,summary_panel}.png`

All artifacts are deterministic given the seeds set inside the script
(numerically identical mod the PNG `tEXt`-chunk build timestamp; the
PNG bytes themselves embed a timestamp, but every plotted value
matches across reruns).  The pymdp-side tests in
`tests/test_simulation_pymdp.py` and the spec tests in
`tests/test_simulation_specs.py` pin the contract; live counts are
visible via `uv run pytest --co -q tests/test_simulation_*.py`.

## Round-3 experiments (multi-K, long-horizon, revertibility)

Three additional `simulate_*.py` scripts ship in round 3:

```bash
uv run python scripts/simulate_multi_k.py          # configured multi-K growth + TT-rank profile
uv run python scripts/simulate_long_horizon.py     # configured long-horizon rollout + steady-state KL convergence
uv run python scripts/simulate_revertibility.py    # m-projection KL identity sweep
```

Each emits a `output/data/*_summary.json` plus the figures registered
in `manuscript/refs/labels.yaml::figures` (six total — see
[`visualizations.md`](visualizations.md)).  Multi-K invariants exercise
the **sparsity-rank tradeoff witness** ([[THMREF:thm_7_3]]) and the
**Schmidt-rank upper-semicontinuity witness** ([[THMREF:prop_7_2]])
empirically at `K > 2`; long-horizon exhibits the
**hierarchical-AIF concentration witness** ([[THMREF:thm_11_1]])
numerically.  Revertibility pins the m-projection KL identity at
every `λ` on the sweep.
