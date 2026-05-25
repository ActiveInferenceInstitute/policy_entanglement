/- `ActinfPolicyEntanglement.ConnectionsWitnesses` — boundary witness
   forms for the two §17 connection claims that are exposed as current
   witness contracts: Theorem 17.1 (hierarchical AIF as the λ → ∞
   limit) and Proposition 17.2 (sophisticated-inference embedding).

   Mathlib-free, `sorry`-free, `axiom`-free.  Both results are stated
   as *witness-consuming* boundary forms: the caller (a separate
   MathlibProofs layer importing `Mathlib.MeasureTheory.Measure.Tight` for the
   λ → ∞ tightness argument and the recursive Bellman-style update for
   sophisticated inference) supplies the analytic / recursive
   structure, and the boundary fragment certifies the existence claim
   by extracting the witness fields.  Each witness threads through the
   boundary-fragment primitives `kl` and `variationalFreeEnergy` so the
   statements are non-vacuous.

   Numerical realizations live in
   [`src/lean/decomposition.py`](../../src/lean/decomposition.py) and
   [`src/simulation/inference.py`](../../src/simulation/inference.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy

namespace ActinfPolicyEntanglement

/-! ## §17.1 Hierarchical AIF as the λ → ∞ limit (Theorem 17.1)

In the λ → ∞ limit, the λ-entangled posterior concentrates on a
hierarchical-AIF fixed point: for every tolerance ε > 0 there exists a
threshold λ₀ such that every λ ≥ λ₀ leaves the family within KL ≤ ε of
the hierarchical fixed point `q_infty`.  Boundary form: the caller
supplies the family `qFamily : Float → JointDist K Pol`, the
hierarchical fixed-point `q_infty`, the support, and the universally-
quantified concentration inequality.  The MathlibProofs layer would
discharge this from `Mathlib.MeasureTheory.Measure.Tight` (tightness of
families of measures) plus the KL-projection argument. -/

/-- **Boundary witness for Theorem 17.1**: a hierarchical-AIF
concentration witness for the λ-entangled family.

* `qFamily λ` — the entangled posterior at coupling `λ`.
* `q_infty` — the hierarchical-AIF fixed point that the family
  concentrates on as `λ → ∞`.
* `support` — the finite policy support against which KL is computed.
* `concentrate` — the universally-quantified concentration inequality
  in `(ε, λ₀)` form.

Supplied by the analytic MathlibProofs layer. -/
structure HierarchicalConcentrationWitness {K : Nat} {Pol : PolicyFactor K}
    (qFamily : Float → JointDist K Pol)
    (q_infty : JointDist K Pol)
    (support : List (PolicySpace K Pol)) where
  /-- For every tolerance `ε > 0` there is a coupling threshold
  `λ₀ > 0` such that every λ ≥ λ₀ leaves the family within KL ≤ ε of
  the hierarchical fixed point. -/
  concentrate : ∀ (eps : Float), 0.0 < eps →
                  ∃ lam0 : Float, 0.0 < lam0 ∧
                    ∀ lam : Float, lam0 ≤ lam →
                      kl (qFamily lam) q_infty support ≤ eps

/-- **Theorem 17.1 (boundary witness form)**: a
`HierarchicalConcentrationWitness` *is* the existence of a λ → ∞
hierarchical-AIF concentration claim for the entangled family.  Stock-
Lean, zero-`sorry`.

**Typed-API-contract disclaimer.** Not a stand-alone proof of the
hierarchical-AIF concentration limit; a typed-API contract.  The
`concentrate` field — that for every ε > 0 a coupling threshold
exists beyond which the entangled posterior is ε-close in KL to the
limit `q_∞` — is supplied as a witness obligation.  MathlibProofs
discharge from `Mathlib.MeasureTheory.Measure.Tight` (tightness of the
λ-entangled posterior family in the λ → ∞ limit). -/
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

/-- Trivial mean-field consequence: at `λ = 0` the family is mean-field;
the concentration claim says nothing at that point (it is a *limit*
claim).  This corollary just unpacks the witness's tightness window. -/
theorem hierarchicalAIF_threshold_exists {K : Nat} {Pol : PolicyFactor K}
    (qFamily : Float → JointDist K Pol)
    (q_infty : JointDist K Pol)
    (support : List (PolicySpace K Pol))
    (witness : HierarchicalConcentrationWitness qFamily q_infty support)
    (eps : Float) (hEps : 0.0 < eps) :
    ∃ lam0 : Float, 0.0 < lam0 ∧
      ∀ lam : Float, lam0 ≤ lam →
        kl (qFamily lam) q_infty support ≤ eps :=
  witness.concentrate eps hEps

/-! ## §17.2 Sophisticated-inference embedding (Proposition 17.2)

Sophisticated inference (recursive look-ahead with a Bellman-style
fixed-point update) embeds into the λ-deformation framework as an
embedding `embed : source → JointDist K Pol` that preserves the
variational free energy.  Boundary form: the caller supplies an
opaque `source` type (a Bellman state space), the embedding map, and
the preservation identity.  The separate additive MathlibProofs layer
is the discharge site for the recursive Bellman update plus the
KL-control identity that relates the sophisticated-inference value
function to the entangled free energy. -/

/-- **Boundary witness for Proposition 17.2**: a sophisticated-inference
embedding into the entanglement framework.

The witness carries:

* `source` — an opaque type representing the sophisticated-inference
  state space (e.g. a Bellman fixed-point ladder).
* `siValue` — the sophisticated-inference value function on `source`,
  i.e. the Bellman-fixpoint scalar each source state attains.
* `embed` — the embedding map `source → JointDist K Pol`.
* `preserveVFE` — the **non-trivial** preservation identity:
  for every `x : source`, the sophisticated-inference value `siValue x`
  equals the variational free energy of the embedded distribution
  `variationalFreeEnergy (embed x) logE G gamma support`.

This identity is what makes the witness genuine boundary content: a
caller cannot satisfy the witness by `rfl` alone (as in the prior
`F = F` form); the caller must commit to a *specific* mapping
between the sophisticated-inference value function and the boundary-
fragment VFE primitive.  Supplied by the analytic MathlibProofs layer
(or by the numerical Python companion). -/
structure SophisticatedInferenceEmbedding {K : Nat} {Pol : PolicyFactor K}
    (logE G : PolicySpace K Pol → Float) (gamma : Float)
    (support : List (PolicySpace K Pol)) where
  /-- The opaque sophisticated-inference source type. -/
  source : Type
  /-- **Anti-vacuity guard** (RedTeam Methods C2, 2026-05-20): the
  source MUST be nonempty.  Without this, `source := Empty` makes
  `preserveVFE` vacuously true (`∀ x : Empty, _` holds for any RHS),
  letting a caller satisfy the witness with no sophisticated-
  inference content.  Requiring `Nonempty source` prevents that
  attack surface: a caller committing `Empty` cannot supply a
  `Nonempty Empty` instance because it is uninhabited.  Per the
  audit, this is a one-field structural fix that closes the vacuity
  vector without changing any downstream caller (no instance of this
  structure is constructed in the present project; MathlibProofs
  discharge sites must now provide a nonemptiness proof). -/
  nonempty_source : Nonempty source
  /-- The sophisticated-inference value function on `source`. -/
  siValue : source → Float
  /-- The embedding into the entangled-posterior family. -/
  embed : source → JointDist K Pol
  /-- **Non-trivial VFE preservation**: the sophisticated-inference
  value at `x` equals the boundary-fragment variational free energy of
  the embedded joint.  Unlike the prior `F(embed x) = F(embed x)`
  reflexivity, this field commits the witness to a specific scalar
  identity that the caller must produce. -/
  preserveVFE : ∀ (x : source),
                  siValue x =
                  variationalFreeEnergy (embed x) logE G gamma support

/-- **Proposition 17.2 (boundary witness form)**: a
`SophisticatedInferenceEmbedding` *is* the existence of an embedding
from a sophisticated-inference source into the λ-deformation family
that maps the sophisticated-inference value function onto the
variational free energy.  Stock-Lean, zero-`sorry`. -/
theorem sophisticatedInference_embedding_witness {K : Nat} {Pol : PolicyFactor K}
    (logE G : PolicySpace K Pol → Float) (gamma : Float)
    (support : List (PolicySpace K Pol))
    (witness : SophisticatedInferenceEmbedding logE G gamma support) :
    ∀ (x : witness.source),
      witness.siValue x =
      variationalFreeEnergy (witness.embed x) logE G gamma support :=
  witness.preserveVFE

end ActinfPolicyEntanglement
