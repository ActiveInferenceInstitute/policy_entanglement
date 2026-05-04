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
   the Bernoulli example in the manuscript (`§5`).
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

`pymdp` 1.0.1 is an *optional* dependency surfaced via the `sim` group:

```bash
uv sync --group sim --group viz   # pymdp + matplotlib helpers
uv sync                           # core only (legacy 119-test surface)
```

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
factors on top, exactly as Theorem 4.1 prescribes.

## Quick example

```python
from builders import make_ising_ensemble
from inference import coupled_policy_posterior
from sweep import lambda_sweep

spec = make_ising_ensemble(K=2, gamma=1.0, coupling_lambda=1.0)
results = lambda_sweep(spec, observations=[0, 0], lams=[0.0, 0.5, 1.0, 2.0])
for r in results:
    print(r.lam, r.total_correlation, r.is_pmf)
```

Output (representative):

```
0.0  0.0          True
0.5  0.123…       True
1.0  0.396…       True
2.0  0.628…       True
```

The total-correlation curve grows monotonically from the mean-field
baseline 0 toward the saturation `log K` (here `log 2 ≈ 0.693`) — the
empirical witness of Prop 6.3 inside a grounded POMDP.

## Reproduction

```bash
uv run python scripts/simulate_pymdp.py
```

Emits:

* `output/simulations/pymdp_lambda_sweep.csv`
* `output/figures/pymdp_total_correlation_curve.png`
* `output/figures/pymdp_joint_lambda_{0.00,2.00,4.00}.png`
* `output/figures/pymdp_coupled_rollout.png`

All artefacts are deterministic given the seeds set inside the script.
The 17 tests in `tests/test_simulation_pymdp.py` and 22 tests in
`tests/test_simulation_specs.py` pin the contract.
