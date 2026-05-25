# Invariants reference

*Latest generated audit.* The historical round-3 pass added 1 invariant
(`revertibility_kl_equals_multiinformation`) for a live total of **47
invariants**, all passing.

Every numerical claim in the manuscript has a *numerical witness*
checked in CI.  The witnesses are encoded as project-local
`reporting.interactive_dashboard.Invariant` instances, computed by
[`src/lean/invariants.py`](../../src/lean/invariants.py) and the
round-3 add-on in
[`scripts/build_dashboard.py`](../../scripts/build_dashboard.py),
rendered to
`output/reports/dashboard_invariants.txt` (also embedded in the
interactive HTML dashboard).

The plain-text report is a CI-diffable artifact: any drift in a
witness value (or any new failure) is caught by the line-by-line check
in
[`tests/test_invariants_and_dashboard.py`](../../tests/test_invariants_and_dashboard.py).

## How to read this page

Each row below lists:

- **Name** — the `Invariant.name` used in the dashboard and the
  plaintext report.  Use this as the key when grep-ing
  `output/reports/dashboard_invariants.txt`.
- **Family** — the builder function in
  [`src/lean/invariants.py`](../../src/lean/invariants.py)
  (or a one-off in
  [`scripts/build_dashboard.py`](../../scripts/build_dashboard.py))
  that produces it.
- **Witness for** — the manuscript theorem / claim it numerically
  certifies; cross-references the registry label where applicable.
- **Tolerance** — the absolute floating-point tolerance at which the
  invariant is gated.

## Live count

47 invariants total (up from 46 in round 2; round-3 addition is
`revertibility_kl_equals_multiinformation`).

| Family | Count | Builder |
|---|---|---|
| Ising closed-form vs empirical | 6 | `ising_invariants` |
| Free energy monotonicity | 3 | `free_energy_invariants` (one per utility level) |
| Optimal-λ properties | 2 | `optimal_lambda_invariants` |
| Phase classifier | 5 | `phase_invariants` (disordered / mixed_low / mixed_mid / mixed_high / frozen) |
| Marginal / TC entropy bounds | 2 | `marginal_invariants` |
| Decomposition (Thm 5.1) | 3 | `decomposition_invariants` |
| Coupling-pays-for-itself | 1 | `coupling_pays_invariants` |
| Affine log-weight (Thm 7.4) | 24 | `affine_log_weight_invariants` (γ ∈ {0, 0.5, 1} × π ∈ {(0,0), (0,1), (1,0), (1,1)} × {a, slope}) |
| Revertibility (round 3) | 1 | inline in `scripts/build_dashboard.py` |
| **Total** | **47** | (matches `output/reports/dashboard_invariants.txt::summary`) |

## Per-family detail

### Ising closed-form vs empirical (6 invariants)

| Name | Witness for | Tolerance |
|---|---|---|
| `ising_tc_at_zero` | `q_{λ=0}` is mean-field ⇒ `TC = 0` | `1e-12` |
| `ising_mean_field_at_zero` | `q_{λ=0}` is bit-exact mean-field | `0` |
| `ising_mi_agreement` | Closed-form `I(λ) = log 2 − H_b(σ(λ))` agrees with empirical TC | `1e-9` |
| `ising_mi_monotone_in_lambda` | `I(λ)` is monotone-increasing on λ ≥ 0 | `1e-12` |
| `ising_mi_below_log2` | Closed-form `I(λ) < log 2` for every grid sample | `1e-12` |
| `ising_tc_kl_equivalence_at_probe` | At λ = 3, `TC(q)` via the two formulas agrees | `1e-12` |

Builder: `ising_invariants(grid)` in
[`src/lean/invariants.py`](../../src/lean/invariants.py).
Manuscript: §6 ([`2E_examples.md`](../../manuscript/2E_examples.md))
and §10 ([`2I_phase_structure.md`](../../manuscript/2I_phase_structure.md));
Lean: [`BernoulliToy`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean).

### Free energy monotonicity (3 invariants)

| Name | Witness for | Tolerance |
|---|---|---|
| `free_energy_monotone_decreasing_u=0` | `F(λ; u=0)` is monotone-decreasing on λ ≥ 0 | `1e-9` |
| `free_energy_monotone_decreasing_u=1` | `F(λ; u=1)` is monotone-decreasing on λ ≥ 0 | `1e-9` |
| `free_energy_monotone_decreasing_u=2` | `F(λ; u=2)` is monotone-decreasing on λ ≥ 0 | `1e-9` |

Builder: `free_energy_invariants(grid, utilities=(0, 1, 2))`.
Manuscript: §11 ([`2J_comparative_statics.md`](../../manuscript/2J_comparative_statics.md));
Lean: `Convexity.freeEnergy_convex_in_lam_witness` (Thm 5.6,
[`Convexity.lean`](../../lean/ActinfPolicyEntanglement/Convexity.lean)).

### Optimal-λ properties (2 invariants)

| Name | Witness for | Tolerance |
|---|---|---|
| `optimal_lambda_at_zero` | `λ*(δ=0) = 0` | `1e-15` |
| `optimal_lambda_monotone_in_delta` | `λ*(δ)` is monotone-increasing in `δ` | `1e-12` |

Builder: `optimal_lambda_invariants(deltas=(0.0, 0.5, 1.0, 2.0))`.

### Phase classifier (5 invariants)

