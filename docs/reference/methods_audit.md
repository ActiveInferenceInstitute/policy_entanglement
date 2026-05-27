# Lean and pymdp Methods Audit

*Latest generated audit.*

This page records the current methods check across the two places where
the project is easiest to overstate: the Mathlib-free Lean boundary and
the real `pymdp` simulation harness.

For the dependency order that turns those methods into manuscript
artifacts, see [`methods_orchestration.md`](methods_orchestration.md).

## Lean Boundary

Confirmed by `uv run python scripts/build_lean.py`:

| Item | Current state |
|---|---|
| Toolchain | stock Lean 4 v4.29.0 |
| Lake build | 22 jobs green |
| Boundary modules | 17 files under `lean/ActinfPolicyEntanglement/` |
| Hygiene | 0 strict `sorry`, 0 `axiom`, 0 `unsafe` / `partial` / `noncomputable`, 0 `Mathlib` imports |
| Manuscript theorem coverage | all 21 registered theorem rows have a Lean companion |

Interpretation:

* The boundary fragment **does** machine-check algebraic identities over
  the local `CommScalar` interface, plus definitional unfoldings and
  forwarders.
* It **does not** claim to prove every analytic probability payload
  inside the stock-Lean package.  KL chain rules, SVD rank theory,
  Bregman Taylor expansion, and measure-tightness arguments either live
  in the separate `MathlibProofs` package or remain witness-payload
  work.
* Those analytic payloads appear as witness structures whose fields tie
  the claimed scalars back to boundary primitives. Row-specific witness
  discharge should happen in `lean/MathlibProofs/`, not by rewriting the
  Mathlib-free boundary API.

The most important anti-overclaiming rule is: a theorem with status
`witness` is a typed contract, not a standalone analytic proof.

## MathlibProofs Analytic Layer

Confirmed by `uv run python scripts/build_mathlib_proofs.py` on the
release path:

| Item | Current state |
|---|---|
| Package | separate `lean/MathlibProofs/` Lake package importing Mathlib |
| Headline discharge | `MathlibProofs.free_energy_decomposition_full` proves the full real-valued free-energy decomposition, with `entanglement_decomposition_generalK` as the finite-KL kernel |
| Axiom audit | foundational-only `#print axioms` for the keystone declarations |
| Non-vacuity | independent negative controls make the build fail if the load-bearing `logZE` or coupling term is neutralized |
| Residual | no verified Float$\leftrightarrow\mathbb{R}$ bridge; several witness-form rows still require row-specific Mathlib payloads |

Interpretation:

* The manuscript may say the headline decomposition is
  machine-checked in $\mathbb{R}$ by `MathlibProofs`.
* The manuscript must still distinguish that real-valued proof from the
  stock-Lean Float boundary and from the numerical pymdp / NumPy
  pipeline.
* Witness-form rows should not be promoted merely because
  `MathlibProofs` contains adjacent infrastructure; each promotion
  requires a row-specific compiled source and registry update.

## pymdp Harness

Confirmed locally by importing the installed package:

```text
inferactively-pymdp==1.0.1
jax 0.9.2
Agent(..., policy_len=1, gamma=1.0, inference_algo='fpi', batch_size=1, ...)
Agent.infer_states(observations, empirical_prior, ...)
Agent.infer_policies(qs) -> (q_pi, G)
```

The project adapter matches that API:

| Contract | Source |
|---|---|
| Only one module imports `pymdp` / JAX. | `src/simulation/agents.py` |
| `StreamSpec` and `CoupledEnsembleSpec` validate shapes without pymdp. | `src/simulation/specs.py` |
| Each stream runs real `Agent.infer_states` then `Agent.infer_policies`. | `src/simulation/inference.py::_run_pymdp_per_stream` |
| The λ-coupled joint posterior adds coupling after pymdp produces per-stream posteriors. | `src/simulation/inference.py::coupled_policy_posterior` |
| The analytical layer receives zero per-stream `G` to avoid double-counting pymdp's EFE. | `src/simulation/inference.py::coupled_policy_posterior` |
| `FreeEnergyBundle` derives every plotted scalar from the same posterior and EFE vectors. | `src/simulation/inference.py::free_energy_bundle` |
| Grids, seeds, rollout horizons, and tolerances flow from one file. | `src/simulation/hyperparameters.py` |

Validation coverage:

* `tests/test_simulation_pymdp.py` checks the Agent adapter, λ=0
  mean-field recovery, monotone total-correlation growth, and rollout
  determinism.
* `tests/test_simulation_free_energy.py` checks VFE/EFE bundle fields,
  entropy identities, total-correlation monotonicity, quantile
  envelopes, and saturation helpers.
* `tests/test_hyperparameters.py` checks the source-of-truth grids and
  manuscript-variable mirror.
* `scripts/validate_outputs.py` checks emitted CSV/JSON/PNG artifacts
  and the pymdp JSONL run log after the full pipeline.

## Documentation Outcome

The public documentation should therefore say:

* "Lean boundary fragment" or "typed API skeleton" for witness theorems.
* "Mathlib-free, `sorry`-free, axiom-free" for the current Lean package.
* "MathlibProofs proves the headline real-valued decomposition" for the
  separate release-path analytic layer.
* "Real `pymdp.agent.Agent` calls" for simulation tests when the `sim`
  group is installed.
* "Float32-aware tolerance" for pymdp-vs-NumPy agreement, because JAX
  executes the Agent path in `float32` while the analytical NumPy layer
  uses `float64`.

It should not say:

* "All analytic KL/SVD/Bregman payloads are proved" before
  `MathlibProofs` contains a row-specific witness construction and a
  green separate build for each row.
* "pymdp is required for the whole project"; it is optional and guarded.
* "The analytical layer recomputes pymdp EFE"; it deliberately passes
  zero per-stream `G` to avoid double counting.

## Claim audit matrix

Cross-track claim ledger (theorem rows + pymdp / GNN / Mathlib / publication /
regression tracks):

- CSV: [`../_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv`](../_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv)
- Generator: `uv run python scripts/generate_audit_matrix.py --write`
- Drift gate: `tests/test_status_docs.py` (minimum row count, theorem coverage, artifact paths)
- Publication DOI: https://doi.org/10.5281/zenodo.20419257 (wired in `manuscript/config.yaml`, `CITATION.cff`, and `src/manuscript/publication_metadata.py`)

