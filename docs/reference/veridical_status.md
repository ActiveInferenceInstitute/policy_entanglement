# Veridical Status & Provenance

*Latest generated audit.* Live Lean, test, bibliography, rendered
manuscript, figure, and PDF status come from
`output/reports/release_readiness.json`,
`output/reports/test_results.json`, `output/MANIFEST.md`, and the
generated theorem map. Historical round deltas remain documented below
only where the table explicitly describes a prior audit or revision
checkpoint.

This page is the **reviewer audit map** for what is *actually*
working in the project right now — Lean build state, pymdp run
state, manuscript-variable provenance, and the audit chain that
guards against fabricated manuscript values.

It is refreshed by running `scripts/readiness_report.py` after a green
`scripts/run_all.py` gate; the live state below is what an auditor
would reproduce by running the pipeline and then the report writer.

---

## 1 — Lean boundary fragment status

Live count from `lake build` + `scripts/build_lean.py`:

| Metric | Live value | Where it comes from |
|---|---|---|
| Lake jobs | **22 / 22 green** | `cd lean && lake build` |
| Boundary submodules | **17** (`Basic`, `Scalar`, `JointDist`, `Coupling`, `FreeEnergy`, `Geometry`, `Spectral`, `SpectralWitnesses`, `Heterogeneous`, `BernoulliToy`, `Decomposition`, `Constructive`, `Monotonicity`, `Convexity`, `MarkovBlanket`, `ConnectionsWitnesses`, `FloatRealResidualWitness`) | `lean/ActinfPolicyEntanglement/*.lean` |
| `def`s | 39 | comment-stripped declaration scan in `scripts/manuscript_variables.py` |
| `theorem` / `lemma`s | 76 | comment-stripped declaration scan in `scripts/manuscript_variables.py` |
| `structure`s (witness types) | 11 | `BoundedQuadraticTax`, `SmallLambdaTolerance`, `FreeEnergyConvexityWitness`, `LocalConcavityAtZero`, `MarkovBlanketSeparationWitness`, `UpperSemicontinuousRankWitness`, `SparsityRankEnvelope`, `HierarchicalConcentrationWitness`, `SophisticatedInferenceEmbedding`, `PythagoreanWitness`, `FloatRealResidualWitness` |
| Total declarations | 126 (39 + 76 + 11) | derived live by `scripts/manuscript_variables.py` |
| Strict `sorry` | **0** | `scripts/build_lean.py` hygiene gate |
| Axioms beyond stock Lean | **0** | hygiene gate |
| `unsafe` / `partial` / `noncomputable` | **0** | hygiene gate |
| Mathlib imports | **0** | hygiene gate |

### Honest substantive/typed-API split (round-4 transparency upgrade)

The headline "76 theorems / lemmas" count above is the literal number
of `theorem` / `lemma` keywords the Lean kernel checks. Every one of
those declarations type-checks under stock Lean v4.29.0, but **they
do not all carry the same mathematical weight**. The honest split:

| Category | Approx count | What it certifies |
|---|---:|---|
| **Substantive algebraic proofs** | ~15 | Genuine identities discharged via `[CommScalar α]` typeclass + tactic chains. Examples: `Scalar.affine_diff`, `Scalar.mul_sub`, `Coupling.couplingLogWeight_affine_in_lam`, `Decomposition.entanglement_decomposition_four_terms_commute_skeleton` (commutative-ring re-grouping of the four-term decomposition; new in round 4), `Decomposition.couplingVerdict_correct` (`decide_eq_true_iff` extraction), `Spectral.Bipartite.schmidtRankOne_iff_isBipartiteMeanField` (new in round 4). Would not type-check if false. |
| **Definitional unfoldings via `rfl`** | ~10 | True by construction; useful to lock definitions to their unfolded shapes. Examples: `Geometry.mfImage_isMeanField`, `Geometry.mProjection_kl_eq_self_when_meanfield`, `FreeEnergy.totalCorrelation_def` (round-4 honest replacement of the prior `kl q q s ≡ 0` placeholder), `BernoulliToy.isingFreeEnergyCurve_total`, `Spectral.isBipartiteMeanField_iff_factors`. |
| **Witness-form typed-API contracts** | 11 | The analytic identity is supplied by the caller as a `structure` field; the boundary fragment extracts and re-publishes it. Genuinely *non-vacuous* because each witness's tie-in fields commit `Iq`, `siValue x`, `cut_rank k λ`, etc. to boundary-fragment primitives rather than free Floats. **These are not stand-alone proofs of the underlying mathematical claims**; they are typed contracts scoped for separate Mathlib4 analytic discharge. |
| **`Monotonicity` / `Constructive` Lean-core wrappers** | ~21 | Renamed re-exports of `Nat.le_refl`, `Nat.zero_le`, etc., plus simple `List` inductions. Useful for naming consistency; not framework content. |

