import Mathlib

namespace MathlibProofs

/--
An outer product has matrix rank at most one.

This is the first intentionally small Mathlib-backed proof slice.  It
validates the separate package's dependency plumbing using Mathlib's
matrix-rank API, without promoting any boundary witness theorem to a
Mathlib-discharged manuscript claim.
-/
theorem vecMulVec_rank_le_one {m n R : Type*} [Fintype n] [CommRing R]
    (w : m → R) (v : n → R) :
    (Matrix.vecMulVec w v).rank ≤ 1 :=
  Matrix.rank_vecMulVec_le w v

/--
Any matrix that is pointwise equal to an outer product has rank at most one.

This v0.2 readiness lemma is still intentionally narrow: it bridges the
project's boundary predicate style ("there exist factors whose products
match every matrix entry") to Mathlib's `Matrix.vecMulVec` rank API. It
does not promote any manuscript theorem row, but it is the exact plumbing
shape needed before a row-specific Proposition 8.1 discharge is built
in this optional package.
-/
theorem rank_le_one_of_pointwise_factorization {m n R : Type*} [Fintype n] [CommRing R]
    (A : Matrix m n R) (u : m → R) (v : n → R)
    (h : ∀ i j, A i j = u i * v j) :
    A.rank ≤ 1 := by
  have hA : A = Matrix.vecMulVec u v := by
    ext i j
    exact h i j
  rw [hA]
  exact Matrix.rank_vecMulVec_le u v

end MathlibProofs
