/- `ActinfPolicyEntanglement.SpectralWitnesses` — boundary witness forms
   for the two spectral / tensor-network claims that are exposed as
   current witness contracts: Proposition 8.2 (Schmidt rank upper-semicontinuous
   in λ) and Theorem 8.3 (sparsity-rank tradeoff for tensor-train coupling).

   Mathlib-free, `sorry`-free, `axiom`-free.  Both results are stated as
   *witness-consuming* boundary forms: the caller (a separate
   MathlibProofs layer importing `Mathlib.Topology.Semicontinuous` and
   `Mathlib.LinearAlgebra.TensorProduct`) supplies the topological /
   tensor-train evidence as a structural witness, and the boundary
   fragment certifies the resulting existence claim by extracting the
   witness fields.

   Numerical realizations live in
   [`src/lean/spectral.py`](../../src/lean/spectral.py) and are exercised
   by [`tests/test_witness_theorems.py`](../../tests/test_witness_theorems.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist

namespace ActinfPolicyEntanglement

/-! ## §8.2 Schmidt rank upper-semicontinuous in λ (Proposition 8.2)

The Schmidt rank of the λ-entangled posterior, viewed as a function of
the coupling parameter `λ`, is **upper-semicontinuous**: for every λ₀
and every rank ceiling `r₀` that the curve respects at λ₀, there is a
neighborhood of λ₀ on which the rank stays bounded by `r₀`.  At the
boundary level we phrase this as a witness-consuming statement: the
caller supplies the rank curve `rankCurve : Float → Nat`, the value
`rankCurve 0 = 1` (mean-field anchor), and the universally-quantified
upper-semicontinuity inequality.  A Mathlib extension would discharge
the witness in the separate additive layer from
`Mathlib.Topology.Semicontinuous` plus the lower-semicontinuity of
matrix rank. -/

/-- **Boundary witness for Proposition 8.2**: a Schmidt-rank curve
`rankCurve : Float → Nat` together with the mean-field anchor
`rankCurve 0 = 1` and the universally-quantified upper-semicontinuity
inequality (every λ-neighborhood of λ₀ contains a δ-window on which
the rank stays ≤ r₀ whenever `rankCurve λ₀ ≤ r₀`).  Supplied by the
analytic Mathlib extension. -/
structure UpperSemicontinuousRankWitness (rankCurve : Float → Nat) where
  /-- Mean-field anchor: at `λ = 0` the joint factorizes, so Schmidt
  rank is `1`. -/
  rank_at_zero : rankCurve 0.0 = 1
  /-- Upper-semicontinuity: every `λ₀` admits a tolerance window on
  which `rankCurve` stays bounded by any ceiling it satisfies at λ₀. -/
  usc : ∀ (lam0 : Float) (r0 : Nat),
          rankCurve lam0 ≤ r0 →
          ∃ delta : Float, 0.0 < delta ∧
            ∀ lam : Float, (lam - lam0).abs < delta → rankCurve lam ≤ r0

/-- **Proposition 8.2 (boundary witness form)**: an
`UpperSemicontinuousRankWitness` *is* the existence of an upper-
semicontinuous Schmidt-rank curve anchored at `rankCurve 0 = 1`.  Stock
Lean, zero-`sorry`.

**Typed-API-contract disclaimer.** Not a stand-alone proof of upper
semicontinuity; a typed-API contract.  The continuity inequality is
supplied as `witness.usc`; the boundary fragment re-publishes it
together with the mean-field anchor.  Bipartite K=2 case is now
*genuinely* proved at the boundary as
`Spectral.Bipartite.schmidtRankOne_iff_isBipartiteMeanField` (round 4);
the general-K upper-semicontinuity statement still requires Mathlib's
topological-semicontinuity library + matrix-rank lower-semicontinuity
to discharge. -/
theorem schmidtRank_upperSemicontinuous_witness
    (rankCurve : Float → Nat)
    (witness : UpperSemicontinuousRankWitness rankCurve) :
    rankCurve 0.0 = 1
      ∧ ∀ (lam0 : Float) (r0 : Nat),
          rankCurve lam0 ≤ r0 →
          ∃ delta : Float, 0.0 < delta ∧
            ∀ lam : Float, (lam - lam0).abs < delta → rankCurve lam ≤ r0 :=
  ⟨witness.rank_at_zero, witness.usc⟩

/-- Accessor theorem: the upper-semicontinuity witness is anchored at
the mean-field rank-one point. -/
theorem upperSemicontinuousRank_at_zero
    (rankCurve : Float → Nat)
    (witness : UpperSemicontinuousRankWitness rankCurve) :
    rankCurve 0.0 = 1 :=
  witness.rank_at_zero

/-- Accessor theorem: instantiate the upper-semicontinuity window at a
chosen point and rank ceiling. -/
theorem upperSemicontinuousRank_window
    (rankCurve : Float → Nat)
    (witness : UpperSemicontinuousRankWitness rankCurve)
    (lam0 : Float) (r0 : Nat)
    (hRank : rankCurve lam0 ≤ r0) :
    ∃ delta : Float, 0.0 < delta ∧
      ∀ lam : Float, (lam - lam0).abs < delta → rankCurve lam ≤ r0 :=
  witness.usc lam0 r0 hRank

/-! ## §8.3 Sparsity-rank tradeoff for tensor-train coupling (Theorem 8.3)

For an `K`-stream coupling potential whose tensor-train representation
has bond-dimensions `(b_1, …, b_{K-1})`, the entangled posterior has
Schmidt rank across each cut bounded above by the corresponding bond
dimension: `cut_rank k λ ≤ bond_bound k` for every λ.  Boundary form:
the caller supplies the per-cut rank function `cut_rank` and the per-cut
bond bound `bond_bound`, together with the universally-quantified
envelope.  The separate additive MathlibProofs layer is the discharge
site for this payload, using `Mathlib.LinearAlgebra.TensorProduct` plus
matrix-rank bounds. -/

/-- **Boundary witness for Theorem 8.3**: a per-cut rank envelope for an
`K`-stream tensor-train coupling.

* `cut_rank k λ` — Schmidt rank of the entangled posterior across cut
  `k ∈ Fin K` as a function of the coupling parameter `λ`.
* `bond_bound k` — a priori envelope on the bond dimension at cut `k`
  supplied by the coupling's tensor-train representation.
* `envelope` — the universally-quantified upper bound: every cut and
  every λ respect the envelope. -/
structure SparsityRankEnvelope (K : Nat) where
  /-- The Schmidt rank across cut `k`, as a function of `λ`. -/
  cut_rank : Fin K → Float → Nat
  /-- A priori bond-dimension envelope for cut `k`. -/
  bond_bound : Fin K → Nat
  /-- The universally-quantified rank-bound envelope. -/
  envelope : ∀ (k : Fin K) (lam : Float), cut_rank k lam ≤ bond_bound k

/-- **Theorem 8.3 (boundary witness form)**: a `SparsityRankEnvelope`
witness *is* the existence of a per-cut Schmidt-rank envelope for the
λ-entangled posterior of a tensor-train coupling.  Stock-Lean, zero-
`sorry`.

**Typed-API-contract disclaimer.** Not a stand-alone proof of the
sparsity-rank tradeoff; a typed-API contract.  The per-cut envelope
`cut_rank k λ ≤ bond_bound k` is supplied as a `SparsityRankEnvelope`
field; the boundary fragment extracts it.  MathlibProofs discharge
from `Mathlib.LinearAlgebra.TensorProduct` plus matrix-rank bounds. -/
theorem sparsityRank_tradeoff_witness (K : Nat)
    (witness : SparsityRankEnvelope K) :
    ∀ (k : Fin K) (lam : Float),
      witness.cut_rank k lam ≤ witness.bond_bound k :=
  witness.envelope

/-- Accessor theorem: instantiate the sparsity-rank envelope at one
cut and one coupling value. -/
theorem sparsityRank_envelope_at (K : Nat)
    (witness : SparsityRankEnvelope K)
    (k : Fin K) (lam : Float) :
    witness.cut_rank k lam ≤ witness.bond_bound k :=
  witness.envelope k lam

/-- Mean-field corollary: at `λ = 0` every cut rank collapses to `1`
*provided* the caller's envelope respects the rank-`1` mean-field
anchor.  Boundary witness form: the caller supplies the anchor as a
hypothesis. -/
theorem sparsityRank_meanField_at_zero (K : Nat)
    (witness : SparsityRankEnvelope K)
    (hAnchor : ∀ k : Fin K, witness.cut_rank k 0.0 = 1) :
    ∀ k : Fin K, witness.cut_rank k 0.0 ≤ 1 := by
  intro k
  rw [hAnchor k]
  exact Nat.le_refl 1

end ActinfPolicyEntanglement
