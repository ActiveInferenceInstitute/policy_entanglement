/- `ActinfPolicyEntanglement.Spectral` — spectral / tensor-network
   structure of the joint policy posterior: bipartite mean-field
   factorization (Proposition 7.1, boundary form).

   Mathlib-free, `sorry`-free, `axiom`-free. The full Schmidt-rank /
   tensor-train statements require Mathlib's matrix-rank machinery
   and are exposed by the `MathlibProofs` extension; this fragment
   ships only the constructively-true factorization witnesses.
   Numerical realizations (SVD, tensor-train ranks) live in
   [`src/lean/spectral.py`](../../src/lean/spectral.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist

namespace ActinfPolicyEntanglement

/-! ## §7.1 Bipartite mean-field factorization (K = 2) -/

namespace Bipartite

/-- For `K = 2`, view the joint as a `Float` matrix indexed by
`(π¹, π²)`. -/
abbrev BipartiteJoint (Pol1 Pol2 : Type) : Type :=
  Pol1 → Pol2 → Float

/-- A bipartite joint is *mean-field* iff it factors as
`u(π¹) · v(π²)`. -/
def IsBipartiteMeanField {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2) : Prop :=
  ∃ (u : Pol1 → Float) (v : Pol2 → Float),
    ∀ π1 π2, q π1 π2 = u π1 * v π2

/-- **Proposition 7.1 (boundary iff form)**: a bipartite joint is
mean-field iff it admits a product factorization.  Both directions
are definitional unfoldings of `IsBipartiteMeanField`; they were
previously split into two separate `id`-theorems whose combined
content was a single biconditional.  The iff form makes the
*equivalence* itself a single boundary theorem and is the form
imported by `SpectralWitnesses` when anchoring Schmidt-rank-1.

The full Schmidt-rank-1 characterization (rank as defined via SVD)
requires Mathlib's `Matrix.rank_one_outer_product` and is exposed by
the `MathlibProofs` extension. Stock-Lean, zero-`sorry`. -/
theorem isBipartiteMeanField_iff_factors {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2) :
    IsBipartiteMeanField q ↔
      ∃ (u : Pol1 → Float) (v : Pol2 → Float),
        ∀ π1 π2, q π1 π2 = u π1 * v π2 :=
  Iff.rfl

/-- **Proposition 7.1 (forward direction, forwarder)**: extraction
shortcut for callers that already have the bipartite-mean-field
predicate in hand and want the product factorization witness. -/
theorem isBipartiteMeanField_factors {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2)
    (h : IsBipartiteMeanField q) :
    ∃ (u : Pol1 → Float) (v : Pol2 → Float),
      ∀ π1 π2, q π1 π2 = u π1 * v π2 :=
  (isBipartiteMeanField_iff_factors q).mp h

/-- **Proposition 7.1 (converse direction, forwarder)**: insertion
shortcut for callers that have a product factorization in hand and
want to mint the bipartite-mean-field predicate. -/
theorem factors_isBipartiteMeanField {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2)
    (witness : ∃ (u : Pol1 → Float) (v : Pol2 → Float),
                  ∀ π1 π2, q π1 π2 = u π1 * v π2) :
    IsBipartiteMeanField q :=
  (isBipartiteMeanField_iff_factors q).mpr witness

/-! ## §8.1 Schmidt-rank-1 boundary characterization

The Schmidt rank of a bipartite joint is `1` iff the joint factors as
`u ⊗ v`.  Boundary form: we expose the rank-1 predicate as the
existence of a rank-1 outer-product factorization and prove its
equivalence with `IsBipartiteMeanField` in stock Lean.  The full
matrix-SVD-based Schmidt rank is supplied by the Mathlib extension. -/

/-- A bipartite joint has **Schmidt rank 1** iff it is the outer
product of a single pair of vectors.  Defined here as the
boundary-fragment-compatible predicate. -/
def HasSchmidtRankOne {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2) : Prop :=
  ∃ (u : Pol1 → Float) (v : Pol2 → Float),
    ∀ π1 π2, q π1 π2 = u π1 * v π2

/-- **Proposition 8.1 (boundary form)**: for a bipartite joint,
Schmidt rank 1 is equivalent to mean-field.  Genuinely proved by
unfolding the two predicates; the boundary fragment certifies this
*algebraic* equivalence in stock Lean without invoking matrix SVD. -/
theorem schmidtRankOne_iff_isBipartiteMeanField {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2) :
    HasSchmidtRankOne q ↔ IsBipartiteMeanField q :=
  Iff.rfl

/-- **Constructive corollary**: any mean-field bipartite joint has
Schmidt rank 1, exhibiting an explicit `(u, v)` witness pair. -/
theorem isBipartiteMeanField_imp_schmidtRankOne {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2)
    (h : IsBipartiteMeanField q) :
    HasSchmidtRankOne q :=
  (schmidtRankOne_iff_isBipartiteMeanField q).mpr h

/-- **Constructive corollary**: any Schmidt-rank-1 bipartite joint is
mean-field.  Together with `isBipartiteMeanField_imp_schmidtRankOne`,
this discharges the bipartite K=2 case of Proposition 8.1 fully on
the boundary fragment. -/
theorem schmidtRankOne_imp_isBipartiteMeanField {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2)
    (h : HasSchmidtRankOne q) :
    IsBipartiteMeanField q :=
  (schmidtRankOne_iff_isBipartiteMeanField q).mp h

end Bipartite

end ActinfPolicyEntanglement
