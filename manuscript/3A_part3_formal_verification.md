# Part III — Formal Verification {-}

Verification in this manuscript is layered: the manuscript's central
analytical identity is machine-checked in $\mathbb{R}$ by a
Mathlib4-backed Lean package; an independent stock-Lean [[VAR:lean_toolchain_version]]
boundary fragment ships the same theorem surface as a typed API so
downstream callers and the Python computational layer commit to a
specific decomposition shape; and a numerical companion in
`src/lean/` evaluates every identity on finite ensembles to
floating-point tolerance. "Machine-checked" means exactly that:
Lean's kernel has type-checked the proof object, `#print axioms`
has been inspected on the relevant declarations, and only the three
foundational axioms of Lean itself (`propext`, `Classical.choice`,
`Quot.sound`) remain.

## What is proved {-}

The entanglement decomposition [[THMREF:thm_4_1]] is established at
$\mathbb{R}$-level by
`MathlibProofs.entanglement_decomposition_generalK` for general $K$
and a *general entangled* joint $q$ (strict positivity and
normalization the only hypotheses; $q$ is never assumed to
factorize). The proof establishes the three components the manuscript
uses downstream:

- non-negativity of the multi-information $0 \le D(q\,\|\,\hat m(q))$;
- the KL chain-rule identity
  $D(q\,\|\,p) = D(q\,\|\,\hat m(q)) + \sum_i q_i\log(m_i/p_i)$;
- $m$-projection minimality.

The product-marginalization core `streamMarginal_productDist` and
the companion finite-KL kernels (`klReal_nonneg` / Gibbs,
`klReal_split_via_intermediate`, `klReal_minimises_generalK`) are
discharged from the standing positivity + normalization
hypotheses without further structural assumptions, and
negative-control-verified as non-vacuous, all under the same
foundational-only axiom set. The
full S01 boxed identity
$F[q_\lambda] = \sum_k F[q^k_\lambda] + \gamma\lambda\langle K_c\rangle + \log Z_E(\lambda) - \lambda\langle J\rangle + I(q_\lambda)$
is then machine-checked by `MathlibProofs.free_energy_decomposition_full`
for the genuine entangled posterior, with $\log Z_E$ the
definitional log-normalizer (not an assumed scalar),
positivity and unit-mass proved (not assumed), the multi-information
term discharged through the general-$K$ kernel above, and two
independent negative controls. The build and axiom audit are
enforced by `scripts/build_mathlib_proofs.py`, which runs `lake
build`, reads `#print axioms` on every certified declaration, and
fails the gate on any non-foundational axiom or non-empty
`sorryAx` list.

## How the verification stack composes {-}

The $\mathbb{R}$-level proof is the *verification* layer. The
stock-Lean [[VAR:lean_toolchain_version]] boundary fragment under `lean/` is the *typed-API*
layer: it ships the same theorem surface in `Float` arithmetic
without Mathlib, with the analytic content of each statement either
proved at the boundary (the algebraic identities — the four-term
re-grouping, the affineness of the coupling log-weight in $\lambda$,
the bipartite Schmidt-rank-1 $\iff$ mean-field equivalence, the
verdict-correctness lemma, the at-zero collapse, $m$-projection
factorization) or carried as an explicit typed hypothesis (the
analytic identities whose discharge is the $\mathbb{R}$ layer's
job). This factoring is deliberate: it forces every downstream
caller, including the separate Mathlib4 discharge layer, to commit
to a specific decomposition shape and parameter-threading
discipline, and it gives the stock-Lean fragment a hygiene contract
(zero `sorry`, zero axioms beyond stock Lean, zero Mathlib
dependencies, zero `unsafe` / `partial` / `noncomputable`) that
holds independently of the analytic layer's state.

The numerical companion in `src/lean/` and the pymdp harness of
[[SECREF:pymdp_harness]] then evaluate every identity on finite
ensembles. The worst-case decomposition residual on the
coupling-ablation suite is
$[[VAR:coupling_ablation_decomposition_residual_max:.2e]]$ —
consistent with floating-point round-off at the scale of the
inputs — and the dashboard invariant
`decomposition_lhs_eq_rhs_max_residual` is regenerated on every
build. The pipeline runs at `Float`; the proof runs at $\mathbb{R}$;
the dashboard invariants tie the two layers to the same numerical
content per run. A *verified* error-bounded
Float$\leftrightarrow\mathbb{R}$ bridge — either a Flocq-style
formal IEEE-754 model or an interval re-implementation — would
formally tie the two layers, and is scoped at [[SECREF:discussion]]
as roadmap research; the present pipeline binds them empirically
via the dashboard invariants.

## Where to read the per-row content {-}

[[SECREF:lean_plan]] contains the per-theorem surface: the live
source, the analytic content each row certifies in the boundary
fragment, and the exact Mathlib4 namespace targets for the
$\mathbb{R}$ discharges. The auto-generated theorem map at
[`docs/reference/_theorem_map.md`](../docs/reference/_theorem_map.md)
indexes every theorem by its four-track wiring (registry label →
manuscript token → Lean declaration → Python witness → test gate),
and `docs/reference/veridical_status.md` carries the per-row
`status:` (proved / forwarder / witness / boundary) and
`faithfulness:` (substantive / typed-API / definitional /
re-export) fields. A reader can therefore enter on any track —
manuscript theorem statement, Lean source, Python witness, or test
gate — and traverse to any other in one hop. The companion
supplement [[SECREF:app.lean_skeleton]] reproduces the live source
excerpts at chapter length so the prose → Lean traversal is
single-document.

One chapter follows:

* **[[SECREF:lean_plan]]** — the current theorem-proving surface,
  the per-row content table, the typed-API discipline that factors
  algebraic content from analytic payloads, and the Mathlib4
  namespace targets for ongoing analytic discharge.

---
