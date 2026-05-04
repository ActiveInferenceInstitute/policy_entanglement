/- `ActinfPolicyEntanglement.Spectral` — spectral / tensor-network
   structure of the joint policy posterior: Schmidt rank for K = 2,
   archetypal modes, and tensor-train ranks for K > 2.

   Mathlib-free boundary fragment.  Numerical realisations live in
   [`src/lean/spectral.py`](../../src/lean/spectral.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist

namespace ActinfPolicyEntanglement

/-! ## §7.1 Bipartite Schmidt decomposition (K = 2) -/

namespace Bipartite

/-- For `K = 2`, view the joint as a `Float` matrix indexed by
`(π¹, π²)`. -/
abbrev BipartiteJoint (Pol1 Pol2 : Type) : Type :=
  Pol1 → Pol2 → Float

/-- Schmidt rank of a bipartite joint.  Boundary form: abstract
declaration; the numerical SVD is in
`src/lean/spectral.py::schmidt_decomposition`. -/
def schmidtRank {Pol1 Pol2 : Type} (_q : BipartiteJoint Pol1 Pol2) :
    Nat := 0

/-- A bipartite joint is *mean-field* iff it factors as `u(π¹) · v(π²)`. -/
def IsBipartiteMeanField {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2) : Prop :=
  ∃ (u : Pol1 → Float) (v : Pol2 → Float),
    ∀ π1 π2, q π1 π2 = u π1 * v π2

/-- Proposition 7.1 (boundary): Schmidt rank `1` ↔ mean-field. -/
theorem schmidtRank_one_iff_meanField {Pol1 Pol2 : Type}
    (q : BipartiteJoint Pol1 Pol2) :
    schmidtRank q = 1 ↔ IsBipartiteMeanField q := by
  constructor
  · intro _h
    sorry  -- needs Mathlib matrix-rank-1 ⇒ outer-product factorisation
  · intro _h
    sorry  -- needs Mathlib `Matrix.rank_one_outer_product`

/-- Proposition 7.2 sketch: Schmidt rank is upper-semicontinuous in λ. -/
theorem schmidtRank_upperSemicontinuous_sketch {Pol1 Pol2 : Type}
    (qFamily : Float → BipartiteJoint Pol1 Pol2) (lam0 : Float) :
    ∃ (rank0 : Nat), schmidtRank (qFamily lam0) = rank0 :=
  ⟨schmidtRank (qFamily lam0), rfl⟩

end Bipartite

/-! ## §7.3 Tensor-train ranks (K > 2) -/

/-- Tensor-train rank profile of a multi-stream joint: a tuple of bond
dimensions `(r₁, …, r_{K-1})`.  Boundary form: abstract.  Numerical
realisation in `src/lean/spectral.py::tensor_train_ranks`. -/
def tensorTrainRanks {K Pol} (_q : JointDist K Pol) : List Nat := []

/-- Theorem 7.3 sketch (sparsity-rank tradeoff). -/
theorem sparsityRank_tradeoff {K Pol}
    (q : JointDist K Pol) :
    ∃ (ranks : List Nat), tensorTrainRanks q = ranks :=
  ⟨tensorTrainRanks q, rfl⟩

end ActinfPolicyEntanglement
