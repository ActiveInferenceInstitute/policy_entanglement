import Mathlib
import MathlibProofs.KlReal

namespace MathlibProofs

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

end MathlibProofs