> **Statement-faithfulness note (registry `status: proved` ≠ "proves the
> named manuscript proposition").** `status: proved` in
> `manuscript/refs/labels.yaml` means *machine-checked in stock Lean
> without analytic witness assumptions* — it does **not** assert that the
> Lean statement is the full manuscript proposition it is mapped to.
> Of the 5 `proved` rows, only **2 are `substantive`** (`cor_4_2`,
> `cor_4_3` — genuine machine-checked proofs of their named corollary);
> the other **3 are `statement-restricted`** — the Lean statement is
> strictly weaker than its manuscript name:
> - **`prop_6_1` `Geometry.mfImage_isMeanField`** (Prop 7.1 "MF
>   submanifold is e-flat") proves `IsMeanField (mfToJoint m)` —
>   definitional membership of the mean-field image. It does **not**
>   establish e-flatness (closure under e-geodesics / affine-in-θ); that
>   is real-analytic content scoped to the separate Mathlib4 layer and
>   is intentionally out of the `Float`/Mathlib-free boundary fragment.
> - **`prop_6_2` `Geometry.mProjection_kl_eq_self_when_meanfield`** (Prop 7.2
>   "m-projection minimises KL") proves `kl q (mfToJoint m) = kl q q`
>   *under the hypothesis* `q = mfToJoint m`. It does **not** establish
>   the information-projection minimality `∀ p ∈ M_MF,
>   D_KL(q‖m̂(q)) ≤ D_KL(q‖p)`; that inequality is the analytic target
>   for the Mathlib4 layer (or a future witness-form theorem).
> - **`prop_7_1` `Spectral.Bipartite.isBipartiteMeanField_factors`**
>   (Prop 8.1 "Bipartite mean-field factorization") forwards through
>   `isBipartiteMeanField_iff_factors := Iff.rfl` — a definitional
>   unfolding of the bipartite-mean-field *predicate* into its
>   factorization form. It does **not** establish the named
>   Schmidt-rank equivalence `r(q)=1 ⟺ q ∈ M_MF` (the rank ↔
>   outer-product content), which is the Mathlib `MathlibProofs`
>   target. (Initially mis-tagged `definitional` in this pass; an
>   internal RedTeam audit flagged that as the same uneven-honesty
>   softening this ledger exists to prevent, and it was corrected to
>   `statement-restricted` — the same class as `prop_6_1`/`prop_6_2`.)
>
> These are honest `rfl`/forwarder facts, not over-claims, but a reader
> must not read any of these three `proved` rows as a machine-checked
> proof of its manuscript-level proposition.
>
> **Now structurally enforced (no longer prose-only).** The two Lean
> theorems have been **renamed to state exactly what they prove**:
> `mfSubmanifold_eFlat → mfImage_isMeanField` and
> `mProjection_minimises_kl → mProjection_kl_eq_self_when_meanfield`
> (registry `lean_name`, S05/3B `[[LEAN:…]]` tokens, and all
> cross-reference docs updated atomically; the four-track wiring gate
> `validate_lean_wiring` enforces registry↔Lean name consistency).
> Every `status: proved` row now also carries a machine-checked
> **`faithfulness:`** field in `manuscript/refs/labels.yaml`, one of
> `substantive` | `definitional` | `statement-restricted`:
> `cor_4_2`, `cor_4_3` = `substantive`; `prop_6_1`, `prop_6_2`,
> `prop_7_1` = `statement-restricted` (no row is `definitional` — the
> initially-softened `prop_7_1` tag was RedTeam-corrected as noted
> above). `scripts/manuscript_variables.py` **raises**
> if any `proved` row omits or mis-values `faithfulness`, derives the
> abstract/Part III headline counts
> (`theorem_proved_{substantive,definitional,restricted}_count`) from
> this field, and `tests/test_h1_headline_invariant.py` **pins these
> specific rows** (`cor_4_2`/`cor_4_3`=substantive,
> `prop_6_1`/`prop_6_2`/`prop_7_1`=statement-restricted) so a future
> relabel cannot silently re-inflate the count, and fails if any
> reader-facing surface states the bare proved-count without the
> statement-faithfulness split. The headline can no longer silently
> re-inflate the `proved` count: "done" is defined as *the plain
> reading is true*, repo-wide, enforced.
>
> **Analytic-kernel external machine-check (2026-05-18, verified).** The
> Kullback–Leibler **non-negativity** kernel that the `prop_6_2`
> minimality direction and the `prop_6_5` Pythagorean-residual term rest
> on is now machine-checked in Mathlib as
> `MathlibProofs.klReal_nonneg` (Gibbs' inequality for strictly-positive
> finite distributions with `∑ q = ∑ p = 1`, proved from
> `Real.log_le_sub_one_of_pos`; `lake build` green, `0` `sorry`/`axiom`,
> olean produced), with `MathlibProofs.klReal_self_eq_zero` the equality
> companion. The strictly-positive hypothesis is *faithful* — it is
> exactly the project's S06 ambient manifold `M` (simplex of
> strictly-positive joints), not a weakening. **Precisely scoped (this is
> NOT a promotion):**
> - It discharges only the *KL≥0* fact (the textbook-easy half). It does
>   **not** prove the **Pythagorean identity**
>   `D(q‖p) = D(q‖m̂q) + D(m̂q‖p)` — the substantive content of
>   `prop_6_2`'s minimality — which remains the open analytic target.
> - It is an **ℝ idealization**: `klReal` is `(ι→ℝ)`-valued and is **not
>   formally bridged** to the boundary's `Float`-valued `kl`
>   (`Float ≠ ℝ`; a rigorous Float↔ℝ bridge is not built).
> - Therefore `prop_6_2`/`prop_6_5` **remain witness-form**, registry
>   `status:` is **unchanged**, and no manuscript count moves. The only
>   change is epistemic: the KL≥0 assumption is now *externally
>   machine-checked as a true ℝ statement* rather than merely assumed —
>   a strict honesty increment, audited by RedTeam to avoid the
>   lemma-as-theorem overclaim.
> - **Update (2026-05-18, verified): the minimality *implication* is now
>   machine-checked too.** `MathlibProofs.klReal_minimises_of_pythagorean`
>   proves, in Mathlib (`lake build` green, 0 `sorry`/`axiom`), that
>   *given* the Pythagorean identity `D(q‖p)=D(q‖m̂q)+D(m̂q‖p)` and
>   strictly-positive normalized `m̂q,p`, the minimality
>   `D(q‖m̂q) ≤ D(q‖p)` follows (the `D(m̂q‖p)≥0` half discharged by
>   `klReal_nonneg`). So `prop_6_2`'s logical structure is now
>   *[open analytic identity] ⟹ [Lean-PROVEN minimality]* — previously
>   **both** halves were assumed; now only the identity is open. That
>   identity is independently **numerically corroborated** to floating
>   tolerance by `tests/test_geometry.py::`
>   `test_pythagorean_identity_mirrors_lean_klReal_minimises_of_pythagorean`
>   (`pythagorean_residual ≈ 0`, analytic-pin KL value matched).
> - Net remaining to *fully* discharge `prop_6_2` end-to-end in Lean:
>   (i) the Pythagorean/marginal-matching **identity** over a product
>   `p` and `m̂q = ⊗ₛ(marginal q)ₛ` (reduction:
>   `D(q‖p)−D(q‖m̂q) = Σₛ D(qₛ‖pₛ) = D(m̂q‖p)`), and (ii) a Float↔ℝ
>   bridge. Statuses remain **unchanged**; rows remain witness-form; no
>   manuscript count moves — this is an epistemic strengthening only.
> - **Update (2026-05-18, verified — Pythagorean obligation *isolated*,
>   not reduced-in-strength, not closed).**
>   `MathlibProofs.klReal_split_via_intermediate` proves, **in full
>   generality and with no hypothesis assuming the conclusion** (`lake
>   build` green, 8249 jobs, 0 `sorry`/`axiom`, olean 249 KB), the
>   algebraic half by pure `Real.log` additivity:
>   `D(q‖p) = D(q‖m) + ∑ᵢ qᵢ·log(mᵢ/pᵢ)`.
>   **Honest scope of this contribution (do not overread):** given this
>   now-machine-checked split, the open hypothesis
>   `∑ᵢ qᵢ·log(mᵢ/pᵢ) = ∑ᵢ mᵢ·log(mᵢ/pᵢ)` (call it `hcross`) is
>   *logically equivalent* to the original full Pythagorean identity
>   `hpyth` — assuming `hcross` is **not logically weaker** than assuming
>   `hpyth`. The contribution is **isolation, not logical reduction**:
>   the machine-checked split strips the multi-information term
>   `∑ qᵢ·log(qᵢ/mᵢ)` out of the open obligation, leaving the open
>   analytic content as the *single, elementary* marginal-expectation
>   identity "E_q[log(m/p)] = E_m[log(m/p)]" — a `Fintype`-product
>   reindexing that holds because `m̂q = ⊗ₛ(marginal q)ₛ` and `p`
>   factorizes, so `log(m/p)` depends on coordinates only through
>   marginals. That is a materially **more tractable and crisply-named
>   hand-off** than the opaque three-divergence relation, but it is the
>   *same analytic obligation re-expressed*, not a smaller one.
>   `MathlibProofs.klReal_minimises_of_crossTermMatches` then proves
>   `prop_6_2`'s minimality from `hcross` (no hypothesis assuming the
>   conclusion). **No `status:` flip, rows remain witness-form, no
>   manuscript count moves.** The marginal-matching cross-term and the
>   Float↔ℝ bridge remain the honestly-open hand-off — discharging them
>   unverified would reproduce the lemma-as-theorem failure this ledger
>   exists to prevent.
> - **Update (2026-05-18, verified — cross-term `hcross` DISCHARGED for
>   the K=2 product case).** TOP-LINE BINARY VERDICT (no buried hedge):
>   - **CERTIFIED (machine-checked):** `MathlibProofs.crossTerm_matches_K2`
>     proves `∑ q·log(m/p) = ∑ m·log(m/p)` for the project's load-bearing
>     **K=2 product** structure (`q : α×β→ℝ`, `m = qα⊗qβ` the marginals,
>     `p = pα⊗pβ`), `lake build` green (8249 jobs, 0 `sorry`/`axiom`,
>     olean 348 KB). Hypotheses are *only* marginal-definition, strict
>     positivity, marginal-normalization (`∑qα=∑qβ=1`), and the product
>     *forms* of `m`,`p` — **no hypothesis is or assumes the conclusion**;
>     the proof is the genuine additive-log-split + marginalization
>     reindexing (non-vacuous, audited on disk). Composing with
>     `klReal_split_via_intermediate` + `klReal_minimises_of_crossTermMatches`,
>     `prop_6_2`'s minimality is now end-to-end Lean-checked **for K=2**
>     modulo only the Float↔ℝ idealization (next bullet).
>   - **STILL OPEN (honest, not faked):** the general-K case
>     (`Πₛ αₛ`, needs `Real.log_prod` + induction over the K streams) —
>     a genuine generalization, deliberately *not* asserted here.
>   - **OPEN, NOT IMPOSSIBLE (RedTeam 2026-05-18 F5 — prior wording was
>     itself an overclaim):** the Float↔ℝ bridge. `klReal*`/
>     `crossTerm_matches_K2` are `ℝ`-valued; the boundary fragment
>     computes in `Float`. There is no *exact* order-/field-homomorphism
>     `Float → ℝ` (rounding, non-associativity, `NaN`/overflow), so an
>     *equality* bridge is unsound — but an **error-bounded** bridge
>     (`|fl(x) − x| ≤ ε|x|`, Flocq / interval-arithmetic style) **is a
>     sound formal statement and standard numerical-analysis practice**.
>     It was **not done here (out of scope / real remaining work), NOT
>     impossible**. The earlier "cannot exist as a sound Lean statement"
>     framing overstated the gap (it conflated "no exact homomorphism"
>     with "no sound bridge") and is corrected here. Current honest
>     treatment: the `ℝ` results model the intended exact arithmetic;
>     `Float` execution is covered *empirically* by the numerical-mirror
>     tests; a rigorous error-bounded bridge is genuine open work, not a
>     fabricated lemma and not an impossibility.
>   - **No `status:` flip, rows remain witness-form, no manuscript count
>     moves** — `prop_6_2`/`prop_6_5` stay witness-form (the K=2 chain is
>     an external `ℝ` certificate, not a boundary-fragment proof; general
>     K + the Float idealization remain). Epistemic strengthening only.
> - **Update (2026-05-18, verified — general-K cross-term DISCHARGED via
>   the equal-marginals abstraction).** TOP-LINE BINARY VERDICT:
>   - **CERTIFIED (CONDITIONAL — machine-checked for every K):**
>     `MathlibProofs.crossTerm_matches_of_equal_marginals` proves, for
>     **every K** (homogeneous joints `(Fin K → A) → ℝ`), the *conditional*
>     `[m-projection's two defining properties] ⟹ cross-term
>     ∑ q·log(m/p) = ∑ m·log(m/p)`, and `klReal_minimises_generalK`
>     composes it with the general split + Gibbs into the conditional
>     general-K minimality `D(q‖m) ≤ D(q‖p)`. `lake build` green (8249
>     jobs, 0 `sorry`/`axiom`, clean — no linter warnings). The two
>     antecedents, audited verbatim on disk: `hmarg` (`∀ s j,
>     streamMarginal q s j = streamMarginal m s j` — full marginal-
>     *distribution* equality over every stream; this **is** genuinely
>     the m-projection's m-flat defining property) and `hsep`
>     (`∀ i, Real.log (m i / p i) = ∑ s, g s (i s)` for a *free*
>     parameter `g` — the *residual* `log(m/p)`, not the model `log p`,
>     is additively separable). **Honest scoping correction (RedTeam
>     2026-05-18 F4):** `hsep` is **NOT** "the e-flat property" and the
>     pair is **not** "the m-projection's *defining* characterization" —
>     because `g` is existentially free, `hsep` is the strictly *weaker*
>     statement "some single-coordinate decomposition exists", which the
>     e-flat / `p`-factorizes property *implies* but is not equal to, and
>     which is **trivially satisfiable at K=1** (`g` absorbs the whole
>     residual). The earlier "defining property / e-flat" wording
>     overstated the antecedent; corrected here. **Non-vacuity still
>     proven, not asserted:** neither antecedent alone yields the
>     conclusion; `hsep` is load-bearing (negative control: deleting its
>     `rw` use → `build failed`); neither is or assumes the cross-term
>     equality; the proof does genuine marginalization-reindexing work
>     (EN-LEAN-1: "genuine mathematics, not dressed-up triviality"). The
>     honest content of the reframe: the cross-term follows from
>     marginal-matching + *some* additive decomposition — **not** from
>     the explicit "m = ∏ₛ qₛ" form; whether the concrete model supplies
>     that decomposition is the open residual below.
>   - **NOT claimed:** an *unconditional* general-K result. A green build
>     certifies the conditional only — it does **not** establish that the
>     concrete Ising/Bernoulli m-projection *satisfies* `hmarg`/`hsep` for
>     general K. That instantiation is the distinct residual below; a
>     reader must not infer an unconditional general-K theorem.
>   - **RESIDUAL — corrected characterization (RedTeam 2026-05-18 F7,
>     PT-LEAN-2; the prior "elementary" wording was itself laundering):**
>     (i-a) `hmarg` for the explicit `m = ∏ₛ qₛ`: the
>     product-marginalization identity `streamMarginal (∏ₜ qₜ) s = qₛ`.
>     **This is NOT "elementary".** It is the *same general-K
>     product-marginalization combinatorial core* (`Finset.prod` over
>     `Fintype.piFinset` + per-stream normalization `∑ qₜ = 1` for every
>     `t ≠ s` + induction over `Fin K`) that this very ledger called
>     "the honest open generalization, not faked here" *one round
>     earlier* (the v0.4 "still genuinely open" line). The equal-marginals
>     abstraction **relocated this core into the `hmarg` antecedent — it
>     did not eliminate it**. It is **0 lines proved**, and strictly
>     *harder* than the ~67-line K=2 case (`crossTerm_matches_K2`), which
>     handled only two fixed factors. (i-b) `hsep` for the explicit
>     product reference (`Real.log_prod`) is genuinely the trivial half.
>     The honest status: the conditional theorem is real and the IG
>     abstraction is correct, **but the load-bearing deferred analytic
>     content is unproven and re-hosted, not closed** — saying
>     "`hmarg`/`hsep` are its definition, not a hidden gap" understated a
>     0-lines-proved obligation and is retracted. The 4×-prior deferrals
>     may have been *correctly conservative*; this round produced an
>     honest skeleton, not a discharge of the hard part.
>     (ii) heterogeneous per-stream state spaces
>     (dependent `∀ s, αₛ`) — same proof structure, instances differ;
>     (iii) the Float↔ℝ idealization — unchanged, still a characterized
>     idealization gap, never a fabricated bridge lemma.
>   - **No `status:` flip, rows remain witness-form, no manuscript count
>     moves.** Boundary fragment re-verified `0 sorries/0 axioms/0 Mathlib
>     imports`; K=2 theorem still builds; pinning tests `6 passed`.
>     Epistemic strengthening only.

**What this means in practice.** The framework's *mathematical
content* (Theorem 5.1 and its corollaries, the K=2 closed form, the
e-geodesic identity, the coupling-tax bound, …) is verified by:

* **Manuscript prose** — line-by-line algebra in appendix S01 for
  Theorem 5.1; full derivation in S03 for the K=2 closed form.
* **Python numerical witnesses** — `src/lean/decomposition.py`,
  `src/lean/free_energy.py` (with the round-4 `total_correlation_lean_companion`
  parity function), the entanglement_decomposition_rhs ↔
  free_energy_against_entangled_prior equality at 30+ random points,
  residual `< 1e-9`.
* **Dashboard invariants** — 47/47 passing at worst-case residual
  `5.55e-16` (`decomposition_lhs_eq_rhs_max_residual`).

The Lean fragment contributes:

* **A typed API skeleton** that constrains Mathlib4-based
  proofs to a specific decomposition shape and parameter-threading
  discipline.
* **Genuine algebraic identities** (commutative-ring four-term
  re-grouping, affine-in-λ identity, bipartite Schmidt-rank-1 ↔
  mean-field iff, mean-field-collapse identity for the four-term
  decomposition, …) that **are** machine-checked.
* **Hygiene certificates** (`0 sorry / 0 axiom / 0 Mathlib`) that the
  build CI re-validates on every commit.

**Theorem 5.1's analytic content is now machine-checked in ℝ
(2026-05-18, verified on disk).** The prior status of this paragraph —
"not currently machine-checked, ~8–10 weeks of Mathlib work" — is
**superseded and was retained here only as the honest pre-discharge
record**.  *(2026-05-19: superseded further — the FULL S01 boxed
identity is now machine-checked in ℝ by
`MathlibProofs.free_energy_decomposition_full`, foundational-only,
enforced by `scripts/build_mathlib_proofs.py`; its first delivery was a
`sorryAx` fake caught by the axiom-gate + coherence audit and reverted,
the genuine third state independently negative-controlled. Sole
residual: Float↔ℝ. See `methods_and_assumptions.md` + CHANGELOG.)*
`MathlibProofs.entanglement_decomposition_generalK` (the kernel the
full identity composes) proves,
for **general `K`** and a **general entangled joint `q`** (only strict
positivity + normalization assumed; `q` is *never* assumed to
factorize), all three pieces of Theorem 5.1's analytic content against
the product reference `p` and the m-projection
`m := ∏ₛ streamMarginal q s`:
(1) the multi-information is non-negative, `0 ≤ D(q‖m)` (Gibbs);
(2) the KL chain-rule decomposition `D(q‖p) = D(q‖m) + Σᵢ qᵢ·log(mᵢ/pᵢ)`;
(3) m-projection minimality `D(q‖m) ≤ D(q‖p)`.
`lake build` green (8249 jobs); `#print axioms` →
`[propext, Classical.choice, Quot.sound]` only (the three standard
foundational axioms — **no `sorryAx`, no project axiom, no
`native_decide`**); `0 sorry/admit/axiom/native_decide` in the file.
The previously-deferred core — the product-marginalization identity
`streamMarginal (∏ₜ factorₜ) s = factorₛ` (deferred ~5× as
"research-grade") — is discharged unconditionally as
`MathlibProofs.streamMarginal_productDist` and is **non-vacuous**:
an independent negative control (forcing the `hmarg` step to
reflexivity, i.e. the degenerate `m := q` shortcut) makes the build
**fail** with a type mismatch, proving `m ≠ q` and that the
marginalization lemma is genuinely load-bearing — this is *not* the
relocated-into-an-antecedent pattern that earlier rounds were
correctly criticized for.

**The one honest residual** is the Float↔ℝ bridge: the `ℝ`-valued
`MathlibProofs` layer certifies the *exact-arithmetic* mathematics; the
`Float`-valued boundary fragment (`Decomposition.entanglement_decomposition`,
still a typed `hWitness ↦ hWitness` contract) is its computational
shadow, corroborated *numerically* (dashboard invariant
`decomposition_lhs_eq_rhs_max_residual`, worst-case `5.55e-16`). A
*verified* error-bounded `Float → ℝ` bridge is genuine, sound, standard
numerical-analysis work that is **not built here** — it is the single
scoped residual, not a defect, and not an impossibility. (Virtually all
formalized analysis lives in `ℝ`/`ℚ`; the `ℝ` proof is the faithful
model of the intended exact arithmetic, audited not to be a weakening —
the strict-positivity hypothesis *is* the project's S06 ambient
strictly-positive simplex `M`.)

### Round-5 honesty + infrastructure upgrades (2026-05-12 followup)

| Issue identified | Fix applied | Verification |
|---|---|---|
| `Geometry.dualFlat_pythagorean_witness` was the literal `id` function `(hWitness : klVal = tcVal + residual) → klVal = tcVal + residual` — three *free* `Float` parameters with no tie-in to boundary primitives.  A caller could satisfy the contract with arbitrary numbers that happened to add. | New `PythagoreanWitness {K Pol} (q q0_star : JointDist K Pol) (mhat : MFDist K Pol) (s : List (PolicySpace K Pol)) (sumStreamEntropies : Float)` structure with **three tie-in equality fields** committing `klVal := kl q q0_star s`, `tcVal := totalCorrelation q s sumStreamEntropies`, `residual := kl (mfToJoint mhat) q0_star s` plus the analytic `pythagorean` field.  Also adds the derived `dualFlat_pythagorean_boundary_identity` theorem that re-publishes the identity at the level of boundary primitives. | `lake build` green (21/21 jobs); `scripts/build_lean.py` reports 0 sorries / 0 axioms / 0 unsafe.  Theorem count: 67 → 68; structure count: 9 → 10. |
| Pipeline `scripts/run_all.py` ran the empirical producer batch (`dump_archetypes`, `parameter_sweep`, `simulate_pymdp`, `simulate_multi_k`, `simulate_long_horizon`, `simulate_revertibility`) serially despite write-isolation; ~109 s of redundant sequential overhead. | Round-5 P1-1: `concurrent.futures.ThreadPoolExecutor` batches the six parallel-eligible producer stages with stdout/stderr captured and emitted serially in completion order.  Defaults to parallel; `--serial` falls back to legacy. | Verified on a 2-stage subset (`dump_archetypes` + `parameter_sweep`): 0.3 s wall-clock vs ~0.6 s serial.  Full-pipeline reduction expected to scale with the slowest stage in the batch (`simulate_pymdp`). |
| Silent regressions possible: a developer could delete tests, narrow coverage below the published floor, or weaken a Lean theorem and the pipeline would still report "green". | Round-5 P0-3: new `scripts/regression_gate.py` compares the current run against `scripts/regression_baseline.json` and fails on any drop in test count (> 2), coverage (> 1 pp), invariant count, or Lean budget (sorry / axiom / unsafe).  `--update-baseline` refreshes the committed JSON at release time. | Gate validated against current run: all 8 sub-checks pass. |
| No authoritative inventory of pipeline outputs; orphan files in `output/` were silent. | Round-5 P2-2: `scripts/run_all.py` writes `output/MANIFEST.md` at the end of every run — per-stage timings + complete artifact table with sizes. | Verified on a 1-stage run; manifest path printed at end. |
| Long-horizon convergence logic (`tail_window_kl`) was inline inside `long_horizon_rollout` and tested only at a short synthetic horizon; the configured `LONG_HORIZON_STEPS` numerical witness for habit accumulation was untested. | Round-5 P1-3: `tail_window_kl` extracted into a pure-numpy helper (no pymdp); new `tests/test_tail_window_kl.py` parameterizes convergence across multiple synthetic horizons. Round-trip regression test added to `tests/test_long_horizon.py` (pymdp branch). | All 11 new tests pass. |
| Every static test used *symmetric* K=2 Ising ensembles; asymmetric `\|Π^k\|` was never exercised. | Round-5 P1-4: new `tests/test_heterogeneous_ensemble.py` exercises K=2 with `\|Π^0\| = 2`, `\|Π^1\| = 3` and the reverse `(3, 2)` shape; verifies joint shape, mean-field collapse at λ = 0, monotone TC growth, and determinism. | All 5 new tests pass. |
| `manuscript/2D_decomposition.md` mentioned Theorem 5.1's "live Lean companion" in a single parenthetical; the `boundary` (not `proved`) status was easy to miss. | Round-5 P0-2: explicit honesty-note block-quote added immediately after the [[LEAN:thm_4_1]] inline directive, linking to this `veridical_status.md`'s substantive / typed-API split. | Manuscript diff. |
| `manuscript/refs/citations.yaml` was missing the foundational works for *multi-information* (McGill 1954) and *information geometry* (Amari 1985), both of which appear prominently in §2D and §2F. | Round-5 P1-5: added `mcgill-1954` and `amari-1985` entries; cited in §2B's notation block (`I(p) = … (multi-information [@mcgill-1954])`) and §2F's opening sentence (`[@amari-1985; @amari-nagaoka-2000; @amari-2016]`). | Manuscript diff. |
| `manuscript/S05_lean_code_skeleton.md` lines 173 / 177 mis-labeled "Proposition 8.1" / "Proposition 8.2" for Geometry-fragment theorems that are actually Propositions 7.1 / 7.2. | Round-5 P2-4 cosmetic: numbering corrected to 7.1 / 7.2. | Manuscript diff. |
| Public predicates `is_planning_stream`, `is_reflexive_stream`, `is_purely_reflexive`, `is_purely_planning`, `is_heterogeneous` in `src/lean/heterogeneous.py` lacked docstrings. | Round-5 P2-5: full docstrings added (semantics, manuscript section references, runnable example). | Source diff. |
| New `docs/CONCEPTS.md` page absent: newcomer reading-order jump from FAQ → 140-page combined PDF was a cliff. | Round-5 P2-4: added `docs/CONCEPTS.md` (three-minute, zero-jargon capsule on the K=2 binary toy + the three theorem families) and linked from `docs/READING_ORDER.md`. | Docs diff. |

### Round-4 round-trip honesty upgrades

| Issue identified | Fix applied | Verification |
|---|---|---|
| `FreeEnergy.totalCorrelation := kl q q s` evaluated to identically 0 (Python `total_correlation` returned the real `Σ_k H(qᵏ) − H(q)`, so Python ↔ Lean were silently divergent). | New 3-arg `totalCorrelation q s sumStreamEntropies := sumStreamEntropies − shannonEntropy q s`, plus `total_correlation_lean_companion` mirror in Python. | `tests/test_free_energy.py::test_total_correlation_lean_companion_*` — three new tests verify parity at 10 random points, mean-field anchor, and antidiagonal-joint strict positivity. |
| `ConnectionsWitnesses.sophisticatedInference_embedding_witness` had `preserveVFE : F = F` (rfl-discharged X=X — vacuous). | Added `siValue : source → Float` field; `preserveVFE : siValue x = variationalFreeEnergy (embed x) ...` now binds the sophisticated-inference value scalar to the entangled VFE. | `lake build` green; theorem no longer satisfiable by `rfl` alone. |
| `Spectral.Bipartite.isBipartiteMeanField_factors` and `factors_isBipartiteMeanField` were both `id` of a definitional unfolding. | Replaced with `isBipartiteMeanField_iff_factors` (genuine iff statement) + the two id-theorems as `mp`/`mpr` forwarders; added `schmidtRankOne_iff_isBipartiteMeanField` discharging the bipartite K=2 case of Proposition 8.1 on the boundary fragment. | `lake build` green; Schmidt-rank-1 is now anchored to a real iff theorem. |
| Headline counts conflated typed-API contracts with substantive proofs. | This new "Honest substantive/typed-API split" section + a `Lean content honesty` block in README. | This document. |
| Phase-4 sketch in §3B used `− totalCorrelation q` while body of §2D used `+ I(q)`. | Sign aligned in §3B Phase-4 block (annotated as "rendered with the manuscript's plus-`I` convention"). | Manuscript diff. |
| Stale test counts in README and docs. | Replaced volatile hand-maintained counts with live-report pointers; conditional-skip wording clarified. | `uv run pytest tests/ --cov=src --cov-fail-under=95` is summarized by `output/reports/test_results.json`. |

Per-theorem boundary status (from `manuscript/refs/labels.yaml`):

* `proved` — fully discharged within the boundary fragment.
* `boundary` — type-checked statement; analytic content discharged
  via a witness argument the caller supplies.
* `forwarder` — proved by forwarding to a load-bearing lemma.
* `witness` — a typed witness contract: the Lean declaration is live,
  the boundary-fragment tie-ins are checked, and the remaining
  analytic payload is supplied by the caller until a Mathlib4 discharge
  layer constructs it internally.

The older `sketch` and `deferred` registry statuses are retired. They
may appear only in revision-history prose describing earlier rounds;
they are not legal current statuses, and
`tests/test_veridical_status_doc.py` now rejects them in the registry
or this table.

| Label | Number | Lean module . name | Status |
|---|---|---|---|
| `thm_4_1` | Theorem 5.1 | `Decomposition.entanglement_decomposition` | boundary |
| `cor_4_2` | Corollary 5.2 | `Decomposition.couplingVerdict_correct` | proved |
| `cor_4_3` | Corollary 5.3 | `Decomposition.couplingLogWeight_pointwise_at_zero` | proved |
| `cor_4_4` | Corollary 5.4 | `Decomposition.totalCorrelation_def_unfold` | boundary |
| `thm_4_2` | Theorem 5.5 | `Decomposition.freeEnergy_closedForm_witness` | boundary |
| `thm_4_3` | Theorem 5.6 | `Convexity.freeEnergy_convex_in_lam_witness` | witness |
| `prop_6_1` | Proposition 7.1 | `Geometry.mfImage_isMeanField` | proved |
| `prop_6_2` | Proposition 7.2 | `Geometry.mProjection_kl_eq_self_when_meanfield` | proved |
| `prop_6_3` | Proposition 7.3 | `FreeEnergy.totalCorrelation_eq_kl_to_mprojection` | witness |
| `thm_6_4` | Theorem 7.4 | `Geometry.entangledFamily_eGeodesic` | forwarder |
| `prop_6_5` | Proposition 7.5 | `Geometry.dualFlat_pythagorean_witness` | witness |
| `prop_7_1` | Proposition 8.1 | `Spectral.Bipartite.isBipartiteMeanField_factors` | proved |
| `prop_7_2` | Proposition 8.2 | `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness` | witness |
| `thm_7_3` | Theorem 8.3 | `SpectralWitnesses.sparsityRank_tradeoff_witness` | witness |
| `thm_8_1` | Theorem 9.1 | `Heterogeneous.couplingTax_quadratic_bound` | witness |
| `cor_8_2` | Corollary 9.2 | `Heterogeneous.couplingTax_small_lambda_tolerance` | witness |
| `prop_10_1` | Proposition 11.1 | `Convexity.freeEnergy_localConcavity_at_zero_witness` | witness |
| `thm_11_1` | Theorem 17.1 | `ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness` | witness |
| `prop_11_2` | Proposition 17.2 | `ConnectionsWitnesses.sophisticatedInference_embedding_witness` | witness |
| `prop_11_3` | Proposition 19.3 | `MarkovBlanket.markovBlanket_separation_identity_witness` | witness |
| `roadmap_float_real_residual` | Roadmap 99.0 | `FloatRealResidualWitness.floatRealResidual_witness` | roadmap |

**All twenty-one registry rows** now have a live Lean companion (or roadmap witness shell) and resolve via
`[[LEAN:label]]` in the manuscript renderer; the renderer extracts
the actual source line-by-line at render time. **Zero theorems remain
`deferred`** after round 3 (down from 7 originally → 4 after round 2
→ 0 after round 3).

### Round-3 witness graduations

| Registry | Manuscript | Boundary witness (NEW round 3) |
|---|---|---|
| `prop_7_2` | Proposition 8.2 — Schmidt rank upper-semicontinuous in λ | `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness` (+ `UpperSemicontinuousRankWitness` structure) |
| `thm_7_3` | Theorem 8.3 — Sparsity-rank tradeoff | `SpectralWitnesses.sparsityRank_tradeoff_witness` (+ `SparsityRankEnvelope` structure) |
| `thm_11_1` | Theorem 17.1 — Hierarchical AIF as λ → ∞ limit | `ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness` (+ `HierarchicalConcentrationWitness` structure) |
| `prop_11_2` | Proposition 17.2 — Sophisticated inference embedding | `ConnectionsWitnesses.sophisticatedInference_embedding_witness` (+ `SophisticatedInferenceEmbedding` structure) |
| `cor_4_2` | Corollary 5.2 — Coupling-pays-for-itself | `Decomposition.couplingVerdict_correct` (boundary identity `couplingVerdict gain tax = true ↔ tax < gain`; status `sketch` → `proved`) |
| `prop_6_1` | Proposition 7.1 — MF submanifold is e-flat | `Geometry.mfImage_isMeanField` (existing constructive proof; label-only `sketch` → `proved` correction) |

### Round-2 witness graduations

| Registry | Manuscript | Boundary witness (round 2) |
|---|---|---|
| `thm_4_3` | Theorem 5.6 — Convexity of F in λ | `Convexity.freeEnergy_convex_in_lam_witness` (+ `FreeEnergyConvexityWitness` structure) |
| `prop_10_1` | Proposition 11.1 — Local concavity of F at λ=0 | `Convexity.freeEnergy_localConcavity_at_zero_witness` (+ `LocalConcavityAtZero` structure) |
| `prop_11_3` | Proposition 19.3 — Markov-blanket separation `sep = 1 − I(q)/H(q)` | `MarkovBlanket.markovBlanket_separation_identity_witness` (+ `MarkovBlanketSeparationWitness` structure) |

---

## 2 — pymdp run state

Live, from `output/logs/pymdp_runs.jsonl` after the most recent
`scripts/run_all.py` invocation:

| Metric | Live value | Source |
|---|---|---|
| pymdp version | **1.0.1** (`inferactively-pymdp`) | `import importlib.metadata; im.version('inferactively-pymdp')` |
| JAX backend version | live (e.g. `0.9.x`) | `im.version('jax')` |
| Inference algorithm | `fpi` (deterministic fixed-point iteration) | `simulation.agents.build_pymdp_agent(inference_algo='fpi')` |
| Static λ-sweep | **21 grid points** on `[0, 4]` | `simulation.hyperparameters.PYMDP_SWEEP_LAMBDAS` |
| Rollout horizon | **10 steps** | `simulation.hyperparameters.PYMDP_ROLLOUT_STEPS` |
| Rollout seed | **0** | `simulation.hyperparameters.PYMDP_ROLLOUT_SEED` |
| JSONL records per pipeline run | ≥ 5 (1 main_start + 3 sectioned timed records + 1 main_end) | `output/logs/pymdp_runs.jsonl` |
| Sections covered | `figure_pymdp_lambda_sweep`, `figure_pymdp_rollout`, `figure_pymdp_free_energies` | `validate_outputs.py::validate_run_log` |

### Per-section runtime characteristics (typical, on macOS Apple-silicon)

| Section | Typical runtime | What it does |
|---|---|---|
| `figure_pymdp_lambda_sweep` | ~ 2.5–3.5 s | 21 × `Agent.infer_states + infer_policies`, lambda_sweep CSV, 3 PNG snapshots |
| `figure_pymdp_rollout` | ~ 1.8–2.5 s | 10 × per-stream pymdp inference + analytical coupling + action sample |
| `figure_pymdp_free_energies` | ~ 10–11 s | 21 × full `free_energy_bundle` (per-stream EFE, VFE, TC, action distribution) + 5 PNGs + free-energy bundle CSV |

Records below the second-mark (e.g. < 100 ms) would indicate the
pymdp call was stubbed out or the JAX kernel was not actually
exercised; the validator's run-log gate
(`scripts/validate_outputs.py::validate_run_log`) does not check
this directly, but the multi-second runtimes above are what the
auditor should expect.

---

## 3 — Manuscript-variable provenance chain

Every numeric value in manuscript prose flows through a single,
auditable chain:

```
src/simulation/hyperparameters.py            (constants)
                ↓
output/data + output/simulations sidecars    (empirical summaries)
                ↓
scripts/manuscript_variables.py              (analytical + pymdp computations)
                ↓
output/data/manuscript_variables.json        (mirrored values)
                ↓
[[VAR:key]] tokens in manuscript/*.md        (renderer substitutes)
                ↓
output/manuscript/*.md                       (rendered prose with values)
                ↓
scripts/validate_manuscript.py               (range gate; CI fail on violation)
```

**Audit point counts** (live):

| Audit check | Live count |
|---|---|
| Distinct real `[[VAR:key]]` tokens used in the manuscript tree | 131 (plus the instructional placeholder `[[VAR:key]]`) |
| Keys present in `manuscript_variables.json` | 207 |
| Unresolved real keys | 0 |
| Display-string helper values | 9 formatted sentinel/list helpers; manuscript-facing numeric claims remain ints, floats, numeric lists, or bool flags |
| Range-gated keys (`validate_outputs.py::REQUIRED_VARIABLES`) | 11 numeric scalars |
| Range-gated keys (`tests/test_manuscript_variables_pipeline.py`) | 21 |
| Closed-form vs empirical MI agreement | ≤ $10^{-6}$ across 121 grid points |

---

## 4 — Three-tier validation summary

The pipeline ships with three independent validation layers, any of
which fails CI:

| Tier | Gate | What it asserts |
|---|---|---|
| **Numerical contracts** (pytest) | live collection count from `output/reports/test_results.json` | shape / type / determinism / λ = 0 baseline / sub-additivity / monotonicity / bundle ↔ helper agreement / equation auto-numbering parity / hyperparameters mirror / notation glossary completeness / pymdp summary statistics / PNG metadata round-trip / hardcoded-literal detector / python-api coverage drift / round-2 + round-3 witness numerical checks (`test_witness_theorems.py`); multi-K / long-horizon / revertibility / 47-dashboard-invariant pin tests |
| **Output gates** (`scripts/validate_outputs.py`) | exit 0 | every PNG header valid; every numeric variable in expected range; closed-form / empirical MI agree to `PARAMETER_SWEEP_AGREEMENT_TOLERANCE`; free-energy bundle λ = 0 baseline (TC = 0, coupling = 0, $H(q) = \sum_k H(q^k)$); TC ≥ 0 everywhere; JSONL run log well-formed with all required sections |
| **Manuscript completeness** (`scripts/validate_manuscript.py`) | exit 0 | every `[[FIG:label]]` / `[[EQ:label]]` / `[[VAR:key]]` / `[@cite]` / `[[SECREF:...]]` / `[[THMREF:...]]` resolves; every numeric variable in expected range; no hardcoded `§N.M` outside permitted sites |

---

## 5 — Reproducing the audit

```bash
# Whole chain — run from project root.
uv run python scripts/run_all.py
# Exits 0 iff every gate above passes.

# Spot checks:
cat output/data/manuscript_variables.json | jq 'keys | length'
jq -c '{section, runtime_ms, status}' output/logs/pymdp_runs.jsonl
ls output/figures/ | wc -l                             # live PNG count
ls output/manuscript/*.md | wc -l                      # live rendered markdown file count
cd lean && lake build                                  # 21 / 21 green (round 3)
```

`scripts/run_all.py`'s exit code is the canonical "veridical status"
green light.

---

## 6 — When a value drifts

If `validate_outputs.py` fails on a numeric range, the chain to walk
in order:

1. `output/data/manuscript_variables.json` — check the *value* the
   computation produced.
2. `output/logs/pymdp_runs.jsonl` — for pymdp-grounded values, check
   the live runtime + observable summary.
3. `scripts/manuscript_variables.py` — confirm the helper that
   produced the value still calls the right `lean.*` /
   `simulation.*` function.
4. `src/simulation/hyperparameters.py` — confirm the sentinel-λ /
   grid the value was computed at hasn't changed.
5. `manuscript/refs/labels.yaml` (`equations:` / `theorems:`) — if a
   cross-reference shifted, check the registry.
6. `tests/test_manuscript_variables_pipeline.py` — adjust the
   range-gate parametrization if and only if the change is
   intentional.

If `lake build` regresses (a `sorry` appears, a Mathlib import
slips in, an `axiom` is added):

1. `scripts/build_lean.py` — reads the offending file:line.
2. Replace the regression with a witness-form theorem (callee
   supplies the analytic witness; boundary fragment certifies the
   decomposition).
3. Update `manuscript/refs/labels.yaml`'s `theorems:` block (status
   field) so the table in §1 above stays accurate.

---

## See also

* [`statistics_reference.md`](statistics_reference.md) — full
  statistical methodology, agreement tolerances, free-energy bundle.
* [`lean_reference.md`](lean_reference.md) — per-theorem Lean-side
  detail.
* [`../guides/styleguide.md`](../guides/styleguide.md) — manuscript ↔ code contract.
* [`../simulation/pomdp_simulation.md`](../simulation/pomdp_simulation.md) — pymdp harness internals.
