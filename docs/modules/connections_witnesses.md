# Module: `ConnectionsWitnesses`

Boundary witness-form definitions and theorems for the two §17
connection claims that were historically outside the boundary fragment:
**Theorem 17.1** (hierarchical-AIF concentration analog) and
**Proposition 17.2** (Sophisticated-inference embedding).  Manuscript
anchor:
[`../manuscript/5B_connections_aif.md`](../../manuscript/5B_connections_aif.md)
§17 (`connections.hierarchical` — Theorem 17.1, anchor `thm_11_1`;
`connections.sophisticated` — Proposition 17.2, anchor `prop_11_2`).

## Overview

`ConnectionsWitnesses` packages the two §17 analytic obligations as
current `witness` status theorems:

* **Theorem 17.1** (`thm_11_1`, *hierarchical-AIF concentration
  analog*) — concentration of the entangled family on a supplied
  cross-level fixed point.
* **Proposition 17.2** (`prop_11_2`, *Sophisticated-inference
  embedding*) — a sophisticated-inference recursive Bellman ladder
  embeds into the λ-deformation family.

Both results are stated as **Mathlib-free, witness-consuming boundary
theorems**.  Each witness threads through the boundary-fragment
primitives `kl` and `variationalFreeEnergy` so the statements are
non-vacuous; the caller (a separate MathlibProofs layer importing
`Mathlib.MeasureTheory.Measure.Tight` for the `λ → ∞` tightness
argument or the recursive Bellman-style update for sophisticated
inference) supplies the analytic / recursive structure as the
witness payload.

The module is `Mathlib`-free, `sorry`-free, and `axiom`-free.  It
follows the *witness-structure idiom* established in
[`Heterogeneous.lean`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean),
[`Convexity.lean`](../../lean/ActinfPolicyEntanglement/Convexity.lean),
[`MarkovBlanket.lean`](../../lean/ActinfPolicyEntanglement/MarkovBlanket.lean),
and the companion round-3 module
[`SpectralWitnesses.lean`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean).

## Definitions provided

| Lean name | Kind | Purpose |
|---|---|---|
| `HierarchicalConcentrationWitness` | `structure` | Carries the universally-quantified concentration inequality: for every `ε > 0` there exists `λ₀ > 0` such that every `λ ≥ λ₀` leaves the family within `kl (qFamily λ) q_infty support ≤ ε` of the hierarchical fixed point.  One field. |
| `SophisticatedInferenceEmbedding` | `structure` | Carries (i) the opaque sophisticated-inference `source` type (e.g. a Bellman fixed-point ladder), (ii) the value function `siValue : source → Float`, (iii) the embedding map `embed : source → JointDist K Pol`, and (iv) the VFE-preservation identity tying `siValue` to `variationalFreeEnergy`.  Four fields. |
| `hierarchicalAIF_lambda_limit_witness` | `theorem` | Boundary witness form of Theorem 17.1. |
| `hierarchicalAIF_threshold_exists` | `theorem` (helper) | Single-tolerance extractor: at a fixed `ε > 0`, produces the threshold `λ₀ > 0` from the witness. |
| `sophisticatedInference_embedding_witness` | `theorem` | Boundary witness form of Proposition 17.2. |

## Key theorems

### `hierarchicalAIF_lambda_limit_witness` (Theorem 17.1 — `thm_11_1`)

```lean
theorem hierarchicalAIF_lambda_limit_witness {K : Nat} {Pol : PolicyFactor K}
    (qFamily : Float → JointDist K Pol)
    (q_infty : JointDist K Pol)
    (support : List (PolicySpace K Pol))
    (witness : HierarchicalConcentrationWitness qFamily q_infty support) :
    ∀ (eps : Float), 0.0 < eps →
      ∃ lam0 : Float, 0.0 < lam0 ∧
        ∀ lam : Float, lam0 ≤ lam →
          kl (qFamily lam) q_infty support ≤ eps :=
  witness.concentrate
```

The theorem says: for every tolerance `ε > 0` there is a coupling
threshold `λ₀ > 0` such that every `λ ≥ λ₀` leaves the family within
KL `≤ ε` of the supplied fixed point.  This is the coupling-shadow
part of hierarchical / deep AIF; temporal-scale separation and
directed top-down / bottom-up message passing are obligations of the
source generative model, not consequences of symmetric `J` alone. The
proof extracts the witness's `concentrate` field directly — one line,
witness-form pattern.  Note that the statement threads through the
boundary-fragment `kl` primitive, making the witness's existence claim
non-vacuous.

### `sophisticatedInference_embedding_witness` (Proposition 17.2 — `prop_11_2`)

```lean
theorem sophisticatedInference_embedding_witness {K : Nat} {Pol : PolicyFactor K}
    (logE G : PolicySpace K Pol → Float) (gamma : Float)
    (support : List (PolicySpace K Pol))
    (witness : SophisticatedInferenceEmbedding logE G gamma support) :
    ∀ (x : witness.source),
      witness.siValue x =
      variationalFreeEnergy (witness.embed x) logE G gamma support :=
  witness.preserveVFE
```

The theorem says: every sophisticated-inference source element `x`
admits an embedded `JointDist K Pol` whose boundary-fragment
`variationalFreeEnergy` equals the caller's sophisticated-inference
value function `siValue x`. This is the round-4 strengthened form:
the witness can no longer be discharged by reflexivity alone, because
the source-side Bellman value is an explicit scalar tied to the
embedded joint.

## Wiring

