# Per-theorem four-track wiring (auto-generated)

**Do not hand-edit.** This file is auto-generated from [`../../manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml) by [`../../scripts/generate_theorem_map.py`](../../scripts/generate_theorem_map.py). Regenerate with:

```bash
uv run python scripts/generate_theorem_map.py
```

A CI test (`tests/test_theorem_map_generated.py`) asserts that re-running the generator produces no diff against this file — any new theorem, renamed Lean declaration, or changed Python / test companion is caught at validation time.

For the full four-track contract see [`four_track_coherence.md`](four_track_coherence.md). For the section-by-section map see [`manuscript_map.md`](manuscript_map.md).

| # | Theorem (registry label) | Manuscript token | Lean (`module.qualified_name`) | Python (numerical witness) | Test gate | Status |
|---|---|---|---|---|---|---|
| 5.1 | Entanglement Decomposition (`thm_4_1`) | `[[THMREF:thm_4_1]]` / `[[LEAN:thm_4_1]]` | [`Decomposition.entanglement_decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | [`lean.decomposition.entanglement_decomposition_rhs`](../../src/lean/decomposition.py) | [`test_decomposition`](../../tests/test_decomposition.py) | boundary |
| 5.2 | Coupling-pays-for-itself (`cor_4_2`) | `[[THMREF:cor_4_2]]` / `[[LEAN:cor_4_2]]` | [`Decomposition.couplingVerdict_correct`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | [`lean.decomposition.coupling_pays_for_itself`](../../src/lean/decomposition.py) | [`test_decomposition`](../../tests/test_decomposition.py) | proved |
| 5.3 | Mean-field at λ = 0 (`cor_4_3`) | `[[THMREF:cor_4_3]]` / `[[LEAN:cor_4_3]]` | [`Decomposition.couplingLogWeight_pointwise_at_zero`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | [`lean.coupling.entangled_log_weight_affine_in_lambda`](../../src/lean/coupling.py) | [`test_coupling`](../../tests/test_coupling.py) | proved |
| 5.4 | Strict gain when q is non-mean-field (`cor_4_4`) | `[[THMREF:cor_4_4]]` / `[[LEAN:cor_4_4]]` | [`Decomposition.totalCorrelation_def_unfold`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | [`lean.free_energy.total_correlation`](../../src/lean/free_energy.py) | [`test_free_energy`](../../tests/test_free_energy.py) | boundary |
| 5.5 | Existence of optimal coupling (`thm_4_2`) | `[[THMREF:thm_4_2]]` / `[[LEAN:thm_4_2]]` | [`Decomposition.freeEnergy_closedForm_witness`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | [`lean.decomposition.coupling_pays_for_itself`](../../src/lean/decomposition.py) | [`test_decomposition`](../../tests/test_decomposition.py) | boundary |
| 5.6 | Convexity of F in λ (`thm_4_3`) | `[[THMREF:thm_4_3]]` / `[[LEAN:thm_4_3]]` | [`Convexity.freeEnergy_convex_in_lam_witness`](../../lean/ActinfPolicyEntanglement/Convexity.lean) | [`lean.decomposition.free_energy_against_entangled_prior`](../../src/lean/decomposition.py) | [`test_witness_theorems`](../../tests/test_witness_theorems.py) | witness |
| 7.1 | MF submanifold is e-flat (`prop_6_1`) | `[[THMREF:prop_6_1]]` / `[[LEAN:prop_6_1]]` | [`Geometry.mfImage_isMeanField`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | [`lean.geometry.is_e_flat`](../../src/lean/geometry.py) | [`test_geometry`](../../tests/test_geometry.py) | proved |
| 7.2 | m-projection / marginalization (`prop_6_2`) | `[[THMREF:prop_6_2]]` / `[[LEAN:prop_6_2]]` | [`Geometry.mProjection_kl_eq_self_when_meanfield`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | [`lean.geometry.m_projection`](../../src/lean/geometry.py) | [`test_geometry`](../../tests/test_geometry.py) | proved |
| 7.3 | Total correlation as Bregman divergence (`prop_6_3`) | `[[THMREF:prop_6_3]]` / `[[LEAN:prop_6_3]]` | [`FreeEnergy.totalCorrelation_eq_kl_to_mprojection`](../../lean/ActinfPolicyEntanglement/FreeEnergy.lean) | [`lean.free_energy.total_correlation_via_kl`](../../src/lean/free_energy.py) | [`test_free_energy`](../../tests/test_free_energy.py) | witness |
| 7.4 | λ-family is an e-geodesic (`thm_6_4`) | `[[THMREF:thm_6_4]]` / `[[LEAN:thm_6_4]]` | [`Geometry.entangledFamily_eGeodesic`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | [`lean.coupling.entangled_log_weight_affine_in_lambda`](../../src/lean/coupling.py) | [`test_coupling`](../../tests/test_coupling.py) | forwarder |
| 7.5 | Pythagorean decomposition (`prop_6_5`) | `[[THMREF:prop_6_5]]` / `[[LEAN:prop_6_5]]` | [`Geometry.dualFlat_pythagorean_witness`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | [`lean.geometry.pythagorean_residual`](../../src/lean/geometry.py) | [`test_geometry`](../../tests/test_geometry.py) | witness |
| 8.1 | Bipartite mean-field factorization (`prop_7_1`) | `[[THMREF:prop_7_1]]` / `[[LEAN:prop_7_1]]` | [`Spectral.Bipartite.isBipartiteMeanField_factors`](../../lean/ActinfPolicyEntanglement/Spectral.lean) | [`lean.spectral.schmidt_decomposition`](../../src/lean/spectral.py) | [`test_spectral`](../../tests/test_spectral.py) | proved |
| 8.2 | Schmidt rank upper-semicontinuous in λ (`prop_7_2`) | `[[THMREF:prop_7_2]]` / `[[LEAN:prop_7_2]]` | [`SpectralWitnesses.schmidtRank_upperSemicontinuous_witness`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) | [`lean.spectral.schmidt_rank`](../../src/lean/spectral.py) | [`test_spectral`](../../tests/test_spectral.py) | witness |
| 8.3 | Sparsity-rank tradeoff (`thm_7_3`) | `[[THMREF:thm_7_3]]` / `[[LEAN:thm_7_3]]` | [`SpectralWitnesses.sparsityRank_tradeoff_witness`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) | [`lean.spectral.tensor_train_ranks`](../../src/lean/spectral.py) | [`test_witness_theorems`](../../tests/test_witness_theorems.py) | witness |
| 9.1 | Heterogeneous coupling tax (`thm_8_1`) | `[[THMREF:thm_8_1]]` / `[[LEAN:thm_8_1]]` | [`Heterogeneous.couplingTax_quadratic_bound`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean) | [`lean.heterogeneous.coupling_tax_within_quadratic_bound`](../../src/lean/heterogeneous.py) | [`test_heterogeneous`](../../tests/test_heterogeneous.py) | witness |
| 9.2 | Reflexive-stream tolerance (`cor_8_2`) | `[[THMREF:cor_8_2]]` / `[[LEAN:cor_8_2]]` | [`Heterogeneous.couplingTax_small_lambda_tolerance`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean) | [`lean.heterogeneous.coupling_tax_within_quadratic_bound`](../../src/lean/heterogeneous.py) | [`test_heterogeneous`](../../tests/test_heterogeneous.py) | witness |
| 11.1 | Local concavity of F at λ=0 (`prop_10_1`) | `[[THMREF:prop_10_1]]` / `[[LEAN:prop_10_1]]` | [`Convexity.freeEnergy_localConcavity_at_zero_witness`](../../lean/ActinfPolicyEntanglement/Convexity.lean) | [`lean.bernoulli_toy.ising_free_energy_curve`](../../src/lean/bernoulli_toy.py) | [`test_bernoulli_toy`](../../tests/test_bernoulli_toy.py) | witness |
| 17.1 | Hierarchical AIF as λ→∞ limit (`thm_11_1`) | `[[THMREF:thm_11_1]]` / `[[LEAN:thm_11_1]]` | [`ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness`](../../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) | — *(typed contract; analytic content assumed — no content-bound Python witness)* | [`test_witness_theorems`](../../tests/test_witness_theorems.py) | witness |
| 17.2 | Sophisticated inference embedding (`prop_11_2`) | `[[THMREF:prop_11_2]]` / `[[LEAN:prop_11_2]]` | [`ConnectionsWitnesses.sophisticatedInference_embedding_witness`](../../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) | — *(typed contract; analytic content assumed — no content-bound Python witness)* | [`test_witness_theorems`](../../tests/test_witness_theorems.py) | witness |
| 19.3 | Markov-blanket separation as 1 − I/H (`prop_11_3`) | `[[THMREF:prop_11_3]]` / `[[LEAN:prop_11_3]]` | [`MarkovBlanket.markovBlanket_separation_identity_witness`](../../lean/ActinfPolicyEntanglement/MarkovBlanket.lean) | [`lean.free_energy.total_correlation`](../../src/lean/free_energy.py) | [`test_free_energy`](../../tests/test_free_energy.py) | witness |
| 99.0 | Verified Float↔ℝ residual bridge (`roadmap_float_real_residual`) | `[[THMREF:roadmap_float_real_residual]]` / `[[LEAN:roadmap_float_real_residual]]` | [`FloatRealResidualWitness.floatRealResidual_witness`](../../lean/ActinfPolicyEntanglement/FloatRealResidualWitness.lean) | [`manuscript.variables.build_float_real_residual`](../../src/manuscript/variables.py) | [`test_meta_files_and_float_residual`](../../tests/test_meta_files_and_float_residual.py) | roadmap |

**How to read this table.** Pick a row. The four columns to its right let you (a) verify the formal statement at the boundary fragment by clicking the Lean link, (b) inspect a concrete numerical witness by clicking the Python link, (c) reproduce the witness check by running the test file, (d) confirm the proof status. Every theorem in `labels.yaml::theorems` appears in exactly one row; no row points at vapor.

## Mathlib4 Discharge Readiness

This second table is a proof-engineering map, not a claim that Mathlib-backed proofs already exist. It identifies where a separate `lean/MathlibProofs/` package should supply witness structures from Mathlib4 lemmas while the current boundary fragment remains stock-Lean and fast to audit.

| # | Label | Current status | Mathlib readiness | Analytic payload | First integration action |
|---|---|---|---|---|---|
| 5.1 | `thm_4_1` | boundary | High | Finite KL / entropy chain rule | Build the `ℝ` + finite-support PMF scaffold, then discharge the KL bookkeeping. |
| 5.2 | `cor_4_2` | proved | No current need | Boundary algebra already proved | Keep Mathlib out unless the surrounding scalar layer is specialized to `ℝ`. |
| 5.3 | `cor_4_3` | proved | No current need | Zero-coupling algebra already proved | Keep as a fast boundary theorem; reuse from the Mathlib layer if needed. |
| 5.4 | `cor_4_4` | boundary | Medium | Total-correlation non-negativity / strictness | After KL is available, add the Mathlib proof of `I(q) ≥ 0` and equality cases. |
| 5.5 | `thm_4_2` | boundary | Medium | Closed log-partition identity | Discharge once the finite exponential-family normalizers live over `ℝ`. |
| 5.6 | `thm_4_3` | witness | High | Convexity of `F(λ)` | Use Mathlib convex-analysis and second-derivative facts after scalar specialization. |
| 7.1 | `prop_6_1` | proved | No current need | Definition-level e-flat boundary contract | Only revisit if the Mathlib layer introduces a full manifold API. |
| 7.2 | `prop_6_2` | proved | Medium | m-projection optimality | Tie the boundary marginalization statement to the finite KL minimizer theorem. |
| 7.3 | `prop_6_3` | witness | High | Total correlation as KL to m-projection | First KL identity after the finite PMF scaffold is in place. |
| 7.4 | `thm_6_4` | forwarder | No current need | Affine log-weight forwarder | Reuse the existing boundary forwarder; no analytic discharge needed. |
| 7.5 | `prop_6_5` | witness | High | KL Pythagorean identity | Discharge from the finite KL chain rule and m-projection optimality. |
| 8.1 | `prop_7_1` | proved | Medium | Rank-one matrix factorization | Specialize the bipartite joint to Mathlib matrices over `ℝ`. |
| 8.2 | `prop_7_2` | witness | Medium | Rank semicontinuity | Use Mathlib topology/rank facts once matrix-valued joints are available. |
| 8.3 | `thm_7_3` | witness | Longer-term | Tensor-train rank envelope | Develop project-local TT rank lemmas on top of Mathlib tensor products. |
| 9.1 | `thm_8_1` | witness | Medium | Bregman / quadratic coupling-tax envelope | Add local Bregman Taylor lemmas on top of Mathlib Taylor/convexity tools. |
| 9.2 | `cor_8_2` | witness | Medium | Small-λ tolerance | Derive after the coupling-tax Taylor bound and continuity at zero are proved. |
| 11.1 | `prop_10_1` | witness | High | Local Taylor concavity at zero | A compact early Mathlib target after `F(λ)` is moved to `ℝ`. |
| 17.1 | `thm_11_1` | witness | Longer-term | Hierarchical concentration as `λ → ∞` | Use measure/tightness and filter convergence after finite-discrete proofs land. |
| 17.2 | `prop_11_2` | witness | Longer-term | Sophisticated-inference embedding | Requires project-local recursive-policy infrastructure; Mathlib is supporting substrate. |
| 19.3 | `prop_11_3` | witness | High | Markov-blanket separation identity | Good first visible discharge once entropy and real arithmetic are wired. |
| 99.0 | `roadmap_float_real_residual` | roadmap | Longer-term | Verified Float↔ℝ residual bridge | Flocq/interval formalization; currently bound by dashboard invariants and float_real_residual.json only. |

**Recommended order.** Start with the high-readiness finite-KL and real-arithmetic rows (`prop_11_3`, `prop_6_3`, `thm_4_1`, `prop_6_5`), then convex/Taylor rows, then matrix-rank rows. Tensor-train and recursive sophisticated-inference embeddings are best treated as project-local developments that use Mathlib as a substrate rather than as drop-in lemmas.
