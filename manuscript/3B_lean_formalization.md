# Lean 4 Formalization: Current Boundary, Witness Contracts, and Mathlib Scope

This section describes the Lean artifact that is actually built, rendered,
and validated in this repository. The source of truth is the
`ActinfPolicyEntanglement` boundary fragment under [`../lean/`](../lean/):
it compiles on stock Lean 4 [[VAR:lean_toolchain_version]], carries a Lean companion for every
numbered theorem in this manuscript, and is re-exported through
`FepSketches.*` for compatibility with the formalized-FEP line
[@friedman-2026-fep-lean]. The section no longer prints non-current
Mathlib sketch code. When the manuscript shows Lean, it shows live source
extracted from `lean/ActinfPolicyEntanglement/`.

## Current Lean artifact

The boundary fragment is **Mathlib-free by construction** and has a zero
hygiene budget: **0 strict `sorry`, 0 `axiom`, 0 `unsafe`, 0 `partial`,
0 `noncomputable`, and 0 `Mathlib` imports**. The current render reports
[[VAR:lean_lake_jobs_total]]/[[VAR:lean_lake_jobs_total]] Lake jobs green
over [[VAR:lean_submodule_count]] boundary submodules, with
[[VAR:lean_total_declarations]] total Lean declarations
([[VAR:lean_def_count]] defs, [[VAR:lean_theorem_count]] theorems / lemmas,
[[VAR:lean_structure_count]] structures).

Every numbered theorem row in `manuscript/refs/labels.yaml` has a live
Lean companion. The companions partition into four content classes
by what each one proves about the named proposition in the boundary
fragment:

- **algebraic** rows prove the named proposition outright in the
  boundary fragment;
- **definitional** rows prove a sub-statement of the named
  proposition (the boundary-content fragment the typed API
  commits to), with the propositional content named beyond that
  sub-statement discharged at $\mathbb{R}$-level by `MathlibProofs/`;
- **forwarder** rows re-export an already-proved boundary lemma;
- **typed-API** rows accept the analytic payload as a typed
  `structure` field and certify the result has the registered
  shape (with the analytic discharge living separately — fully
  done for [[THMREF:thm_4_1]] in `MathlibProofs/`, named target
  for the rest at [[SECREF:open_questions]] Q14).