| Track | Resolves to |
|---|---|
| Manuscript section (Thm 17.1) | [`§17.2 Hierarchical / Deep AIF`](../../manuscript/5B_connections_aif.md) (`connections.hierarchical`). |
| Manuscript section (Prop 17.2) | [`§17.3 Sophisticated inference`](../../manuscript/5B_connections_aif.md) (`connections.sophisticated`). |
| Lean module | [`ConnectionsWitnesses.lean`](../../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) (2 structures, 3 theorems, zero `sorry`, zero `axiom`). |
| Registry labels | `thm_11_1` (Thm 17.1) and `prop_11_2` (Prop 17.2) in [`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml); both are current `status: witness` rows. |
| Python sanity rail (Thm 17.1) | [`src/lean/decomposition`](../../src/lean/decomposition.py) (`free_energy_against_entangled_prior`) and the long-horizon experiment [`scripts/simulate_long_horizon.py`](../../scripts/simulate_long_horizon.py) — the configured rollout is an empirical sidecar for finite-horizon concentration behavior; it does not prove the hierarchical-AIF process-theory claim. |
| Python sanity rail (Prop 17.2) | [`src/simulation/inference`](../../src/simulation/inference.py) — `coupled_policy_posterior` is the numerical coupled-policy posterior under λ-deformation; sophisticated-inference look-ahead is exercised by the per-stream EFE that pymdp computes inside `Agent.infer_policies`. |
| Tests | [`tests/test_witness_theorems.py`](../../tests/test_witness_theorems.py) exercises both witnesses against floating tolerance on the canonical Ising ensemble; [`tests/test_long_horizon.py`](../../tests/test_long_horizon.py) pins the steady-state convergence numerics. |

## Examples / use-cases (witness construction)

A Mathlib-side caller that wishes to certify Theorem 17.1 on a
specific λ-entangled family constructs a `HierarchicalConcentrationWitness`
by supplying the analytic concentration evidence:

```lean
def myConcentrationWitness
    (concentrationProof :
      ∀ (eps : Float), 0.0 < eps →
        ∃ lam0 : Float, 0.0 < lam0 ∧
          ∀ lam : Float, lam0 ≤ lam →
            kl (myFamily lam) my_qInfty mySupport ≤ eps) :
    HierarchicalConcentrationWitness myFamily my_qInfty mySupport where
  concentrate := concentrationProof
```

and then invokes

```lean
example (eps : Float) (h_eps : 0.0 < eps) : ... :=
  hierarchicalAIF_lambda_limit_witness
    myFamily my_qInfty mySupport
    (myConcentrationWitness concentrationProof)
    eps h_eps
```

to discharge the existence claim.  Analogously, a sophisticated-inference
embedding is supplied as:

```lean
def myEmbedding : SophisticatedInferenceEmbedding logE G gamma support where
  source     := MyBellmanLadder
  siValue    := bellmanValue
  embed      := fun x => /-…coupled posterior at x…-/
  preserveVFE := preservationProof
```

On the **numerical** side, the long-horizon rollout configured by
`simulation.hyperparameters.LONG_HORIZON_STEPS` and the
revertibility experiment at every `λ` on
`simulation.hyperparameters.REVERTIBILITY_LAMBDAS` provide the empirical
sidecars.  See the figures
[`long_horizon_marginals`](../../output/figures/long_horizon_marginals.png),
[`long_horizon_steady_state`](../../output/figures/long_horizon_steady_state.png),
and [`revertibility_witness`](../../output/figures/revertibility_witness.png).

## Note on Theorem 17.1's relationship to habit accumulation

The hierarchical-AIF concentration witness is related to the
*habit-accumulation* phenomenon in §9.5 (`heterogeneous.habit`): as
$\lambda \to \infty$ the per-stream marginals may settle onto a tight
neighborhood of a dominant archetype under the supplied concentration
witness.  The long-horizon
experiment ([`scripts/simulate_long_horizon.py`](../../scripts/simulate_long_horizon.py))
exhibits the finite-horizon empirical side of this behavior: the per-stream
tail-window KL
$D_{\mathrm{KL}}(q_t^k \,\|\, \bar q^k_{\mathrm{tail}})$ stays below
`output/data/manuscript_variables.json::long_horizon_steady_state_tol`
through the configured tail window.  Adjacent-step KL is reported
separately, so the concentration witness is not conflated with
$D_{\mathrm{KL}}(q_t^k\|q_{t-1}^k)$.

## Cross-references

* [`spectral_witnesses.md`](spectral_witnesses.md) — the companion
  round-3 module covering Proposition 8.2 + Theorem 8.3 (the §8
  witness graduations).
* [`decomposition_theorem.md`](decomposition_theorem.md) — Theorem 5.1
  is the upstream identity that grounds `variationalFreeEnergy` in
  the embedding `preserveVFE` tie-in.
* [`free_energy.md`](free_energy.md) — `kl` and
  `variationalFreeEnergy` are the boundary-fragment primitives the
  two witnesses tie in to.
* [`heterogeneous_ensembles.md`](heterogeneous_ensembles.md) — the
  original witness-structure idiom (`BoundedQuadraticTax`,
  `SmallLambdaTolerance`); the hierarchical-concentration witness is
  its `λ → ∞` analog.
* [`coupling.md`](coupling.md) — `entangledPosteriorLogWeight` is the
  family over which the `qFamily : Float → JointDist K Pol` of the
  Thm 17.1 witness is built.
* [`../reference/lean_reference.md`](../reference/lean_reference.md) —
  per-theorem status table.  Round 3 added the
  `ConnectionsWitnesses.lean` rows.
* [`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md) — the
  Mathlib payload-discharge roadmap; `hierarchicalAIF_lambda_limit_witness`
  (needs `Mathlib.MeasureTheory.Measure.Tight`) and
  `sophisticatedInference_embedding_witness` (needs the recursive
  Bellman update + KL-control identity) are the two new entries.
