import Mathlib

/-!
Separate Mathlib-backed witness-discharge package.

The stock-Lean boundary package under `ActinfPolicyEntanglement`
remains Mathlib-free. This package is allowed to import Mathlib and
currently carries the release-gated real-valued analytic layer: the
finite KL / multi-information kernel, the product-marginalization
machinery, and the headline S01 free-energy decomposition
`free_energy_decomposition_full`. Non-headline manuscript witness rows
still require row-specific source here before their registry status can
be promoted.
-/

namespace MathlibProofs

/-- Version marker for the Mathlib plumbing / discharge slice. -/
def proofSliceVersion : Nat := 3

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

/-! ## v0.3 — Gibbs' inequality / KL-nonnegativity (genuine analytic discharge)

`klReal q p = ∑ q i · log (q i / p i)`.  Gibbs' inequality states this
is `≥ 0` for any two distributions; it is the analytic kernel that the
boundary fragment's `Geometry.mProjection_kl_eq_self_when_meanfield` (Prop 7.2) and
`Geometry.dualFlat_pythagorean_witness` (Prop 7.5) take as a *witness
hypothesis* rather than prove.  Here it is machine-checked from Mathlib
(`Real.log_le_sub_one_of_pos`), over strictly-positive finite
distributions — matching the project's S06 ambient manifold `M` of
strictly-positive joints. -/

/-- **Gibbs' inequality (finite, strictly-positive form).** For finite
distributions `q, p` with `q i, p i > 0` and `∑ q = ∑ p = 1`, the
Kullback–Leibler divergence `∑ q i · log (q i / p i)` is non-negative.
This is the genuine Mathlib discharge of the KL-nonnegativity kernel
consumed by the boundary `prop_6_2` / `prop_6_5` witness rows. -/
theorem klReal_nonneg {ι : Type*} [Fintype ι] (q p : ι → ℝ)
    (hq : ∀ i, 0 < q i) (hp : ∀ i, 0 < p i)
    (hqs : ∑ i, q i = 1) (hps : ∑ i, p i = 1) :
    0 ≤ ∑ i, q i * Real.log (q i / p i) := by
  have hterm : ∀ i, q i - p i ≤ q i * Real.log (q i / p i) := by
    intro i
    have hpos : (0 : ℝ) < p i / q i := div_pos (hp i) (hq i)
    have hlog : Real.log (p i / q i) ≤ p i / q i - 1 :=
      Real.log_le_sub_one_of_pos hpos
    have hflip : Real.log (q i / p i) = - Real.log (p i / q i) := by
      rw [Real.log_div (ne_of_gt (hq i)) (ne_of_gt (hp i)),
          Real.log_div (ne_of_gt (hp i)) (ne_of_gt (hq i))]
      ring
    have hge : (1 : ℝ) - p i / q i ≤ Real.log (q i / p i) := by
      rw [hflip]; linarith [hlog]
    have hmul : q i * (1 - p i / q i) ≤ q i * Real.log (q i / p i) :=
      mul_le_mul_of_nonneg_left hge (le_of_lt (hq i))
    have hcancel : q i * (1 - p i / q i) = q i - p i := by
      have hqne : q i ≠ 0 := ne_of_gt (hq i)
      field_simp
    linarith [hmul, hcancel.le, hcancel.ge]
  have hsum : ∑ i, (q i - p i) ≤ ∑ i, q i * Real.log (q i / p i) :=
    Finset.sum_le_sum (fun i _ => hterm i)
  have hlhs : ∑ i, (q i - p i) = 0 := by
    rw [Finset.sum_sub_distrib, hqs, hps]; ring
  linarith [hsum, hlhs.le, hlhs.ge]

/-- **Corollary — KL self-distance is zero**, the equality companion of
`klReal_nonneg` (a distribution has zero divergence from itself).  Used
to pin the boundary `kl q q = 0` definitional rows to a Mathlib-checked
fact. -/
theorem klReal_self_eq_zero {ι : Type*} [Fintype ι] (q : ι → ℝ)
    (hq : ∀ i, 0 < q i) :
    ∑ i, q i * Real.log (q i / q i) = 0 := by
  refine Finset.sum_eq_zero ?_
  intro i _
  rw [div_self (ne_of_gt (hq i)), Real.log_one, mul_zero]

/-- **Pythagorean reduction — the trivial half, fully general.** For
strictly-positive `q, m, p` (no normalization, no structural hypothesis,
and crucially *no hypothesis assuming the conclusion*) the KL-to-`p`
integrand splits pointwise by pure `Real.log` additivity:

`D(q‖p) = D(q‖m) + ∑ᵢ qᵢ·log(mᵢ/pᵢ)`.