| Class | Count | Boundary-fragment content (named propositions; full content reference) |
|---|---:|---|
| **algebraic** (`proved`, substantive) | [[VAR:theorem_proved_substantive_count]] | A complete machine-checked proof of the named proposition: [[THMREF:cor_4_2]] (coupling-verdict correctness — the Boolean decision procedure is sound) and [[THMREF:cor_4_3]] (the coupling log-weight vanishes pointwise at $\lambda=0$). |
| **definitional** (`proved`, scope-restricted) | [[VAR:theorem_proved_restricted_count]] | A machine-checked sub-statement of the named proposition: [[THMREF:prop_6_1]] (`mfImage_isMeanField` proves the definitional membership $\textsf{IsMeanField}(\textsf{mfToJoint}\,m)$ — every product distribution is mean-field, by `rfl`; the full e-flatness statement is discharged at $\mathbb{R}$-level), [[THMREF:prop_6_2]] (`mProjection_kl_eq_self_when_meanfield` proves the KL equality that pins the $m$-projection's value when $q$ is already mean-field; information-projection minimality is the $\mathbb{R}$-level discharge), [[THMREF:prop_7_1]] (the definitional unfolding of the bipartite-mean-field predicate `Iff.rfl`-checked; the Schmidt-rank equivalence $r(q)=1\iff$ mean-field is the $\mathbb{R}$-level discharge target). |
| **forwarder** | [[VAR:theorem_status_forwarder_count]] | The Lean declaration re-exports an already-proved boundary lemma. |
| **typed-API** (`boundary` + `witness-form`) | [[VAR:theorem_status_boundary_count]] + [[VAR:theorem_status_witness_count]] | The Lean declaration commits the caller to a specific decomposition shape and parameter-threading discipline. [[VAR:theorem_status_boundary_count]] `boundary` rows fix the algebraic interface and log-weight skeleton; [[VAR:theorem_status_witness_count]] `witness-form` rows accept the analytic payload (KL chain-rule identity, convexity certificate, rank semicontinuity, concentration bound) as a typed `structure` field. The analytic content for the central row [[THMREF:thm_4_1]] is established at $\mathbb{R}$-level in `MathlibProofs/`; the analytic content for the remaining typed-API rows is the discharge target of [[SECREF:open_questions]] Q14. |

The four classes are pinned per-row by the `faithfulness:` field in
`manuscript/refs/labels.yaml`, audited at every render by
`docs/reference/veridical_status.md`, and locked against silent
re-inflation by `tests/test_h1_headline_invariant.py`. The normative
ledger of which substrate proves what is
`docs/reference/methods_and_assumptions.md`.

The typed-API class is not a hidden proof of the analytic content.
It is a machine-checked contract: the caller supplies a witness
field, and the boundary fragment certifies that the result has the
theorem's advertised shape. The numerical layer in `src/lean/`,
`src/simulation/`, and the dashboard invariants exercises these
contracts on concrete Bernoulli, Ising, pymdp, $K = 3$, $K = 4$,
long-horizon, and revertibility instances; the Mathlib4 discharge
layer establishes the analytic identity at the $\mathbb{R}$ level
for the central case.

## What Mathlib4 is used for

Mathlib4 is in scope as the **analytic discharge library**, not as a hidden
dependency of the current boundary fragment. This separation is the most
rigorous division for this project:

The distinction mirrors the external toolchain rather than a local
terminological preference: Lean is the proof assistant and programming
language whose trusted kernel checks the boundary fragment
[@demoura-ullrich-2021; @lean-fro-2026], while Mathlib is the
community mathematical library that supplies the reusable analysis,
probability, algebra, and linear-algebra substrate for future and
current analytic discharges [@mathlib-2020; @lean-fro-mathlib-2026].
Accordingly, a theorem row is never promoted merely because a typed
witness argument exists in the boundary API; promotion requires the
row-specific Lean/Mathlib source and its gate to build.

| Layer | Current status | Why this is the right boundary |
|---|---|---|
| `lean/ActinfPolicyEntanglement/` | Builds without Mathlib on Lean 4 [[VAR:lean_toolchain_version]]. | Keeps the theorem registry fast, reproducible, and hygiene-auditable. |
| Witness `structure`s | Current Lean source. | Names the exact analytic payload each theorem needs without pretending it has been derived inside Mathlib. |
| `lean/MathlibProofs/` | Mathlib-backed analytic discharge package; **machine-checks the full S01 boxed free-energy identity ([[THMREF:thm_4_1]]) in $\mathbb{R}$** via `free_energy_decomposition_full`, with the multi-information term discharged through the axiom-clean general-$K$ kernel `entanglement_decomposition_generalK`.  Foundational-only `#print axioms` (no `sorryAx`, two independent negative controls); enforced by `scripts/build_mathlib_proofs.py` and `tests/test_mathlib_axiom_audit.py`. | Promotes [[THMREF:thm_4_1]] (the central result) to $\mathbb{R}$-verified; the Float boundary fragment in this same project is the numerically-corroborated shadow with one open residual (a *verified* error-bounded Float$\leftrightarrow\mathbb{R}$ bridge, scoped in `docs/reference/methods_and_assumptions.md` as multi-week future research). |
| Manuscript + Python evidence | Current, validated. | Shows the analytic identities by derivation and numerical execution while the Mathlib discharge remains separate. |

The Mathlib target is therefore precise but non-misleading: it tells a Lean
contributor where the analytic proof obligations live, while the present
manuscript only claims what the current build and tests actually validate.

## Mathlib4 analytic targets

The following table is not source code. It is the current dependency map
from witness payload to the Mathlib4 area that should discharge it:

| Witness payload | Boundary theorem(s) | Mathlib area |
|---|---|---|
| Finite KL / entropy chain rule | [[THMREF:thm_4_1]], [[THMREF:prop_6_3]], [[THMREF:prop_6_5]], [[THMREF:prop_11_3]] | PMF / finite-measure probability, finite sums, logarithms, and KL-style entropy identities |
| Convexity and local Taylor behavior in $\lambda$ | [[THMREF:thm_4_3]], [[THMREF:prop_10_1]] | Convex analysis, differentiability / Taylor expansion, real logarithm and exponential facts |
| Bregman / quadratic coupling-tax envelope | [[THMREF:thm_8_1]], [[THMREF:cor_8_2]] | Taylor expansion plus local convex-analysis primitives; no current Mathlib Bregman divergence module is assumed |
| Rank and spectral continuity | [[THMREF:prop_7_2]], [[THMREF:thm_7_3]] | Matrix rank, semicontinuity, tensor-product and finite-dimensional linear-algebra infrastructure |
| Concentration and recursive embedding | [[THMREF:thm_11_1]], [[THMREF:prop_11_2]] | measure tightness, KL convergence, and recursive fixed-point infrastructure |

This map also explains why the boundary fragment should not import Mathlib
directly. Several targets are already present in Mathlib4, several need
local finite-discrete definitions on top of existing primitives, and some
would require new upstream work. The current artifact remains honest by
keeping those as named witness payloads instead of interleaving partial
Mathlib development with the verified boundary.

Two recent Mathlib infrastructure papers anchor the measure-theoretic
end of this map: the Markov-kernel formalization in
`MeasureTheory.Probability.Kernel.*` [@degenne-2025] supplies the
kernel-composition / disintegration primitives used by KL chain-rule
discharge, and the recent Brownian-motion formalization in the same
namespace [@brownian-lean-2025] anchors the continuous-time
infrastructure that any future extension to continuous policy spaces
(currently out of scope, see [[SECREF:open_questions]] Q4) would build
on.  Both references are cited here as anchors for the witness-discharge
direction, not as in-flight dependencies of the current build.

## Live-source injection

The companion supplement [[SECREF:app.lean_skeleton]] is the executable
audit trail. It does not contain hand-copied theorem blocks. Each
`[[LEAN:<label>]]` token is resolved as follows:

1. `manuscript/refs/labels.yaml` names the theorem's `lean_module` and
   `lean_name`.
2. `src/manuscript/lean_extract.py` indexes declarations from the live
   `.lean` files under `lean/ActinfPolicyEntanglement/`.
3. `src/manuscript/renderer.py` embeds the exact source block with source
   coordinates and the registry status.
4. `scripts/validate_manuscript.py` fails if any Lean declaration, theorem
   token, section reference, figure reference, equation reference, citation,
   or variable token is unresolved.

This is the reason the supplement can be read as source evidence rather than
as prose illustration: if a theorem is renamed or moved, the next render
fails instead of silently shipping stale text.

## What the Lean track proves today

The current Lean track proves the algebraic and structural statements that
do not require measure-theoretic or real-analysis infrastructure:

* λ = 0 reductions and coupling-log-weight affineness;
* Boolean coupling-verdict correctness;
* definitional total-correlation unfoldings over the local scalar API;
* e-geodesic forwarding through the affine log-weight identity;
* the bipartite rank-one / mean-field interface on the boundary fragment;
* stream-mode totality and structural monotonicity lemmas used by the
  manuscript's theorem registry.

The witness-form theorems then isolate the analytic content that belongs to
Mathlib4. That is not a weakness in the current artifact; it is the
mechanism that keeps each claim assigned to the tool that can actually check
it. The manuscript's theorem statements, Python witnesses, pymdp harness,
figures, and dashboard invariants show the analytic behavior now; a separate
Mathlib-backed library can later replace supplied witness fields with
derived fields without changing the boundary theorem names or manuscript
registry wiring.

## The verification stack

Three layers compose the verification, each with a precise role:

**$\mathbb{R}$-level proof (`MathlibProofs/`).**  The full S01 boxed
free-energy identity
$F[q_\lambda]=\sum_k F[q^k_\lambda]+\gamma\lambda\langle K_c\rangle+\log Z_E(\lambda)-\lambda\langle J\rangle+I(q_\lambda)$
([[THMREF:thm_4_1]]) is machine-checked by
`MathlibProofs.free_energy_decomposition_full`, with the
multi-information term discharged through the axiom-clean general-$K$
kernel `entanglement_decomposition_generalK` and surfaced for direct
callers as `multiInformation_nonneg_at_joint`. Positivity and unit
mass of $q_\lambda$ are proved from the definitions; per-stream
marginals are positive by the standalone `streamMarginal_pos` lemma;
$\log Z_E$ is the definitional log-normalizer; two independent
negative controls make the build fail when neutralised. Only the
three foundational axioms (`propext`, `Classical.choice`,
`Quot.sound`) remain on `#print axioms`, with zero `sorry` / `axiom`.
The build and axiom audit are enforced by
`scripts/build_mathlib_proofs.py` plus
`tests/test_mathlib_axiom_audit.py` (9-keystone foundational-only
gate) and pinned by `tests/test_mathlib_proofs_integrity.py`
(keystone list and proof-body non-triviality past `:= by`).

**Typed-API layer (`lean/ActinfPolicyEntanglement/`).**  The stock-
Lean [[VAR:lean_toolchain_version]] boundary fragment hosts the [[VAR:theorem_registry_count]]-row
Lean companion surface ([[SECREF:app.lean_skeleton]]) as a typed API:
the algebraic rows are proved at the boundary, the definitional
rows pin scope-restricted statements, the typed-API rows accept
analytic payloads as `structure` fields, and the forwarder row
re-exports.  The fragment compiles with zero strict `sorry`, zero
axioms beyond stock Lean, no Mathlib dependency, and no
`unsafe`/`partial`/`noncomputable` declarations.  Its role is to
keep the theorem registry fast, reproducible, hygiene-auditable,
and source-extractable into the manuscript prose without dragging
in the analytic substrate at every render.

**Numerical layer (`src/lean/`, `src/simulation/`).**  Every
identity is evaluated on finite ensembles.  The worst-case
decomposition residual on the coupling-ablation suite is
$[[VAR:coupling_ablation_decomposition_residual_max:.2e]]$ —
floating-point round-off precision — recorded in
`decomposition_lhs_eq_rhs_max_residual` and regenerated on every
build alongside the other dashboard invariants; the same residuals are
exported to ``output/reports/float_real_residual.json`` for machine audit
(see ``FloatRealResidualWitness`` in the Lean boundary fragment — roadmap
witness row, not a closed Float↔ℝ proof).

The three layers are pipeline-bound: the dashboard invariants tie
the typed-API and numerical layers to the same per-run content, and
`MathlibProofs/` discharges the analytic content the typed-API rows
name.  A *verified* error-bounded Float$\leftrightarrow\mathbb{R}$
bridge — either a Flocq-style formal IEEE-754 model with
per-operation $|\mathrm{fl}(x\circ y)-(x\circ y)|\leq \tfrac{1}{2}\,\mathrm{ulp}$
error propagation through the $\sum$/$\log$/$\exp$ graph
[@ieee-754-2019; @boldo-melquiond-2011], or an
interval-arithmetic re-implementation provably bracketing the
$\mathbb{R}$ values — is the natural formal sibling of the present
empirical binding; [[SECREF:open_questions]] Q14 and
`docs/reference/methods_and_assumptions.md` carry the route map.

When the manuscript says "Lean-checked", the analytic content lives
in the $\mathbb{R}$-level layer for the central case and in the
typed-API layer's algebraic and definitional rows for the surface
the boundary fragment owns.  No claim in this manuscript asserts a
Float-arithmetic verification of an analytic identity; no claim
asserts that the boundary fragment proves the analytic content of
the typed-API rows.

## Validation gates

The Lean / Mathlib boundary is validated by the same project gates that
validate the manuscript:

| Gate | What it catches |
|---|---|
| `uv run python scripts/build_lean.py` | Lean build failures, strict `sorry`, `axiom`, unsafe / partial / noncomputable regressions, accidental Mathlib imports in the boundary fragment. |
| `uv run python scripts/validate_manuscript.py` | Dangling theorem, Lean, equation, section, figure, citation, and variable tokens; hardcoded section / theorem references; hardcoded numeric results. |
| `uv run pytest tests/ --cov=src --cov-fail-under=95` | Python numerical witnesses, pymdp contracts, renderer / registry behavior, project-wide link integrity, American-English prose guard, and regression coverage. |
| `uv run python scripts/run_all.py` | End-to-end regeneration of figures, sidecars, manuscript variables, dashboard, theorem map, output validations, and regression baseline. |

The result is a clean division of responsibility: current Lean source is
only what builds; Mathlib4 is documented only where it is the correct
analytic proof substrate; no non-current Mathlib code block is presented as
part of the validated manuscript.