| Name | Witness for | Tolerance |
|---|---|---|
| `phase_classifier_disordered` | `phase(λ=0.4 | μ=0.5, σ=2.5) == 'disordered'` | `0` |
| `phase_classifier_mixed_low` | `phase(λ=0.6 | …) == 'mixed'` | `0` |
| `phase_classifier_mixed_mid` | `phase(λ=1.5 | …) == 'mixed'` | `0` |
| `phase_classifier_mixed_high` | `phase(λ=2.4 | …) == 'mixed'` | `0` |
| `phase_classifier_frozen` | `phase(λ=2.6 | …) == 'frozen'` | `0` |

Builder: `phase_invariants(probes=…)`.  Manuscript: §10
([`2I_phase_structure.md`](../../manuscript/2I_phase_structure.md));
Lean: `BernoulliToy.couplingPhaseAt`.

### Marginal / TC entropy bounds (2 invariants)

| Name | Witness for | Tolerance |
|---|---|---|
| `joint_entropy_below_log_size` | `H(q) ≤ log |Π|` over the entire λ-sweep | `1e-12` |
| `tc_nonneg_over_sweep` | `Σ H(q^k) − H(q) = TC ≥ 0` at every grid point | `1e-12` |

Builder: `marginal_invariants(grid)`.  Lean:
[`FreeEnergy`](../../lean/ActinfPolicyEntanglement/FreeEnergy.lean)
(`shannonEntropy`, `totalCorrelation`).

### Decomposition (Thm 5.1) (3 invariants)

| Name | Witness for | Tolerance |
|---|---|---|
| `decomposition_lhs_eq_rhs_max_residual` | `max |F[q_λ] − Σ RHS_terms|` over the sweep | `1e-9` |
| `decomposition_lhs_eq_rhs_array_close` | Pointwise `F[q_λ] ≈ entanglement_decomposition_rhs(...).total` | `1e-9` |
| `decomposition_lhs_finite` | LHS `F[q_λ]` is finite at every grid point | finite |

Builder: `decomposition_invariants(grid)`.  Manuscript: §5
([`2D_decomposition.md`](../../manuscript/2D_decomposition.md));
Lean: [`Decomposition.entanglement_decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean);
docs: [`decomposition_theorem.md`](../modules/decomposition_theorem.md).

### Coupling-pays-for-itself (1 invariant)

| Name | Witness for | Tolerance |
|---|---|---|
| `coupling_pays_above_lambda=0.1` | Every λ > 0.1 produces `TC(q_λ) > TC(q_0)` | `0` |

Builder: `coupling_pays_invariants(grid, threshold=0.1)`.  Manuscript:
§5.2 (Cor 5.2); Lean: `Decomposition.couplingVerdict_correct` (round-3
addition).

### Affine log-weight (Thm 7.4) (24 invariants)

A 3 × 4 × 2 = 24-entry block witnessing Theorem 7.4 (affine λ ↦
`log E_λ(π) = a + b·λ` with intercept `a = 0` and slope
`b = J(π) − γ · K_c(π)`).  Three precision levels
`γ ∈ {0, 0.5, 1}` × four policies `π ∈ {(0,0), (0,1), (1,0), (1,1)}`
× two checks (`a_zero` and `slope_correct`).

| Name pattern | Witness for | Tolerance |
|---|---|---|
| `affine_a_zero_gamma={γ}_pi={π}` | `a = 0` in `log E_λ(π) = a + b·λ` | `1e-15` |
| `affine_slope_correct_gamma={γ}_pi={π}` | `b = J(π) − γ · K_c(π)` | `1e-15` |

Builder: `affine_log_weight_invariants(gammas=(0, 0.5, 1.0))`.
Manuscript: §7
([`2F_geometry.md`](../../manuscript/2F_geometry.md));
Lean: `Coupling.couplingLogWeight_affine_in_lam` and
`Geometry.entangledFamily_eGeodesic`.

### Revertibility (round 3, 1 invariant)

| Name | Witness for | Tolerance |
|---|---|---|
| `revertibility_kl_equals_multiinformation` | At every λ on the revertibility sweep, the m-projection KL equals the total correlation `I(q_λ)` | `1e-15` |

Builder: inline in
[`scripts/build_dashboard.py`](../../scripts/build_dashboard.py)
consuming
[`scripts/simulate_revertibility.py`](../../scripts/simulate_revertibility.py)'s
summary JSON.  Manuscript: §17
([`5B_connections_aif.md`](../../manuscript/5B_connections_aif.md))
and the round-3 mention in
[`CHANGELOG.md`](../CHANGELOG.md);
Lean: ties in to `ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness`
(via the long-horizon experiment) and
`Decomposition.entanglement_decomposition` (algebraic identity).

## Round-by-round delta

| Round | Count | Delta | New families |
|---|---|---|---|
| 1 | 22 | — | Ising, free-energy monotonicity, decomposition, affine-log-weight (γ = 0 only) |
| 2 | 46 | +24 | phase classifier, marginal/TC, optimal-λ, coupling-pays, affine-log-weight expanded to γ ∈ {0, 0.5, 1} |
| 3 | 47 | +1 | revertibility (KL ↔ multi-information identity at every λ) |

The round-2 → round-3 delta is intentionally small — round 3 was a
*theorem-graduation* round (closing the four remaining `deferred`
theorems and adding two `proved` rows), not an *invariant-expansion*
round.

## See also

- [`statistics_reference.md`](statistics_reference.md) §7 — total
  test-budget breakdown; the 47 invariants are also exercised by
  `tests/test_invariants_and_dashboard.py`.
- [`veridical_status.md`](veridical_status.md) — live audit (Lean
  build + invariant pass count + variable provenance).
- [`four_track_coherence.md`](four_track_coherence.md) — the "show,
  not tell" contract that ties each invariant to its Lean theorem,
  Python helper, and manuscript section.
- [`../guides/testing.md`](../guides/testing.md) — the no-mocks
  policy and how to add a new invariant.
