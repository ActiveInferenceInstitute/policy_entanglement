# Methods & Assumptions Ledger

*The single, coherent statement of what this project's formal and
empirical machinery actually establishes — what is machine-checked,
what is numerically witnessed, and what is assumed. Read this once
instead of reconstructing it from the running audit log in
[`veridical_status.md`](veridical_status.md).*

This page is normative for claim-strength language anywhere in the
manuscript. If a sentence's strength disagrees with the ledger, the
ledger wins and the sentence is the bug.

---

## 1 — The three verification tiers

Every formal claim in the project sits in exactly one tier. The tiers
are not ranked by importance — they are ranked by *what kind of
guarantee they give a reader*.

| Tier | Guarantee | Where |
|---|---|---|
| **T1 — machine-checked in ℝ** | A Lean 4 + Mathlib proof of the *named mathematical statement*, depending only on the three standard foundational axioms (`propext`, `Classical.choice`, `Quot.sound`); `0 sorry/admit/axiom/native_decide`. Exact-arithmetic (`ℝ`-valued). | `lean/MathlibProofs/` |
| **T2 — machine-checked, Float boundary** | A Lean 4 (stock, Mathlib-free) proof that genuinely establishes its named statement over the in-house `CommScalar`/`Float` API. Substantive but elementary. | `lean/ActinfPolicyEntanglement/`, `faithfulness: substantive` rows |
| **T3 — typed analytic-boundary contract** | A Lean declaration that type-checks but whose analytic payload is *supplied as an explicit hypothesis* (witness-form) or proves a statement *strictly weaker than its manuscript name* (statement-restricted) or is true by `rfl`/forwarding (definitional/forwarder). **Not a stand-alone proof of the named proposition.** | `faithfulness: statement-restricted` rows; `status: witness/boundary/forwarder` rows |
| **N — numerically witnessed** | Not a proof. A deterministic-seeded numerical computation agreeing with the analytic quantity to a *gated tolerance* (exact recompute) or within a *sampling-error band* (finite-N estimator). | `src/`, `tests/`, dashboard invariants |

A claim may have both a formal tier and a numerical witness; the
numerical witness never upgrades the formal tier.

---

## 2 — The headline result: Theorem 5.1 (entanglement decomposition)

**Tier T1 — machine-checked in ℝ.** *(2026-05-19: the FULL S01
free-energy identity `F=Σ F[qᵏ]+γλ⟨K_c⟩+log Z_E−λ⟨J⟩+I(q)` is now
machine-checked in ℝ by `MathlibProofs.free_energy_decomposition_full`
— genuine `entangledPosterior`, `logZE` the definitional normalizer,
`I(q)` discharged via the kernel below; foundational-only axioms; two
independent negative controls; enforced by `build_mathlib_proofs.py`.
The earlier "kernel-only, full identity is residual (i)" framing is
retired — the sole residual is now the Float↔ℝ bridge.)*
`MathlibProofs.entanglement_decomposition_generalK` (the kernel the
full identity composes) proves, for
**general `K`** and a **general entangled joint `q`** — only strict
positivity (`∀ i, 0 < q i`) and normalization (`∑ q = 1`) assumed; `q`
is *never* assumed to factorize — with `m := ∏ₛ streamMarginal q s`
(the m-projection) and product reference `p`:

1. multi-information non-negativity `0 ≤ D(q‖m)` (Gibbs);
2. KL chain-rule decomposition `D(q‖p) = D(q‖m) + Σᵢ qᵢ·log(mᵢ/pᵢ)`;
3. m-projection minimality `D(q‖m) ≤ D(q‖p)`.

`#print axioms` → `[propext, Classical.choice, Quot.sound]` only;
`lake build` green (8249 jobs); file is `0 sorry/admit/axiom/native_decide`.
The previously ~5×-deferred core — the product-marginalization identity
`streamMarginal (∏ₜ factorₜ) s = factorₛ` — is discharged
unconditionally as `streamMarginal_productDist` and is **non-vacuous**:
forcing the marginal-matching step to reflexivity (the degenerate
`m := q` shortcut) makes the build fail, proving `m ≠ q` and that the
lemma is genuinely load-bearing. Locked by
`tests/test_mathlib_proofs_integrity.py` (presence + hygiene +
anti-degeneracy).

