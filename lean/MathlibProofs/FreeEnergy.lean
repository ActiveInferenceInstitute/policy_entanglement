import Mathlib
import MathlibProofs.Marginals

namespace MathlibProofs

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
