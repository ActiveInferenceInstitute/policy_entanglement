# AGENTS.md — `src/simulation/`

pymdp 1.0.1 POMDP simulation harness for coupled-policy active-inference
ensembles.  Companion to the analytical mirrors in `src/lean/`.

## Module map

| File | Role |
|---|---|
| `specs.py` | `StreamSpec`, `CoupledEnsembleSpec` — pure data classes (no pymdp dep) |
| `builders.py` | Deterministic Ising K-stream toy + helpers |
| `agents.py` | pymdp 1.0.1 `Agent` adapter (the *only* file that imports pymdp / jax) |
| `inference.py` | Per-stream EFE / policy-posterior + λ-coupled joint |
| `rollout.py` | `RolloutStep`, `Rollout`, `simulate_coupled_rollout` |
| `sweep.py` | `LambdaSweepResult`, `lambda_sweep`, `total_correlation_curve` |

## Rules

* `pymdp` is **optional** (`uv sync --group sim`).  Tests skip via the
  `requires_pymdp` marker when missing.
* Anything that touches `pymdp.agent.Agent` lives in `agents.py`.  The
  rest of the subpackage operates on numpy and the analytical layer
  (`coupling.entangled_posterior`).
* Keep deterministic seeds in every helper that involves randomness.
* The coupled posterior layering is fixed: pymdp provides the
  *mean-field* layer (per-stream `q_pi^k`), the analytical layer adds
  the cross-stream `λ·J` / `γ·λ·K_c` factors on top.  Do not pipe pymdp's
  EFE back into `entangled_posterior` — `coupled_policy_posterior`
  already passes zero-G for that reason.