**Enforcement (no longer maintainer-attested).** The Tier-T1 claim is
gated by `scripts/build_mathlib_proofs.py` — `lake build` + grep
hygiene + a **`#print axioms` audit that fail-closes** if any keystone
theorem depends on a non-foundational axiom (`sorryAx`, a project/
Mathlib `axiom`, `native_decide`) — run on the `--with-mathlib` /
release path. The fast suite carries the grep-level tripwire
(`tests/test_mathlib_proofs_integrity.py`). "Machine-checked in ℝ"
therefore rests on a reproducible enforced command, not an assertion.

**The honest residual — Float↔ℝ (precisely scoped open problem).** The
`ℝ` layer certifies the *exact-arithmetic* mathematics. The Float
boundary companion `Decomposition.entanglement_decomposition` (Tier
T3, a typed `hWitness ↦ hWitness` contract) is its
**numerically-corroborated computational shadow**, corroborated by four independent existing
mechanisms: dashboard invariant `decomposition_lhs_eq_rhs_max_residual`
(worst-case `5.55e-16`), conservative interval brackets on the K=2
decomposition sweep grid
(`src/manuscript/float_real_interval.py` →
`output/reports/float_real_residual.json`; Tier **N** corroboration
only — not route (b) discharged), the seeded Monte-Carlo MI concentration /
√N-convergence tests (§4), and the K=2 numerical witness of the ℝ
capstone (`tests/test_theorem_map_content.py`, all three capstone
conjuncts to `1e-9`). This is corroboration, **not** a proof that the
Float pipeline realises the ℝ theorem.

*The precise obstruction (so this is a crisp research task, not a
hand-wave):* Lean 4's `Float` is opaque IEEE-754 binary64 exposed via
`@[extern]` compiler intrinsics; Mathlib has **no rounding model /
no lemmas** relating `Float` operations to their `ℝ` values. A
*verified* bridge therefore requires one of two known, sound routes,
each genuine multi-week formalization work, neither attempted here:
(a) a Flocq-style formal IEEE-754 model with per-operation
`|fl(x∘y) − (x∘y)| ≤ ½ ulp` lemmas, error-propagated through the
decomposition's `∑`/`log`/`exp` graph; or (b) an interval-arithmetic
re-implementation of the pipeline whose intervals provably bracket the
ℝ values. This is **scoped future work — not a defect and not an
impossibility**; it is the single thing standing between "analytic
content machine-checked in ℝ" and "the shipped Float numbers are
machine-checked". It is dishonest to relabel it closed; it is honest
to state it this precisely, corroborate it numerically as strongly as
possible (§4), and name the two sound routes. (Essentially all
formalized analysis lives in `ℝ`/`ℚ`; the strict-positivity hypothesis
*is* the project's S06 ambient strictly-positive simplex `M`, audited
as faithful, not a weakening — but that does **not** itself bridge
Float.)

---

## 3 — Per-row strength ledger (the 5 `proved` rows)

`status: proved` means "machine-checked in stock Lean with no analytic
witness assumption" — it does **not** assert the Lean statement *is*
the named manuscript proposition. The `faithfulness:` field
(`manuscript/refs/labels.yaml`, machine-enforced, pinned in
`tests/test_h1_headline_invariant.py`) records which:

| Row | Manuscript | Lean | Faithfulness | What is actually established |
|---|---|---|---|---|
| `cor_4_2` | Cor 5.2 | `couplingVerdict_correct` | **substantive** (T2) | the decision contract `verdict = true ↔ tax < gain` (genuine `decide_eq_true_iff`) |
| `cor_4_3` | Cor 5.3 | `couplingLogWeight_pointwise_at_zero` | **substantive** (T2) | the named λ=0 identity `couplingLogWeight … 0 = 0` (genuine, via `affine_at_zero`) |
| `prop_6_1` | Prop 7.1 | `mfImage_isMeanField` | **statement-restricted** (T3) | mean-field *membership* `IsMeanField (mfToJoint m)` by `rfl` — **not** e-flatness |
| `prop_6_2` | Prop 7.2 | `mProjection_kl_eq_self_when_meanfield` | **statement-restricted** (T3) | `kl q (mfToJoint m) = kl q q` *only when* `q = mfToJoint m` — **not** information-projection minimality |
| `prop_7_1` | Prop 8.1 | `isBipartiteMeanField_factors` | **statement-restricted** (T3) | an `Iff.rfl` definitional unfolding of the bipartite-mean-field predicate — **not** the named Schmidt-rank equivalence `r(q)=1 ⟺ MF` |