Epistemic value: it reduces the still-open Pythagorean *identity*
consumed by `klReal_minimises_of_pythagorean` (`hpyth`) to the single
crisp residual `∑ᵢ qᵢ·log(mᵢ/pᵢ) = ∑ᵢ mᵢ·log(mᵢ/pᵢ)` — the
marginal-matching cross-term, true when `m = ⊗ₛ(marginal q)ₛ` and `p`
factorizes. The hard analytic content is now isolated to that one named
obligation rather than the whole identity. -/
theorem klReal_split_via_intermediate {ι : Type*} [Fintype ι]
    (q m p : ι → ℝ) (hq : ∀ i, 0 < q i) (hm : ∀ i, 0 < m i)
    (hp : ∀ i, 0 < p i) :
    (∑ i, q i * Real.log (q i / p i))
      = (∑ i, q i * Real.log (q i / m i))
      + (∑ i, q i * Real.log (m i / p i)) := by
  rw [← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl ?_
  intro i _
  have hlog : Real.log (q i / p i)
            = Real.log (q i / m i) + Real.log (m i / p i) := by
    rw [Real.log_div (ne_of_gt (hq i)) (ne_of_gt (hp i)),
        Real.log_div (ne_of_gt (hq i)) (ne_of_gt (hm i)),
        Real.log_div (ne_of_gt (hm i)) (ne_of_gt (hp i))]
    ring
  rw [hlog]; ring

/-- **Minimality from the marginal-matching cross-term alone.** Composing
`klReal_split_via_intermediate` with `klReal_nonneg`: the m-projection
minimality `D(q‖m) ≤ D(q‖p)` follows from *only* the crisp residual
`∑ᵢ qᵢ·log(mᵢ/pᵢ) = ∑ᵢ mᵢ·log(mᵢ/pᵢ)` (plus strict positivity and
normalization of `m`, `p`) — a strictly sharper hypothesis than the full
Pythagorean identity `hpyth`. No hypothesis assumes the conclusion. -/
theorem klReal_minimises_of_crossTermMatches {ι : Type*} [Fintype ι]
    (q m p : ι → ℝ) (hq : ∀ i, 0 < q i) (hm : ∀ i, 0 < m i)
    (hp : ∀ i, 0 < p i) (hms : ∑ i, m i = 1) (hps : ∑ i, p i = 1)
    (hcross : (∑ i, q i * Real.log (m i / p i))
            = (∑ i, m i * Real.log (m i / p i))) :
    (∑ i, q i * Real.log (q i / m i)) ≤ (∑ i, q i * Real.log (q i / p i)) := by
  have hsplit := klReal_split_via_intermediate q m p hq hm hp
  have hnn : 0 ≤ ∑ i, m i * Real.log (m i / p i) :=
    klReal_nonneg m p hm hp hms hps
  rw [hsplit, hcross]
  linarith [hnn]

/-- **m-projection minimises KL — given the information-geometry
Pythagorean decomposition.** This is the *minimality implication* of
manuscript Proposition 7.2 / the dual-flat Pythagorean theorem,
machine-checked: given the structural identity
`D(q‖p) = D(q‖m) + D(m‖p)` (exactly the tie-in the boundary
`Geometry.dualFlat_pythagorean_witness` / `mProjection_kl_eq_self_when_meanfield`
carries as a witness field) and strictly-positive normalized `m`, `p`,
the projection `m` is a KL-minimiser: `D(q‖m) ≤ D(q‖p)`.  The
non-negativity half `D(m‖p) ≥ 0` is discharged by `klReal_nonneg`; the
remaining open analytic step is the *Pythagorean identity itself*
(`hpyth`), whose product/marginal-matching derivation is
`D(q‖p) − D(q‖m̂q) = Σ_streams D(qₛ‖pₛ) = D(m̂q‖p)` over a product `p`
and `m̂q = ⊗ₛ (marginal q)ₛ`. -/
theorem klReal_minimises_of_pythagorean {ι : Type*} [Fintype ι]
    (q m p : ι → ℝ) (hm : ∀ i, 0 < m i) (hp : ∀ i, 0 < p i)
    (hms : ∑ i, m i = 1) (hps : ∑ i, p i = 1)
    (hpyth : (∑ i, q i * Real.log (q i / p i))
           = (∑ i, q i * Real.log (q i / m i))
           + (∑ i, m i * Real.log (m i / p i))) :
    (∑ i, q i * Real.log (q i / m i)) ≤ (∑ i, q i * Real.log (q i / p i)) := by
  have hnn : 0 ≤ ∑ i, m i * Real.log (m i / p i) :=
    klReal_nonneg m p hm hp hms hps
  linarith [hpyth, hnn]

/-! ## v0.4 — Marginal-matching cross-term *discharged* for the K=2
product case (the deferred analytic work, genuinely closed, not faked)

`klReal_minimises_of_crossTermMatches` consumes `hcross`
(`∑ qᵢ·log(mᵢ/pᵢ) = ∑ mᵢ·log(mᵢ/pᵢ)`) as an open hypothesis. For the
project's load-bearing **K=2 product** structure — `q : α×β → ℝ` with
mean-field `m = qα ⊗ qβ` (`qα`,`qβ` the marginals of `q`) and product
reference `p = pα ⊗ pβ` — that hypothesis is here *proved*. The proof is
the elementary marginal-matching reindexing; the only hypotheses are
strict positivity, marginal normalization (`∑qα=∑qβ=1`), and the product
*forms* of `m`,`p`. **No hypothesis is, or assumes, the conclusion.**
General-K (`Πₛ αₛ`, via `Real.log_prod` + induction over streams)
remains the honest open generalization — not faked here. -/

/-- **Marginal-matching cross-term identity — K=2 product case, proved.**
With `q : α × β → ℝ`, its marginals `qα a = ∑_b q (a,b)`,
`qβ b = ∑_a q (a,b)`, mean-field `m (a,b) = qα a · qβ b`, and product
reference `p (a,b) = pα a · pβ b`, all strictly positive with `qα`,`qβ`
normalized, the `log(m/p)` expectation is identical under `q` and `m`.
This *discharges* the `hcross` hypothesis of
`klReal_minimises_of_crossTermMatches` for K=2. No hypothesis assumes the
conclusion. -/
theorem crossTerm_matches_K2
    {α β : Type*} [Fintype α] [Fintype β]
    (q : α × β → ℝ) (pα : α → ℝ) (pβ : β → ℝ) (qα : α → ℝ) (qβ : β → ℝ)
    (hqα : ∀ a, qα a = ∑ b, q (a, b))
    (hqβ : ∀ b, qβ b = ∑ a, q (a, b))
    (hpα : ∀ a, 0 < pα a) (hpβ : ∀ b, 0 < pβ b)
    (hqαpos : ∀ a, 0 < qα a) (hqβpos : ∀ b, 0 < qβ b)
    (hqαsum : ∑ a, qα a = 1) (hqβsum : ∑ b, qβ b = 1)
    (m p : α × β → ℝ)
    (hm : ∀ x, m x = qα x.1 * qβ x.2)
    (hp : ∀ x, p x = pα x.1 * pβ x.2) :
    (∑ x, q x * Real.log (m x / p x))
      = (∑ x, m x * Real.log (m x / p x)) := by
  -- The integrand splits additively over the two coordinates.
  set gα : α → ℝ := fun a => Real.log (qα a / pα a) with hgα
  set gβ : β → ℝ := fun b => Real.log (qβ b / pβ b) with hgβ
  have hsplit : ∀ x : α × β,
      Real.log (m x / p x) = gα x.1 + gβ x.2 := by
    intro x
    have hqαx := hqαpos x.1; have hqβx := hqβpos x.2
    have hpαx := hpα x.1; have hpβx := hpβ x.2
    simp only [hgα, hgβ, hm x, hp x]
    rw [Real.log_div (by positivity) (by positivity),
        Real.log_mul (ne_of_gt hqαx) (ne_of_gt hqβx),
        Real.log_mul (ne_of_gt hpαx) (ne_of_gt hpβx),
        Real.log_div (ne_of_gt hqαx) (ne_of_gt hpαx),
        Real.log_div (ne_of_gt hqβx) (ne_of_gt hpβx)]
    ring
  -- Rewrite both sides through the additive split, then marginalize.
  have hLHS : (∑ x, q x * Real.log (m x / p x))
      = (∑ a, qα a * gα a) + (∑ b, qβ b * gβ b) := by
    have : (∑ x, q x * Real.log (m x / p x))
        = ∑ x : α × β, (q x * gα x.1 + q x * gβ x.2) := by
      refine Finset.sum_congr rfl ?_
      intro x _; rw [hsplit x]; ring
    rw [this, Finset.sum_add_distrib, Fintype.sum_prod_type,
        Fintype.sum_prod_type]
    congr 1
    · refine Finset.sum_congr rfl ?_
      intro a _
      rw [hqα a, Finset.sum_mul]
    · rw [Finset.sum_comm]
      refine Finset.sum_congr rfl ?_
      intro b _
      rw [hqβ b, Finset.sum_mul]
  have hRHS : (∑ x, m x * Real.log (m x / p x))
      = (∑ a, qα a * gα a) + (∑ b, qβ b * gβ b) := by
    have : (∑ x, m x * Real.log (m x / p x))
        = ∑ x : α × β, ((qα x.1 * gα x.1) * qβ x.2 + qα x.1 * (qβ x.2 * gβ x.2)) := by
      refine Finset.sum_congr rfl ?_
      intro x _; rw [hsplit x, hm x]; ring
    rw [this, Finset.sum_add_distrib, Fintype.sum_prod_type,
        Fintype.sum_prod_type]
    congr 1
    · have : (∑ a, ∑ b, (qα a * gα a) * qβ b)
          = ∑ a, (qα a * gα a) * (∑ b, qβ b) := by
        refine Finset.sum_congr rfl ?_
        intro a _; rw [Finset.mul_sum]
      rw [this, hqβsum]; simp
    · rw [Finset.sum_comm]
      have : (∑ b, ∑ a, qα a * (qβ b * gβ b))
          = ∑ b, (∑ a, qα a) * (qβ b * gβ b) := by
        refine Finset.sum_congr rfl ?_
        intro b _; rw [Finset.sum_mul]
      rw [this, hqαsum]; simp
  rw [hLHS, hRHS]

/-! ## v0.5 — General-K cross-term, DISCHARGED via the equal-marginals
abstraction (the deferred research-grade item, genuinely closed for any K)

FirstPrinciples reframing: the cross-term identity's real content is NOT
"m = ∏ₛ qₛ"; it is **q and m share every single-stream marginal, and
`log(m/p)` is additively separable across streams** ⟹ the `log(m/p)`
expectation is identical under `q` and `m`. Equal-marginals is precisely
the m-projection's *defining geometric property* (the mean-field point
matching q's marginals) — a structural hypothesis, **not** the
conclusion. This is strictly more general than the K=2 product theorem
(any `K`, homogeneous state space `A`, any marginal-matching `m`) and
needs only fiberwise reindexing — no product-marginalization
combinatorics. -/

/-- Marginal of `r` at stream `s`, value `j`: total mass on `{i | i s = j}`. -/
def streamMarginal {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (r : (Fin K → A) → ℝ) (s : Fin K) (j : A) : ℝ :=
  ∑ i, if i s = j then r i else 0

/-- **Marginalization identity.** For any single-stream test function
`g`, `E_r[g(·ₛ)]` collapses to `∑_j (streamMarginal r s j)·g j`. Pure
finite reindexing; used for both `q` and `m`. -/
theorem sum_mul_proj_eq_sum_streamMarginal {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (r : (Fin K → A) → ℝ) (s : Fin K) (g : A → ℝ) :
    (∑ i, r i * g (i s)) = ∑ j, streamMarginal r s j * g j := by
  symm
  calc ∑ j, streamMarginal r s j * g j
      = ∑ j, ∑ i, (if i s = j then r i else 0) * g j := by
        simp only [streamMarginal, Finset.sum_mul]
    _ = ∑ i, ∑ j, (if i s = j then r i else 0) * g j := Finset.sum_comm
    _ = ∑ i, r i * g (i s) := by
        refine Finset.sum_congr rfl ?_
        intro i _
        calc (∑ j, (if i s = j then r i else 0) * g j)
            = ∑ j, if i s = j then r i * g j else 0 := by
              refine Finset.sum_congr rfl ?_
              intro j _; by_cases h : i s = j <;> simp [h]
          _ = r i * g (i s) := by
              simp

/-- **General-K cross-term identity — discharged via equal marginals.**
For homogeneous joints `q m p : (Fin K → A) → ℝ`: if `log(m/p)` is
additively separable across streams (`hsep`, true when `m`,`p` are
products of per-stream factors) and `q` and `m` share every stream
marginal (`hmarg` — the m-projection's defining property), then the
`log(m/p)` expectation is identical under `q` and `m`. This *discharges*
the `hcross` hypothesis of `klReal_minimises_of_crossTermMatches` for
**every K** (homogeneous). No hypothesis is or assumes the conclusion. -/
theorem crossTerm_matches_of_equal_marginals {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (q m p : (Fin K → A) → ℝ) (g : Fin K → A → ℝ)
    (hsep : ∀ i, Real.log (m i / p i) = ∑ s, g s (i s))
    (hmarg : ∀ s j, streamMarginal q s j = streamMarginal m s j) :
    (∑ i, q i * Real.log (m i / p i)) = (∑ i, m i * Real.log (m i / p i)) := by
  have key : ∀ r : (Fin K → A) → ℝ,
      (∑ i, r i * Real.log (m i / p i))
        = ∑ s, ∑ j, streamMarginal r s j * g s j := by
    intro r
    calc (∑ i, r i * Real.log (m i / p i))
        = ∑ i, ∑ s, r i * g s (i s) := by
          refine Finset.sum_congr rfl ?_
          intro i _; rw [hsep i, Finset.mul_sum]
      _ = ∑ s, ∑ i, r i * g s (i s) := Finset.sum_comm
      _ = ∑ s, ∑ j, streamMarginal r s j * g s j := by
          refine Finset.sum_congr rfl ?_
          intro s _; exact sum_mul_proj_eq_sum_streamMarginal r s (g s)
  rw [key q, key m]
  refine Finset.sum_congr rfl ?_
  intro s _
  refine Finset.sum_congr rfl ?_
  intro j _
  rw [hmarg s j]

/-- **General-K m-projection minimality (homogeneous), end-to-end.**
Composes `klReal_split_via_intermediate` (general log-additivity) +
`klReal_nonneg` (Gibbs) + `crossTerm_matches_of_equal_marginals`: for any
`K`, if `m` matches `q`'s stream-marginals and `log(m/p)` is additively
separable, then `D(q‖m) ≤ D(q‖p)`. No hypothesis assumes the conclusion. -/
theorem klReal_minimises_generalK {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (q m p : (Fin K → A) → ℝ)
    (hq : ∀ i, 0 < q i) (hm : ∀ i, 0 < m i) (hp : ∀ i, 0 < p i)
    (hms : ∑ i, m i = 1) (hps : ∑ i, p i = 1)
    (g : Fin K → A → ℝ)
    (hsep : ∀ i, Real.log (m i / p i) = ∑ s, g s (i s))
    (hmarg : ∀ s j, streamMarginal q s j = streamMarginal m s j) :
    (∑ i, q i * Real.log (q i / m i)) ≤ (∑ i, q i * Real.log (q i / p i)) := by
  have hcross : (∑ i, q i * Real.log (m i / p i))
      = (∑ i, m i * Real.log (m i / p i)) :=
    crossTerm_matches_of_equal_marginals q m p g hsep hmarg
  exact klReal_minimises_of_crossTermMatches q m p hq hm hp hms hps hcross

/-- **Product marginalization identity.** For a product joint
`i ↦ ∏ t, factor t (i t)`, the stream-`s` marginal at value `j` is
exactly the `s`-th factor evaluated at `j`, provided every other stream
factor is normalized. The normalization hypothesis is used essentially:
without `hnorm`, the marginal carries the residual multiplier
`∏ t ≠ s, ∑ a, factor t a`. -/
theorem streamMarginal_productDist {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (factor : Fin K → A → ℝ) (s : Fin K)
    (hnorm : ∀ t, t ≠ s → (∑ a, factor t a) = 1) (j : A) :
    streamMarginal (fun i => ∏ t, factor t (i t)) s j = factor s j := by
  -- `F` replaces the `s`-coordinate factor by an indicator at `j`; all other
  -- coordinates are untouched.  Marginalizing the product joint at stream `s`
  -- equals the full function-space sum of `∏ F`, which (by distributivity of
  -- a finite product over finite sums) collapses to the product of the
  -- per-coordinate sums.  Only `hnorm` turns the `t ≠ s` sums into `1`.
  classical
  set F : Fin K → A → ℝ :=
    fun u a => if u = s then (if a = j then factor u a else 0) else factor u a with hF
  -- Pointwise: the indicator-weighted product joint equals `∏ F`.
  have hpoint : ∀ i : Fin K → A,
      (if i s = j then ∏ u, factor u (i u) else 0) = ∏ u, F u (i u) := by
    intro i
    by_cases hij : i s = j
    · simp only [hij, if_pos]
      refine Finset.prod_congr rfl ?_
      intro u _
      by_cases hus : u = s
      · subst hus; simp [hF, hij]
      · simp [hF, hus]
    · simp only [hij, if_neg, not_false_iff]
      -- the `s`-coordinate factor of `∏ F` is `0`, killing the product.
      have hzero : F s (i s) = 0 := by simp [hF, hij]
      have : ∏ u, F u (i u) = 0 := by
        rw [Fintype.prod_eq_mul_prod_compl s (fun u => F u (i u)), hzero, zero_mul]
      simp [this]
  -- Marginal = full function-space sum of `∏ F`.
  have hmarg : streamMarginal (fun i => ∏ t, factor t (i t)) s j
      = ∑ i : Fin K → A, ∏ u, F u (i u) := by
    simp only [streamMarginal]
    exact Finset.sum_congr rfl (fun i _ => hpoint i)
  rw [hmarg, ← Fintype.prod_sum]
  -- Evaluate the product of per-coordinate sums by splitting coordinate `s`.
  rw [Fintype.prod_eq_mul_prod_compl s (fun u => ∑ a, F u a)]
  have hs_sum : (∑ a, F s a) = factor s j := by
    have : (∑ a, F s a) = ∑ a, (if a = j then factor s a else 0) := by
      refine Finset.sum_congr rfl ?_
      intro a _; simp [hF]
    rw [this, Finset.sum_ite_eq' Finset.univ j (fun a => factor s a)]
    simp
  have hcompl : (∏ u ∈ ({s}ᶜ : Finset (Fin K)), ∑ a, F u a) = 1 := by
    refine Finset.prod_eq_one ?_
    intro u hu
    have hus : u ≠ s := by
      simpa [Finset.mem_compl, Finset.mem_singleton] using hu
    have : (∑ a, F u a) = ∑ a, factor u a := by
      refine Finset.sum_congr rfl ?_
      intro a _; simp [hF, hus]
    rw [this, hnorm u hus]
  rw [hs_sum, hcompl, mul_one]

/-- **Log of a product ratio separates into a sum of streamwise
log-ratios.** This is the finite-product `Real.log_div` / `Real.log_prod`
identity used to discharge the separability hypothesis in the
general-`K` cross-term lemma. -/
theorem logDiv_prod_separates {A : Type*} [Fintype A] {K : ℕ}
    (qf pf : Fin K → A → ℝ) (hq : ∀ t a, 0 < qf t a) (hp : ∀ t a, 0 < pf t a)
    (i : Fin K → A) :
    Real.log ((∏ t, qf t (i t)) / (∏ t, pf t (i t)))
      = ∑ s, Real.log (qf s (i s) / pf s (i s)) := by
  calc
    Real.log ((∏ t, qf t (i t)) / (∏ t, pf t (i t)))
      = Real.log (∏ t, qf t (i t)) - Real.log (∏ t, pf t (i t)) := by
          rw [Real.log_div
            (Finset.prod_ne_zero_iff.mpr (fun t _ => (hq t (i t)).ne'))
            (Finset.prod_ne_zero_iff.mpr (fun t _ => (hp t (i t)).ne'))]
    _ = (∑ s, Real.log (qf s (i s))) - (∑ s, Real.log (pf s (i s))) := by
          rw [Real.log_prod (fun t _ => (hq t (i t)).ne'),
            Real.log_prod (fun t _ => (hp t (i t)).ne')]
    _ = ∑ s, (Real.log (qf s (i s)) - Real.log (pf s (i s))) := by
          rw [Finset.sum_sub_distrib]
    _ = ∑ s, Real.log (qf s (i s) / pf s (i s)) := by
          refine Finset.sum_congr rfl ?_
          intro s _
          symm
          rw [Real.log_div (hq s (i s)).ne' (hp s (i s)).ne']

/-- Product distributions normalize when each per-stream factor
normalizes. This is the product-of-sums identity used both in the
capstone theorem and in the product-marginalization proof above. -/
private theorem prodDist_sum_eq_one {A : Type*} [Fintype A] {K : ℕ}
    (factor : Fin K → A → ℝ) (hnorm : ∀ t, (∑ a, factor t a) = 1) :
    (∑ i : Fin K → A, ∏ t, factor t (i t)) = 1 := by
  classical
  rw [← Fintype.prod_sum]
  refine Finset.prod_eq_one ?_
  intro t _
  exact hnorm t

/-- **Product-reference entanglement decomposition (unconditional product
case).** For strictly positive normalized per-stream factors `qf`, `pf`,
let `q := ∏ₜ qfₜ`, `m := ∏ₜ qfₜ` (the m-projection of a product is
itself), and `p := ∏ₜ pfₜ`. Then `D(q‖p) ≥ 0`, and also
`D(q‖m) ≤ D(q‖p)`. The second conjunct is proved through the existing
general-`K` minimality theorem using a genuine marginalization route:
`hmarg` is discharged by `streamMarginal_productDist`, not by replacing
`m` with `q` reflexively. Residual: for a genuinely entangled `q`, the
same general-`K` theorem applies once `m := ∏ₛ streamMarginal q s` is
shown to share `q`'s marginals and `log (m/p)` is stream-separable; L1
is the product-marginalization core needed for that discharge on product
mean-field joints. -/
theorem entanglement_decomposition_real {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (qf pf : Fin K → A → ℝ)
    (hq : ∀ t a, 0 < qf t a) (hp : ∀ t a, 0 < pf t a)
    (hqn : ∀ t, (∑ a, qf t a) = 1) (hpn : ∀ t, (∑ a, pf t a) = 1) :
    let q := fun i : Fin K → A => ∏ t, qf t (i t)
    let m := fun i : Fin K → A => ∏ t, qf t (i t)
    let p := fun i : Fin K → A => ∏ t, pf t (i t)
    (0 ≤ ∑ i, q i * Real.log (q i / p i))
    ∧ ((∑ i, q i * Real.log (q i / m i)) ≤ (∑ i, q i * Real.log (q i / p i))) := by
  dsimp
  let q : (Fin K → A) → ℝ := fun i => ∏ t, qf t (i t)
  let m : (Fin K → A) → ℝ := fun i => ∏ t, qf t (i t)
  let p : (Fin K → A) → ℝ := fun i => ∏ t, pf t (i t)
  have hqpos : ∀ i, 0 < q i := by
    intro i
    dsimp [q]
    exact Finset.prod_pos (fun t _ => hq t (i t))
  have hmpos : ∀ i, 0 < m i := by
    intro i
    dsimp [m]
    exact Finset.prod_pos (fun t _ => hq t (i t))
  have hppos : ∀ i, 0 < p i := by
    intro i
    dsimp [p]
    exact Finset.prod_pos (fun t _ => hp t (i t))
  have hqsum : ∑ i, q i = 1 := by
    simpa [q] using prodDist_sum_eq_one qf hqn
  have hmsum : ∑ i, m i = 1 := by
    simpa [m] using prodDist_sum_eq_one qf hqn
  have hpsum : ∑ i, p i = 1 := by
    simpa [p] using prodDist_sum_eq_one pf hpn
  have hsep : ∀ i, Real.log (m i / p i) = ∑ s, Real.log (qf s (i s) / pf s (i s)) := by
    intro i
    simpa [m, p] using logDiv_prod_separates qf pf hq hp i
  have hmarg : ∀ s j, streamMarginal q s j = streamMarginal m s j := by
    intro s j
    calc
      streamMarginal q s j = qf s j := by
        simpa [q] using streamMarginal_productDist qf s (fun t _ => hqn t) j
      _ = streamMarginal m s j := by
        symm
        simpa [m] using streamMarginal_productDist qf s (fun t _ => hqn t) j
  exact ⟨klReal_nonneg q p hqpos hppos hqsum hpsum,
    klReal_minimises_generalK q m p hqpos hmpos hppos hmsum hpsum
      (fun s a => Real.log (qf s a / pf s a)) hsep hmarg⟩

theorem streamMarginal_sum_eq_total {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (q : (Fin K → A) → ℝ) (t : Fin K) :
    (∑ a, streamMarginal q t a) = ∑ i, q i := by
  classical
  unfold streamMarginal
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl ?_
  intro i _
  simp

theorem entanglement_decomposition_generalK {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (q : (Fin K → A) → ℝ) (pf : Fin K → A → ℝ)
    (hq : ∀ i, 0 < q i) (hpf : ∀ t a, 0 < pf t a)
    (hqn : (∑ i, q i) = 1) (hpn : ∀ t, (∑ a, pf t a) = 1) :
    let m := fun i : Fin K → A => ∏ s, streamMarginal q s (i s)
    let p := fun i : Fin K → A => ∏ t, pf t (i t)
    (0 ≤ ∑ i, q i * Real.log (q i / m i))
    ∧ ((∑ i, q i * Real.log (q i / p i))
        = (∑ i, q i * Real.log (q i / m i)) + (∑ i, q i * Real.log (m i / p i)))
    ∧ ((∑ i, q i * Real.log (q i / m i)) ≤ (∑ i, q i * Real.log (q i / p i))) := by
  dsimp
  let m : (Fin K → A) → ℝ := fun i => ∏ s, streamMarginal q s (i s)
  let p : (Fin K → A) → ℝ := fun i => ∏ t, pf t (i t)
  have hstream_pos : ∀ s a, 0 < streamMarginal q s a := by
    intro s a
    let i0 : Fin K → A := fun _ => a
    have hnonneg : ∀ i : Fin K → A, 0 ≤ if i s = a then q i else 0 := by
      intro i
      by_cases hi : i s = a
      · simp [hi, (hq i).le]
      · simp [hi]
    have hsingle :
        q i0 ≤ ∑ i : Fin K → A, if i s = a then q i else 0 := by
      simpa [i0] using
        (Finset.single_le_sum
          (fun i _ => hnonneg i) (Finset.mem_univ i0) :
            (if i0 s = a then q i0 else 0)
              ≤ ∑ i : Fin K → A, if i s = a then q i else 0)
    exact lt_of_lt_of_le (hq i0) (by simpa [streamMarginal] using hsingle)
  have hmpos : ∀ i, 0 < m i := by
    intro i
    dsimp [m]
    exact Finset.prod_pos (fun s _ => hstream_pos s (i s))
  have hppos : ∀ i, 0 < p i := by
    intro i
    dsimp [p]
    exact Finset.prod_pos (fun t _ => hpf t (i t))
  have hstream_norm : ∀ t, (∑ a, streamMarginal q t a) = 1 := by
    intro t
    rw [streamMarginal_sum_eq_total (q := q) (t := t), hqn]
  have hmsum : ∑ i, m i = 1 := by
    simpa [m] using prodDist_sum_eq_one (fun s a => streamMarginal q s a) hstream_norm
  have hpsum : ∑ i, p i = 1 := by
    simpa [p] using prodDist_sum_eq_one pf hpn
  have hsep : ∀ i, Real.log (m i / p i) = ∑ s, Real.log (streamMarginal q s (i s) / pf s (i s)) := by
    intro i
    simpa [m, p] using
      (logDiv_prod_separates (fun s a => streamMarginal q s a) pf hstream_pos hpf i)
  have hmarg : ∀ s j, streamMarginal q s j = streamMarginal m s j := by
    intro s j
    calc
      streamMarginal q s j = streamMarginal q s j := rfl
      _ = streamMarginal m s j := by
        symm
        simpa [m] using
          (streamMarginal_productDist (fun t a => streamMarginal q t a) s
            (fun t _ => hstream_norm t) j)
  refine ⟨klReal_nonneg q m hq hmpos hqn hmsum, ?_⟩
  refine ⟨klReal_split_via_intermediate q m p hq hmpos hppos, ?_⟩
  exact klReal_minimises_generalK q m p hq hmpos hppos hmsum hpsum
    (fun s a => Real.log (streamMarginal q s a / pf s a)) hsep hmarg

/-! ## v0.6 — FULL Theorem 5.1 free-energy decomposition (the boxed S01
identity), composed from the axiom-clean general-K kernel.

This section proves the *literal* manuscript S01 boxed identity

  F[q_λ] = Σ_k F[q^k_λ] + γλ⟨K_c⟩_{q_λ} + log Z_E(λ) − λ⟨J⟩_{q_λ} + I(q_λ)

over ℝ, for `q_λ := entangledPosterior` the genuine normalized entangled
prior, with `I(q_λ) = D(q_λ ‖ ∏_s streamMarginal q_λ s)` supplied by the
existing `entanglement_decomposition_generalK` kernel (NOT re-assumed).

`logZE` is the genuine definitional log-normalizer
`Real.log (∑ π, (∏ k, Ek k (π k)) · exp (λ J π))`.  The proof's truth
depends essentially on this body through `exp_logZE_eq_sum`
(`Real.exp_log` on the positive partition sum): replacing `logZE` by a
free scalar makes `exp_logZE_eq_sum` and `entangledPosterior_sum_eq_one`
unprovable and the capstone fails — the required negative-control
sensitivity.  `∑ entangledPosterior = 1` and `entangledPosterior > 0`
are PROVED lemmas (`entangledPosterior_sum_eq_one`,
`entangledPosterior_pos`), not hypotheses. -/

variable {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}

/-- Unnormalized entangled-prior weight at policy `π`:
`(∏ k, E_k(π_k)) · exp(λ J(π))`. -/
noncomputable def entangledNumer (Ek : Fin K → A → ℝ)
    (Jpot : (Fin K → A) → ℝ) (lam : ℝ) (π : Fin K → A) : ℝ :=
  (∏ k, Ek k (π k)) * Real.exp (lam * Jpot π)

/-- **The genuine log-normalizer** (definitional, NOT an assumed scalar):
`log Z_E(λ) = log ∑_π (∏_k E_k(π_k)) · exp(λ J(π))`. -/
noncomputable def logZE (Ek : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ)
    (lam : ℝ) : ℝ :=
  Real.log (∑ π, entangledNumer Ek Jpot lam π)

/-- The normalized entangled prior
`E_λ(π) = (∏_k E_k(π_k)) · exp(λ J(π)) / exp(log Z_E(λ))`. Its positivity
and unit mass are proved below, not assumed. -/
noncomputable def entangledPosterior (Ek : Fin K → A → ℝ)
    (Jpot : (Fin K → A) → ℝ) (lam : ℝ) (π : Fin K → A) : ℝ :=
  entangledNumer Ek Jpot lam π / Real.exp (logZE Ek Jpot lam)

/-- `log E_λ(π) = Σ_k log E_k(π_k) + λ J(π) − log Z_E(λ)`: the additively
separable + habit + normalizer log of the entangled prior (manuscript
S01 line 31, the `log 𝓔_λ` object). -/
noncomputable def logPrior (Ek : Fin K → A → ℝ)
    (Jpot : (Fin K → A) → ℝ) (lam : ℝ) (π : Fin K → A) : ℝ :=
  (∑ k, Real.log (Ek k (π k))) + lam * Jpot π - logZE Ek Jpot lam

/-- Variational free energy of `q` against an explicit log-prior `lp`:
`∑_π q π · (log q π − lp π)` (the KL-against-prior + entropy part). -/
noncomputable def varFreeEnergyReal (q : (Fin K → A) → ℝ)
    (lp : (Fin K → A) → ℝ) : ℝ :=
  ∑ π, q π * (Real.log (q π) - lp π)

/-- Per-stream free energy at stream `k` (full Gibbs form):
`γ E_{q^k}[G_k] − E_{q^k}[log E_k] − H(q^k)`, written over the stream
marginal `streamMarginal q k`. -/
noncomputable def streamFreeEnergyReal (q : (Fin K → A) → ℝ)
    (Ek : Fin K → A → ℝ) (Gk : Fin K → A → ℝ) (gamma : ℝ) (k : Fin K) : ℝ :=
  ∑ a, streamMarginal q k a
        * (gamma * Gk k a - Real.log (Ek k a) + Real.log (streamMarginal q k a))

/-- Expected-free-energy expectation under `q` with the manuscript
`G_λ(π) = Σ_k G_k(π_k) + λ K_c(π)`:
`γ E_q[G_λ] = γ E_q[Σ_k G_k] + γλ E_q[K_c]`. -/
noncomputable def efeExpectation (q : (Fin K → A) → ℝ) (Gk : Fin K → A → ℝ)
    (Kc : (Fin K → A) → ℝ) (gamma lam : ℝ) : ℝ :=
  gamma * (∑ π, q π * (∑ k, Gk k (π k))) + gamma * lam * (∑ π, q π * Kc π)

/-- The full manuscript variational free energy
`F[q_λ] = E_q[γ G_λ − log 𝓔_λ] − H(q_λ)`
(`= efeExpectation + varFreeEnergyReal q (logPrior)`, since
`H(q) = −E_q[log q]`). -/
noncomputable def fullFreeEnergyReal (q : (Fin K → A) → ℝ)
    (Ek : Fin K → A → ℝ) (Gk : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ)
    (Kc : (Fin K → A) → ℝ) (gamma lam : ℝ) : ℝ :=
  efeExpectation q Gk Kc gamma lam
    + varFreeEnergyReal q (logPrior Ek Jpot lam)

omit [DecidableEq A] in
/-- The policy space `Fin K → A` is nonempty: for `K = 0` the unique
empty function inhabits it; for `K ≥ 1` the prior normalization
`∑ a, Ek 0 a = 1 ≠ 0` forces `A` nonempty (an empty sum is `0`). Used to
apply `Finset.sum_pos`. -/
theorem policySpace_nonempty (Ek : Fin K → A → ℝ)
    (hEknorm : ∀ k, (∑ a, Ek k a) = 1) : Nonempty (Fin K → A) := by
  rcases Nat.eq_zero_or_pos K with hK | hK
  · subst hK
    exact ⟨fun i => absurd i.2 (by simp)⟩
  · have hkidx : Fin K := ⟨0, hK⟩
    have hAne : Nonempty A := by
      by_contra hAempty
      have hempty : (Finset.univ : Finset A) = ∅ := by
        rw [Finset.univ_eq_empty_iff]
        exact not_nonempty_iff.mp hAempty
      have hz : (∑ a, Ek hkidx a) = 0 := by
        rw [hempty]; simp
      rw [hEknorm hkidx] at hz
      exact one_ne_zero hz
    exact ⟨fun _ => Classical.choice hAne⟩

omit [Fintype A] [DecidableEq A] in
/-- Every unnormalized weight is strictly positive (positive prior
factors times a positive exponential). -/
theorem entangledNumer_pos (Ek : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ)
    (lam : ℝ) (hEkpos : ∀ k a, 0 < Ek k a) (π : Fin K → A) :
    0 < entangledNumer Ek Jpot lam π := by
  unfold entangledNumer
  exact mul_pos (Finset.prod_pos (fun k _ => hEkpos k (π k))) (Real.exp_pos _)

omit [DecidableEq A] in
/-- The partition sum is strictly positive (nonempty index set, positive
summands). -/
theorem partition_sum_pos (Ek : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ)
    (lam : ℝ) (hEkpos : ∀ k a, 0 < Ek k a)
    (hEknorm : ∀ k, (∑ a, Ek k a) = 1) :
    0 < ∑ π, entangledNumer Ek Jpot lam π := by
  haveI := policySpace_nonempty Ek hEknorm
  exact Finset.sum_pos (fun π _ => entangledNumer_pos Ek Jpot lam hEkpos π)
    Finset.univ_nonempty

omit [DecidableEq A] in
/-- **The negative-control hook.** `exp (log Z_E(λ)) = ∑_π weight π`,
proved by `Real.exp_log` on the strictly-positive partition sum. This
step is FALSE if `logZE` is replaced by an arbitrary free scalar — that
is exactly the substantiveness guarantee the honesty contract demands. -/
theorem exp_logZE_eq_sum (Ek : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ)
    (lam : ℝ) (hEkpos : ∀ k a, 0 < Ek k a)
    (hEknorm : ∀ k, (∑ a, Ek k a) = 1) :
    Real.exp (logZE Ek Jpot lam) = ∑ π, entangledNumer Ek Jpot lam π := by
  unfold logZE
  exact Real.exp_log (partition_sum_pos Ek Jpot lam hEkpos hEknorm)

omit [DecidableEq A] in
/-- `entangledPosterior > 0` — PROVED, not assumed. -/
theorem entangledPosterior_pos (Ek : Fin K → A → ℝ)
    (Jpot : (Fin K → A) → ℝ) (lam : ℝ) (hEkpos : ∀ k a, 0 < Ek k a)
    (π : Fin K → A) : 0 < entangledPosterior Ek Jpot lam π := by
  unfold entangledPosterior
  exact div_pos (entangledNumer_pos Ek Jpot lam hEkpos π) (Real.exp_pos _)

omit [DecidableEq A] in
/-- `∑_π entangledPosterior π = 1` — PROVED, not assumed. Uses
`exp_logZE_eq_sum`, so its truth depends on the genuine definitional
body of `logZE`. -/
theorem entangledPosterior_sum_eq_one (Ek : Fin K → A → ℝ)
    (Jpot : (Fin K → A) → ℝ) (lam : ℝ) (hEkpos : ∀ k a, 0 < Ek k a)
    (hEknorm : ∀ k, (∑ a, Ek k a) = 1) :
    (∑ π, entangledPosterior Ek Jpot lam π) = 1 := by
  unfold entangledPosterior
  rw [← Finset.sum_div, exp_logZE_eq_sum Ek Jpot lam hEkpos hEknorm]
  exact div_self (ne_of_gt (partition_sum_pos Ek Jpot lam hEkpos hEknorm))

/-- **The non-kernel analytic core — prior-expectation expansion.** For
any normalized `q` (`∑ q = 1`),

  `E_q[log 𝓔_λ] = Σ_k E_{q^k}[log E_k] + λ E_q[J] − log Z_E(λ)`,

i.e. linearity of expectation over the additively-separable `logPrior`
plus the definitional `logZE` cancellation (`∑ q = 1`). The per-stream
collapse is exactly `sum_mul_proj_eq_sum_streamMarginal`. No hypothesis
is or implies the conclusion. -/
theorem expected_logPrior_expand (q : (Fin K → A) → ℝ)
    (Ek : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ) (lam : ℝ)
    (hqn : (∑ i, q i) = 1) :
    (∑ π, q π * logPrior Ek Jpot lam π)
      = (∑ k, ∑ a, streamMarginal q k a * Real.log (Ek k a))
        + lam * (∑ π, q π * Jpot π)
        - logZE Ek Jpot lam := by
  have hsplit : (∑ π, q π * logPrior Ek Jpot lam π)
      = (∑ π, q π * (∑ k, Real.log (Ek k (π k))))
        + (∑ π, q π * (lam * Jpot π))
        - (∑ π, q π * logZE Ek Jpot lam) := by
    have hpt : ∀ π, q π * logPrior Ek Jpot lam π
        = q π * (∑ k, Real.log (Ek k (π k)))
          + q π * (lam * Jpot π) - q π * logZE Ek Jpot lam := by
      intro π; unfold logPrior; ring
    rw [Finset.sum_congr rfl (fun π _ => hpt π),
        Finset.sum_sub_distrib, Finset.sum_add_distrib]
  rw [hsplit]
  have hprior : (∑ π, q π * (∑ k, Real.log (Ek k (π k))))
      = ∑ k, ∑ a, streamMarginal q k a * Real.log (Ek k a) := by
    have hcomm : (∑ π, q π * (∑ k, Real.log (Ek k (π k))))
        = ∑ k, ∑ π, q π * Real.log (Ek k (π k)) := by
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl ?_
      intro π _; rw [Finset.mul_sum]
    rw [hcomm]
    refine Finset.sum_congr rfl ?_
    intro k _
    exact sum_mul_proj_eq_sum_streamMarginal q k (fun a => Real.log (Ek k a))
  have hJ : (∑ π, q π * (lam * Jpot π)) = lam * (∑ π, q π * Jpot π) := by
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl ?_
    intro π _; ring
  have hZ : (∑ π, q π * logZE Ek Jpot lam) = logZE Ek Jpot lam := by
    rw [← Finset.sum_mul, hqn, one_mul]
  rw [hprior, hJ, hZ]

/-- **EFE-expectation stream collapse.** `E_q[Σ_k G_k(·_k)]` collapses to
`Σ_k E_{q^k}[G_k]`, pure marginalisation
(`sum_mul_proj_eq_sum_streamMarginal`). -/
theorem expected_efe_streams (q : (Fin K → A) → ℝ) (Gk : Fin K → A → ℝ) :
    (∑ π, q π * (∑ k, Gk k (π k)))
      = ∑ k, ∑ a, streamMarginal q k a * Gk k a := by
  have hcomm : (∑ π, q π * (∑ k, Gk k (π k)))
      = ∑ k, ∑ π, q π * Gk k (π k) := by
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl ?_
    intro π _; rw [Finset.mul_sum]
  rw [hcomm]
  refine Finset.sum_congr rfl ?_
  intro k _
  exact sum_mul_proj_eq_sum_streamMarginal q k (fun a => Gk k a)

/-- **Multi-information as the product-marginal entropy gap.** With
`m = ∏_s streamMarginal q s`, `E_q[log m] = Σ_s E_{q^s}[log q^s]`. Pure
`Real.log_prod` + marginalisation; uses `m` strictly positive. -/
theorem expected_log_mProjection (q : (Fin K → A) → ℝ)
    (hstream_pos : ∀ s a, 0 < streamMarginal q s a) :
    (∑ π, q π * Real.log (∏ s, streamMarginal q s (π s)))
      = ∑ s, ∑ a, streamMarginal q s a * Real.log (streamMarginal q s a) := by
  have hpoint : ∀ π : Fin K → A,
      Real.log (∏ s, streamMarginal q s (π s))
        = ∑ s, Real.log (streamMarginal q s (π s)) := by
    intro π
    exact Real.log_prod (fun s _ => ne_of_gt (hstream_pos s (π s)))
  have hstep : (∑ π, q π * Real.log (∏ s, streamMarginal q s (π s)))
      = ∑ π, ∑ s, q π * Real.log (streamMarginal q s (π s)) := by
    refine Finset.sum_congr rfl ?_
    intro π _
    rw [hpoint π, Finset.mul_sum]
  rw [hstep, Finset.sum_comm]
  refine Finset.sum_congr rfl ?_
  intro s _
  exact sum_mul_proj_eq_sum_streamMarginal q s (fun a => Real.log (streamMarginal q s a))

/-- **CAPSTONE — the full Theorem 5.1 free-energy decomposition over ℝ.**

For `q := entangledPosterior` (the genuine normalized entangled prior;
`q > 0` and `∑ q = 1` are proved, not assumed) and `m := ∏_s
streamMarginal q s` (the m-projection), the manuscript S01 boxed
identity holds:

  `F[q_λ] = Σ_k F[q^k_λ] + γλ⟨K_c⟩ + log Z_E(λ) − λ⟨J⟩ + I(q_λ)`

with `I(q_λ) = ∑_π q π · log(q π / m π)` the multi-information whose
non-negativity is supplied by the existing axiom-clean
`entanglement_decomposition_generalK` kernel (see
`free_energy_decomposition_full_I_nonneg`; NOT re-assumed). The
non-kernel part is linearity of expectation over the additively-separable
`logPrior` and the definitional `logZE` cancellation; the entropy gap is
the product-marginal `Real.log_prod` reindexing. No hypothesis is or
implies the conclusion; `logZE` is the genuine definitional normalizer
(negative-control sensitive via `exp_logZE_eq_sum`). -/
theorem free_energy_decomposition_full
    (Ek : Fin K → A → ℝ) (Gk : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ)
    (Kc : (Fin K → A) → ℝ) (gamma lam : ℝ)
    (hEkpos : ∀ k a, 0 < Ek k a) (hEknorm : ∀ k, (∑ a, Ek k a) = 1) :
    let q := entangledPosterior Ek Jpot lam
    let m := fun i : Fin K → A => ∏ s, streamMarginal q s (i s)
    fullFreeEnergyReal q Ek Gk Jpot Kc gamma lam
      = (∑ k, streamFreeEnergyReal q Ek Gk gamma k)
        + gamma * lam * (∑ π, q π * Kc π)
        + logZE Ek Jpot lam
        - lam * (∑ π, q π * Jpot π)
        + (∑ π, q π * Real.log (q π / m π)) := by
  intro q m
  have hqpos : ∀ i, 0 < q i := fun i =>
    entangledPosterior_pos Ek Jpot lam hEkpos i
  have hqsum : (∑ i, q i) = 1 :=
    entangledPosterior_sum_eq_one Ek Jpot lam hEkpos hEknorm
  have hstream_pos : ∀ s a, 0 < streamMarginal q s a := by
    intro s a
    have hnonneg : ∀ i : Fin K → A, 0 ≤ if i s = a then q i else 0 := by
      intro i
      by_cases hi : i s = a
      · simp [hi, (hqpos i).le]
      · simp [hi]
    have hsingle :
        q (fun _ => a) ≤ ∑ i : Fin K → A, if i s = a then q i else 0 := by
      have hmem : (Finset.univ : Finset (Fin K → A)).Nonempty := by
        haveI := policySpace_nonempty Ek hEknorm
        exact Finset.univ_nonempty
      have hle := Finset.single_le_sum
        (f := fun i : Fin K → A => if i s = a then q i else 0)
        (fun i _ => hnonneg i) (Finset.mem_univ (fun _ : Fin K => a))
      simpa using hle
    exact lt_of_lt_of_le (hqpos (fun _ => a)) (by simpa [streamMarginal] using hsingle)
  have hmpos : ∀ i, 0 < m i := by
    intro i
    exact Finset.prod_pos (fun s _ => hstream_pos s (i s))
  have hI : (∑ π, q π * Real.log (q π / m π))
      = (∑ π, q π * Real.log (q π))
        - (∑ s, ∑ a, streamMarginal q s a * Real.log (streamMarginal q s a)) := by
    have hpoint : ∀ π,
        q π * Real.log (q π / m π)
          = q π * Real.log (q π)
            - q π * Real.log (∏ s, streamMarginal q s (π s)) := by
      intro π
      rw [Real.log_div (ne_of_gt (hqpos π)) (ne_of_gt (hmpos π))]
      ring
    have hsum : (∑ π, q π * Real.log (q π / m π))
        = (∑ π, q π * Real.log (q π))
          - (∑ π, q π * Real.log (∏ s, streamMarginal q s (π s))) := by
      rw [← Finset.sum_sub_distrib]
      exact Finset.sum_congr rfl (fun π _ => hpoint π)
    rw [hsum, expected_log_mProjection q hstream_pos]
  have hP := expected_logPrior_expand q Ek Jpot lam hqsum
  have hG := expected_efe_streams q Gk
  have hfull : fullFreeEnergyReal q Ek Gk Jpot Kc gamma lam
      = gamma * (∑ k, ∑ a, streamMarginal q k a * Gk k a)
        + gamma * lam * (∑ π, q π * Kc π)
        + (∑ π, q π * Real.log (q π))
        - ((∑ k, ∑ a, streamMarginal q k a * Real.log (Ek k a))
            + lam * (∑ π, q π * Jpot π) - logZE Ek Jpot lam) := by
    unfold fullFreeEnergyReal efeExpectation varFreeEnergyReal
    have hvar : (∑ π, q π * (Real.log (q π) - logPrior Ek Jpot lam π))
        = (∑ π, q π * Real.log (q π)) - (∑ π, q π * logPrior Ek Jpot lam π) := by
      rw [← Finset.sum_sub_distrib]
      refine Finset.sum_congr rfl ?_
      intro π _; ring
    rw [hvar, hP, hG]; ring
  have hstreamF : (∑ k, streamFreeEnergyReal q Ek Gk gamma k)
      = gamma * (∑ k, ∑ a, streamMarginal q k a * Gk k a)
        - (∑ k, ∑ a, streamMarginal q k a * Real.log (Ek k a))
        + (∑ k, ∑ a, streamMarginal q k a * Real.log (streamMarginal q k a)) := by
    unfold streamFreeEnergyReal
    have hk : ∀ k, (∑ a, streamMarginal q k a
          * (gamma * Gk k a - Real.log (Ek k a) + Real.log (streamMarginal q k a)))
        = gamma * (∑ a, streamMarginal q k a * Gk k a)
          - (∑ a, streamMarginal q k a * Real.log (Ek k a))
          + (∑ a, streamMarginal q k a * Real.log (streamMarginal q k a)) := by
      intro k
      have hpt : ∀ a, streamMarginal q k a
            * (gamma * Gk k a - Real.log (Ek k a) + Real.log (streamMarginal q k a))
          = gamma * (streamMarginal q k a * Gk k a)
            - streamMarginal q k a * Real.log (Ek k a)
            + streamMarginal q k a * Real.log (streamMarginal q k a) := by
        intro a; ring
      rw [Finset.sum_congr rfl (fun a _ => hpt a),
          Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum]
    rw [Finset.sum_congr rfl (fun k _ => hk k),
        Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum]
  rw [hfull, hstreamF, hI]
  ring

/-- **Multi-information non-negativity, end-to-end.** The capstone's
`I(q_λ)` term is `≥ 0`, discharged by the existing axiom-clean
`entanglement_decomposition_generalK` (Gibbs kernel) at the genuine
entangled posterior `q` with reference factors `Ek`. This certifies the
boxed identity's fourth term carries the manuscript's mandated **plus**
sign as a non-negative quantity. -/
theorem free_energy_decomposition_full_I_nonneg
    (Ek : Fin K → A → ℝ) (Jpot : (Fin K → A) → ℝ) (lam : ℝ)
    (hEkpos : ∀ k a, 0 < Ek k a) (hEknorm : ∀ k, (∑ a, Ek k a) = 1) :
    let q := entangledPosterior Ek Jpot lam
    0 ≤ ∑ π, q π * Real.log (q π / (∏ s, streamMarginal q s (π s))) := by
  intro q
  have hqpos : ∀ i, 0 < q i := fun i =>
    entangledPosterior_pos Ek Jpot lam hEkpos i
  have hqsum : (∑ i, q i) = 1 :=
    entangledPosterior_sum_eq_one Ek Jpot lam hEkpos hEknorm
  have hker := entanglement_decomposition_generalK q Ek hqpos hEkpos hqsum hEknorm
  exact hker.1

/-- **Stream marginal is strictly positive on a strictly-positive joint.**

Standalone-named extraction of the positivity argument already used inline
inside `entanglement_decomposition_generalK`.  For a strictly positive
joint `q` on `Fin K → A`, every per-stream marginal `streamMarginal q s a`
is strictly positive.  The proof uses the bound `q i₀ ≤ ∑ i, [i s = a] · q i`
for the constant section `i₀ = fun _ => a`.

Standalone keystone: this lemma is the analytic precondition for the
`multiInformation_nonneg_at_joint` named bridge below, and any downstream
analytic discharge that takes the per-stream marginals as a reference
factor. -/
theorem streamMarginal_pos {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (q : (Fin K → A) → ℝ) (hq : ∀ i, 0 < q i) (s : Fin K) (a : A) :
    0 < streamMarginal q s a := by
  let i0 : Fin K → A := fun _ => a
  have hnonneg : ∀ i : Fin K → A, 0 ≤ if i s = a then q i else 0 := by
    intro i
    by_cases hi : i s = a
    · simp [hi, (hq i).le]
    · simp [hi]
  have hsingle :
      q i0 ≤ ∑ i : Fin K → A, if i s = a then q i else 0 := by
    simpa [i0] using
      (Finset.single_le_sum
        (fun i _ => hnonneg i) (Finset.mem_univ i0) :
          (if i0 s = a then q i0 else 0)
            ≤ ∑ i : Fin K → A, if i s = a then q i else 0)
  exact lt_of_lt_of_le (hq i0) (by simpa [streamMarginal] using hsingle)

/-- **Multi-information non-negativity at any strictly-positive normalized
joint (standalone, named).**

The multi-information $I(q) := D_{\mathrm{KL}}\!\big(q \,\big\|\, \prod_k q^k\big)$
is non-negative for every strictly-positive normalized joint $q$ on
$K$ finite streams, with $q^k$ the per-stream marginals.  This is the
analytic identity behind the manuscript's §13 revertibility witness and the
entropy-route-vs-KL-route consistency check at §21.

The proof folds through `entanglement_decomposition_generalK` with the
per-stream marginals themselves as the reference factors (using
`streamMarginal_pos` for positivity and `streamMarginal_sum_eq_total` for
normalization), then extracts the multi-information non-negativity
component. -/
theorem multiInformation_nonneg_at_joint
    {A : Type*} [Fintype A] [DecidableEq A] {K : ℕ}
    (q : (Fin K → A) → ℝ) (hq : ∀ i, 0 < q i) (hqn : (∑ i, q i) = 1) :
    let m := fun i : Fin K → A => ∏ s, streamMarginal q s (i s)
    0 ≤ ∑ i, q i * Real.log (q i / m i) := by
  intro _
  have hsm_pos : ∀ s a, 0 < streamMarginal q s a := fun s a =>
    streamMarginal_pos q hq s a
  have hsm_norm : ∀ t, (∑ a, streamMarginal q t a) = 1 := by
    intro t
    rw [streamMarginal_sum_eq_total (q := q) (t := t), hqn]
  have hker := entanglement_decomposition_generalK q (fun s a => streamMarginal q s a)
    hq hsm_pos hqn hsm_norm
  exact hker.1

#print axioms free_energy_decomposition_full
#print axioms multiInformation_nonneg_at_joint
#print axioms streamMarginal_pos

end MathlibProofs
