# AGENTS.md — `docs/modules/`

Per-module concept index. Each Markdown file here pairs **one Lean module** under
[`../../lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/) with its
**Python mirror** under [`../../src/lean/`](../../src/lean/) and its **manuscript anchor**
under [`../../manuscript/`](../../manuscript/).

## Index

| File | Lean module | Python mirror | Manuscript anchor |
|---|---|---|---|
| `basic.md` | `Basic.lean` | (no mirror — types only) | `2B_setup.md` |
| `bernoulli_toy.md` | `BernoulliToy.lean` | `bernoulli_toy.py` | `2E_examples.md` |
| `constructive.md` | `Constructive.lean` | (no mirror — boundary witnesses) | `S05_lean_code_skeleton.md` |
| `convexity.md` | `Convexity.lean` | (realized in `free_energy.py`, `coupling.py`) | `2D_decomposition.md` §5.4, `2J_comparative_statics.md` §11.3, `S02_convexity_of_free_energy.md` |
| `coupling.md` | `Coupling.lean` | `coupling.py` | `2C_lambda_deformation.md` |
| `decomposition_theorem.md` | `Decomposition.lean` | `decomposition.py` | `2D_decomposition.md`, `S01_proof_of_decomposition_theorem.md` |
| `free_energy.md` | `FreeEnergy.lean` | `free_energy.py` | `2D_decomposition.md`, `2F_geometry.md` |
| `heterogeneous_ensembles.md` | `Heterogeneous.lean` | `heterogeneous.py` | `2H_heterogeneous.md` |
| `information_geometry.md` | `Geometry.lean` | `geometry.py` | `2F_geometry.md` |
| `joint_dist.md` | `JointDist.lean` | `joint_dist.py` | `2B_setup.md` |
| `markov_blanket.md` | `MarkovBlanket.lean` | (realized in `free_energy.py`) | `5D_connections_multi_agent.md` §19.3 |
| `monotonicity.md` | `Monotonicity.lean` | (implicit via `numpy` order) | (lemma library; cross-cut) |
| `scalar_typeclass.md` | `Scalar.lean` | (implicit — `numpy.float64`) | `S05_lean_code_skeleton.md` |
| `spectral_structure.md` | `Spectral.lean` | `spectral.py` | `2G_spectral.md` |
| `spectral_witnesses.md` | `SpectralWitnesses.lean` | (realized in `spectral.py`; multi-K experiments in `scripts/simulate_multi_k.py`) | `2G_spectral.md` §8.1 (`prop_7_2`), §8.3 (`thm_7_3`) — witness-form rows |
| `connections_witnesses.md` | `ConnectionsWitnesses.lean` | (realized in `decomposition.py`, `simulation/inference.py`; long-horizon in `scripts/simulate_long_horizon.py`) | `5B_connections_aif.md` §17.2 (`thm_11_1`), §17.3 (`prop_11_2`) — witness-form rows |
| `float_real_residual_witness.md` | `FloatRealResidualWitness.lean` | (roadmap row — residual fields sourced from `output/reports/float_real_residual.json`; residual tracking in `tests/test_meta_files_and_float_residual.py`) | `3B_lean_formalization.md` — Float↔ℝ residual scaffold, roadmap row |

## Authoring rules

1. **One concept per page.** A module page covers a single Lean module and
   its Python mirror.
2. **Show the live Lean signature.** Quote the actual `theorem` declaration
   (no paraphrase). Update when the boundary fragment changes.
3. **Pair with a Python sanity rail.** Show how the Python mirror exercises
   the same identity numerically. Cross-link to the relevant
   `tests/test_<module>.py`.
4. **Manuscript anchor.** Link to the manuscript section that **states**
   the theorem (not the supplement; the supplement carries the proof).
5. **Stay synchronized with `manuscript/refs/labels.yaml`.** When a theorem
   moves between modules, update both the registry and this page.

## Current ground truth

* Live boundary/module counts are checked by `scripts/build_lean.py`
  and summarized in `output/reports/release_readiness.json`.
  Historical module-addition deltas live in `docs/CHANGELOG.md`;
  current-facing pages should link to live reports instead of carrying
  hand-maintained status snapshots.

## See also

- [`../../lean/ActinfPolicyEntanglement/AGENTS.md`](../../lean/ActinfPolicyEntanglement/AGENTS.md) — Lean-side authoring rules
- [`../../src/lean/AGENTS.md`](../../src/lean/AGENTS.md) — Python-mirror rules
- [`../reference/lean_reference.md`](../reference/lean_reference.md) — per-theorem status table + Mathlib refinement roadmap pointer
- [`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md) — witness-payload-discharge plan for the separate MathlibProofs layer