So of 5 `proved` rows: **2 substantive, 3 statement-restricted, 0
definitional-counted-as-genuine.** Headline counts in 0A/1A/1B/3A/6C
are derived from this field; every reader surface stating the
proved-count must co-locate this split (enforced repo-wide).

The `witness`/`boundary`/`forwarder` rows are Tier T3 typed contracts;
their analytic payloads are the Mathlib4 discharge targets. The
`MathlibProofs` package additionally carries genuine T1 ℝ kernels
(`klReal_nonneg`/Gibbs, `klReal_split_via_intermediate`,
`klReal_minimises_generalK`, `crossTerm_matches_K2`) that the witness
rows' payloads can be discharged from.

---

## 4 — Empirical estimator definitions (Tier N)

| Quantity | Estimator | Kind | Gate |
|---|---|---|---|
| K=2 Bernoulli MI, exact recompute | `bernoulli_toy.empirical_mutual_information` = `total_correlation(ising_joint_posterior(λ))` | **closed-form recompute** (NOT a sampler); agreement with `ising_mutual_information` to `BERNOULLI_VERIFICATION_TOLERANCE = 1e-9` is *internal analytic consistency* of two algebraically-independent closed forms | `tests/test_bernoulli_toy.py` |
| K=2 Bernoulli MI, finite sample | `bernoulli_toy.empirical_mutual_information_montecarlo(λ, N, seed)`: seeded multinomial draw from the 4-atom `ising_joint_posterior(λ)`, audited `total_correlation` of the empirical joint | **genuine stochastic estimator** — bias `O(1/N)`, sd `O(1/√N)`; converges to closed form *in the finite-sample sense*, with a `~4σ` concentration band and a √N-convergence test | `tests/test_bernoulli_toy.py` (the *real* empirical witness) |
| m-projection revertibility | `I(q_λ) = D_KL(q_λ ‖ m̂(q_λ))` | exact recompute, gated `≤ 1e-9` | `validate_outputs.py::revertibility_kl_equals_multiinformation` |
| closed-form vs empirical MI agreement | over `PARAMETER_SWEEP_LAMBDAS` grid | gated `≤ PARAMETER_SWEEP_AGREEMENT_TOLERANCE = 1e-6` | `tests/test_bernoulli_toy.py` |

All numeric values in manuscript prose flow
`hyperparameters.py → sidecars → manuscript_variables.json → [[VAR:]]
→ rendered prose`, range-gated by `validate_manuscript.py`.

---

## 5 — Assumption ledger (what is taken as given, project-wide)

- **Strictly-positive finite simplex `M`** — all `ℝ` KL/Gibbs results
  assume `∀ i, 0 < q i` and `∑ q = 1`. This is the manuscript's S06
  ambient manifold, not a convenience weakening.
- **Float arithmetic models exact arithmetic** — Tier T2/T3 Float
  declarations are taken to represent the intended `ℝ` semantics up to
  the numerically-witnessed residual; the verified bridge is the
  scoped residual (§2).
- **pymdp 1.0.1 / JAX float32 engine** — empirical free-energy bundle
  is computed in float32 then recast at the analytical boundary;
  single-stream agreement bounded `≤ pymdp_single_stream_float_tolerance`.
  Headline TC sentinels are reproducible to that budget, not to their
  display precision.
- **No mocks** — every test uses real numerical computation
  (`pytest-httpserver`/real files where I/O is needed); a test that
  asserts `f(a) ≈ f(a)` is a tautology and is treated as a defect, not
  coverage.

---

## See also

- [`veridical_status.md`](veridical_status.md) — the live audit map and
  full chronological provenance (this page is its normative summary).
- [`four_track_coherence.md`](four_track_coherence.md) — prose ↔ eq ↔
  Python ↔ Lean ↔ test wiring.
- `lean/MathlibProofs/MathlibProofs.lean` — the Tier T1 ℝ proofs.
- `tests/test_mathlib_proofs_integrity.py` — the T1 structural lock.
