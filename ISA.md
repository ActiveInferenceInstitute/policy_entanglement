---
project: actinf_policy_entanglement_lean
task: Comprehensive whole-project publication-readiness review — verify all claims (recent GNN additions + previously-untouched parts), fix drift/over-claims, harden the soundness gate, certify ready or scope residuals
slug: 20260524-actinf-pubready-review
effort: E4
phase: complete
progress: 26/26
mode: complete
started: 2026-05-24T15:30:00-07:00
updated: 2026-05-24T16:30:00-07:00
v1_commit: 8b41085
docs_commit: 85a8224
---

# ISA — actinf_policy_entanglement_lean: whole-project publication-readiness review

## Problem

The user asks for a deep, comprehensive review of the **entire** project — the recent
GNN fifth-track additions AND the previously/untouched parts — to verify all claims,
improve/move/remove writing, and certify everything is complete, accurate, and ready.
The project has a long integrity record (`project-actinf-integrity-state`, passes 6–13)
with a precise known-open residual list (the Float↔ℝ verified bridge; the terminal
`prop_11_2`/`thm_11_1`). The bar: verify FRESH on disk (convergent-automation churn can
drift the untouched parts), never re-spin a known-open residual as closed, never fabricate
the Float↔ℝ bridge (recurrence-#8 guardrail), and the honest output may be "genuine core +
precise residuals," not "all good."

## Vision

A referee opening the artifact finds: a green authoritative gate; the ℝ analytic keystone
machine-checked foundational-only with a **dated static witness** they can read without
rebuilding; headlines whose proof-strength claims co-locate their deficits (2-of-5
substantive proved; Float↔ℝ open); per-proposition statement-restriction disclosure; a
GNN fifth track consistent with the body; no hardcoded numerics/versions bypassing the
token system; and a soundness gate that **fails loudly** on a broken build rather than
skipping green. The verdict is an explicit certify/non-certify with named residuals.

## Out of Scope

- Fabricating or claiming the Float↔ℝ verified bridge, or any Float-level verification.
- Re-spinning `prop_11_2`/`thm_11_1` (terminal) or the Float↔ℝ residual as "closed".
- Editing the verified ℝ core or boundary-fragment `.lean` files (review re-verifies only).
- Restructuring a green, hard-won gate where the limitation is bounded + already mitigated
  (the H-gap sweep gate) — scope it, don't churn it.

## Principles

- **Verify fresh on disk myself** — run the gate + the ℝ-core `#print axioms` audit this
  session; do not trust prior green or any agent's report (`feedback-verify-not-trust-machine-proof`).
- **Fail-closed on soundness** — a soundness gate must fail loudly on a broken build, never skip green.
- **No over-claim; co-locate deficits** — grep is necessary, not sufficient; advisor checks co-location.
- **Cross-vendor** — RedTeam + Forge catch what an in-family green count cannot.
- **Honest residuals stay residuals** — name them; never conceal, never fake-close.

## Constraints

- Gate must stay green (build_dashboard → regression_gate exit 0); ℝ keystone `#print axioms`
  foundational-only (`propext`/`Classical.choice`/`Quot.sound`).
- No `.lean` core edits this session; no manuscript over-claim introduced.
- Any gate-hardening fix must be non-vacuous (negative control) and must not break the green path.
- Token discipline: no hardcoded numerics/versions bypassing `[[VAR:...]]`.

## Goal

Verify every claim class fresh on disk (gate, ℝ keystone, headline/registry honesty, Lean
faithfulness, empirical/witness gates, GNN-in-context, writing/cross-refs), fix the genuine
drift/over-claims surfaced, harden the one real soundness-gate defect (axiom-audit
skip→fail) with a non-vacuous control + a dated static witness, and produce an explicit
publication-readiness verdict with named residuals. Done = gate green, keystone re-verified
foundational-only on disk, all HIGH/MEDIUM findings fixed-or-scoped, advisor + Forge +
RedTeam concur, and a certify verdict issued.

## Criteria

### Fresh truth (R8/R10)
- [x] ISC-1: full gate run fresh this session — exit 0, 0 failures, coverage ≥ floor, Lean boundary 22/0/0/0.
- [x] ISC-2: ℝ-core keystone `#print axioms` re-verified on disk MYSELF (build_mathlib_proofs.py) — foundational-only, exit 0.
- [x] ISC-3: manuscript renders with 0 dangling tokens after all edits.

### Adversarial coverage (RedTeam + Forge + advisor)
- [x] ISC-4: RedTeam verifier-attack on the gate/oracle run; completeness gaps captured.
- [x] ISC-5: RedTeam V1 (headline/registry honesty) run; clean or fixed.
- [x] ISC-6: RedTeam V2 (empirical/witness/VAR vacuity) run; clean or scoped.
- [x] ISC-7: RedTeam V3 (Lean registry faithfulness) run; clean or fixed.
- [x] ISC-8: RedTeam V4 (writing/cross-refs/GNN-in-context) run; findings fixed.
- [x] ISC-9: Forge whole-project cross-vendor readiness audit run; verdict captured.
- [x] ISC-10: advisor commitment-boundary readiness call run (HARD at E4).

### NOT-READY flippers (advisor) — must verify before sign-off
- [x] ISC-11: two-route TC witness (`total_correlation` vs `total_correlation_via_kl`) confirmed genuinely disjoint on disk (a marginalization/log-base bug diverges, not silently agrees).
- [x] ISC-12: no manuscript prose lets "verified/proven/machine-checked" cross the Float↔ℝ bridge to the numerical layer unqualified (grep + read confirmed).

### Genuine fixes from the review
- [x] ISC-13: S08 hardcoded `7.77e-16` literal → `[[VAR:gnn_roundtrip_max_residual:.2e]]` token.
- [x] ISC-14: S08 three mis-pointed `[[SECREF:open_questions]]` (GNN residuals) → `[[SECREF:app.gnn_downstream]]` (legit Q8 graph-neural-network refs kept).
- [x] ISC-15: 1C hardcoded `stock Lean v4.29.0` → `[[VAR:lean_toolchain_version]]` (pre-existing drift in untouched parts).
- [x] ISC-16: soundness-gate fail-closed fix — `tests/test_mathlib_axiom_audit.py` no longer skips-green on a nonzero build with the toolchain present; nonzero → FAIL (the advisor+Forge #1 must-fix).
- [x] ISC-17: ISC-16 fix is NON-VACUOUS — `classify_axiom_probe` unit test proves nonzero/sorryAx → "fail" even with the xfail opt-out; green path (rc=0) unchanged.
- [x] ISC-18: dated static axiom-audit witness committed (`docs/_audit/MATHLIB_AXIOM_AUDIT.md`) so a referee confirms foundational-only without rebuilding.

### Verified-clean (confirmed, no change needed)
- [x] ISC-19: headlines (0A/1A/3A) honest — deficit co-located, no count drift, "four tracks" correct (S06 holds GNN as separately-tabulated non-proof track).
- [x] ISC-20: all 5 `proved` rows statement-faithful (2 substantive + 3 statement-restricted); faithfulness pins truth-binding (not shape-only).
- [x] ISC-21: 2F/2G Takeaway boxes carry per-proposition statement-restricted disclosure (co-located).
- [x] ISC-22: CITATION.cff + reader surfaces carry no proved-count over-claim.
- [x] ISC-23: empirical gates (revertibility, robustness null-control, sentinel guard, decomposition/coupling-tax conformance) discriminating, not vacuous.

### Residuals + verdict
- [x] ISC-24: residuals named honestly (Float↔ℝ bridge; prop_11_2/thm_11_1 terminal; H-gap sweep gate = column-consistency not two-route, bounded; oracle-completeness gaps for new reader surfaces).
- [x] ISC-25: explicit publication-readiness verdict (CERTIFY / READY-WITH-FIXES / NOT-READY) with named residuals.
- [x] ISC-26: Anti: no known-open residual re-spun as closed; no Float↔ℝ verification claimed; no `.lean` core edited (re-verified intact).

## Test Strategy

| isc | type | check | tool |
|-----|------|-------|------|
| ISC-1 | command | regression gate exit 0 | build_dashboard + regression_gate |
| ISC-2 | command | `#print axioms` foundational-only | build_mathlib_proofs.py |
| ISC-11 | reasoning+code | two routes diverge on a wrong marginal/log-base | read free_energy.py + test_witness_conformance |
| ISC-12 | grep+read | no unqualified verified-crossing | Grep |
| ISC-13..15 | grep+render | token/secref fixes resolve | inject + validate_manuscript |
| ISC-16,17 | negative-control | classify_axiom_probe fail-closed | pytest |
| ISC-25 | verdict | certify/non-certify issued | advisor + synthesis |

## Features

| name | satisfies | depends_on |
|------|-----------|------------|
| fresh-truth | ISC-1..3 | — |
| adversarial | ISC-4..10 | fresh-truth |
| flippers | ISC-11,12 | adversarial |
| fixes | ISC-13..18 | adversarial |
| clean-confirm | ISC-19..23 | adversarial |
| verdict | ISC-24..26 | all |

## Decisions

- 2026-05-24: effort E4 (classifier fail-safe E3 on timeout; context-override — comprehensive review + ultrathink + heavy integrity history demands advisor + cross-vendor + RedTeam).
- 2026-05-24: deployed 1 verifier + 4 vector RedTeam specialists + Forge cross-vendor + advisor, armed with registry ground truth + the known-honest-residual list (hunt drift, not re-litigate honest residuals).
- 2026-05-24: H-gap sweep gate (V2 MEDIUM) — left structurally unchanged (green, bounded, single-column drift caught by an existing NC, genuine two-route TC test exists in test_witness_conformance); scoped as a residual rather than churned. No manuscript over-claim (4B grep clean).
- 2026-05-24: no consolidated "scope of verification" paragraph added — the delineation already exists co-located (abstract + 3A "What is proved" + Float↔ℝ section + 2F/2G per-proposition callouts + 3B 2-of-5 + S07 legend + veridical_status); adding would duplicate + risk drift.

## Changelog

- **conjectured**: a green regression gate certifies the project is publication-ready.
- **refuted_by**: RedTeam verifier + Forge (both on disk) — the gate's `test_mathlib_axiom_audit` SKIPPED-green on a nonzero build with the toolchain present (the fail-loud assert was unreachable), so a broken/unsound ℝ-core build (sorryAx / non-foundational axiom) would show green; and the gate cannot see semantic-but-valid token mis-targets, hardcoded-numeric recurrence, or reader surfaces outside the 4-file whitelist.
- **learned**: a green gate is necessary, not sufficient, for readiness — the soundness gate must fail-closed (nonzero+toolchain-present → FAIL), and a dated static witness + cross-vendor + advisor co-location review cover what the gate structurally cannot. Verify the keystone on disk myself; the gate's honest-xfail path is not a substitute.
- **criterion_now**: `classify_axiom_probe` fail-closes nonzero builds (unit-tested non-vacuous); `docs/_audit/MATHLIB_AXIOM_AUDIT.md` is the dated witness; token/secref drift fixed.

## Verification

- ISC-2: ℝ keystone re-verified on disk — `build_mathlib_proofs.py` EXIT 0; `free_energy_decomposition_full` + 8 keystones `#print axioms = [propext, Classical.choice, Quot.sound]`; "OK MathlibProofs builds, clean local hygiene, 9 keystone theorem(s) #print-axioms foundational-only". Static witness: `docs/_audit/MATHLIB_AXIOM_AUDIT.md`.
- ISC-3: manuscript renders — `✓ rendered token leak check: 38 rendered section files`, `All manuscript validations passed` (0 dangling) after token/secref fixes.
- ISC-4: RedTeam verifier-attack → ORACLE-INCOMPLETE (green gate necessary-not-sufficient; the axiom-audit xfail-green gap + the reader-surface whitelist gap captured).
- ISC-5: V1 (headline/registry) → LOW/clean; deficit co-located, no count drift, "four tracks" correct.
- ISC-6: V2 (empirical/witness) → MEDIUM (H-gap sweep gate shared-route, bounded); everything else clean.
- ISC-7: V3 (Lean faithfulness) → LOW/clean; 5 proved rows faithful, keystone no hmarg degeneracy, pins truth-binding.
- ISC-8: V4 (writing/cross-refs/GNN) → HIGH/MEDIUM findings (S08 literal, 3 secref mis-points, 1C version) all FIXED.
- ISC-9: Forge cross-vendor whole-project audit → READY-WITH-FIXES, 0 criticals; confirmed-honest list captured; named the axiom-audit skip-bug as the one soft spot.
- ISC-10: advisor commitment-boundary readiness call run → READY-WITH-FIXES; 4 conditions; the axiom-audit fail-closed as #1.
- ISC-11: two-route TC disjointness CONFIRMED on disk — `total_correlation` (ΣH(marginal)−H(joint)) vs `total_correlation_via_kl` (KL(q‖∏marginals)); a marginalization/log-base bug diverges (the identity holds only for true marginals), not silent agreement.
- ISC-12: no "verified/proven/machine-checked" crosses the Float↔ℝ bridge unqualified — grep co-occurrences all properly scoped (1C:136 "machine-checks ℝ and tests the Float"; 3B:218 the roadmap bridge; 3B:231 "no claim"; 3A:10 the precise "machine-checked means…").
- ISC-13: S08 `7.77e-16` → `[[VAR:gnn_roundtrip_max_residual:.2e]]` (renders).
- ISC-14: S08 :40/:70/:133 `[[SECREF:open_questions]]` → `[[SECREF:app.gnn_downstream]]`; legit Q8 graph-NN refs (:41,:43) kept; renders.
- ISC-15: 1C:129 `stock Lean v4.29.0` → `stock Lean [[VAR:lean_toolchain_version]]`.
- ISC-16: `tests/test_mathlib_axiom_audit.py` fail-closed — `classify_axiom_probe` replaces the skip-on-nonzero; nonzero+toolchain-present → FAIL. Both axiom-audit tests pass (`tests/test_mathlib_axiom_audit.py ..`).
- ISC-17: NON-VACUITY — `test_classify_axiom_probe_is_fail_closed` green: rc=0→pass; rc≠0 (incl. sorryAx) → "fail" even with xfail opt-out; only provisioning-gap+opt-out → xfail. Green path (rc=0) unchanged → no regression.
- ISC-18: `docs/_audit/MATHLIB_AXIOM_AUDIT.md` dated witness committed (verbatim `#print axioms`, command, exit, scope).
- ISC-19: headlines (0A/1A/3A) confirmed honest (V1 + Forge).
- ISC-20: 5 proved rows statement-faithful; `_PINNED_FAITHFULNESS` truth-binding (V3).
- ISC-21: 2F/2G Takeaway boxes carry the statement-restricted callout (re-read on disk).
- ISC-22: CITATION.cff "central identity machine-checked in ℝ … four CI-gated tracks" — no proved-count over-claim (read on disk).
- ISC-23: empirical gates discriminating (revertibility fixed-constant tol; null-control fraction; sentinel guard; decomposition/coupling-tax two-route) — V2 + Forge confirmed.
- ISC-24: residuals named — Float↔ℝ bridge; terminal prop_11_2/thm_11_1; H-gap-gate column-consistency (bounded); oracle-completeness gaps (manual-pass-mitigated).
- ISC-26: Anti — no residual re-spun closed; no Float↔ℝ verification claimed; zero `.lean` core edits (keystone re-verified intact). Confirmed.
- ISC-1: certification gate GREEN on disk — `Regression gate passed.`, `regression_gate EXIT=0`; `✓ test count 1410 ≥ 1353`, `✓ test failures 0 ≤ max 0`, `✓ coverage 95.64% ≥ 94.22%`, `✓ invariants 47/47`, `✓ lake jobs 22`, `✓ Lean sorries/axioms/unsafe = 0`. (The one-word `catalogued`→`cataloged` AmE slip was caught by the gate and fixed; `test_american_english` passes; this run is the clean token with the hardened fail-closed axiom-audit test counted.)
- ISC-25: **VERDICT = READY (CERTIFY) with named residuals.** The artifact is accurate and complete and the gate + ℝ-keystone audit + cross-vendor + advisor concur; the named residuals are honest *future work*, not blockers: (a) the Float↔ℝ verified bridge (multi-week Lean research, never to be faked); (b) terminal `prop_11_2`/`thm_11_1` (no independent numeric route possible in principle); (c) the H-gap sweep gate is a column-consistency check, not a two-route witness (bounded — single-column drift caught + genuine two-route TC test exists); (d) oracle-completeness gaps (the green gate cannot see semantic-but-valid token mis-targets, hardcoded-numeric recurrence, or reader surfaces outside the 4-file whitelist — mitigated by this review's manual pass + the fail-closed axiom gate + the dated witness).

🔒 ARTIFACT-BACKING: every `[x]` carries a quoted token (gate output, axiom line, render check, test names, file:line fixes). 0 reverted.

## v1 ship closure (`8b41085` / `85a8224`)

- **Code ship @ `8b41085`:** Zenodo DOI live (`10.5281/zenodo.20301239`); 28-row claim audit matrix; honest Tier-N interval witness field `decomposition_invariant_within_interval` (two-source check; no tautological contains flag).
- **Docs sweep @ `85a8224`:** manuscript section arithmetic 29 + 8 + 1 = 38 rendered; audit snapshot §8; signposting (package lists, claim-matrix pointers, CONTRIBUTING layout).
- **Gates @ `8b41085`:** 1471 collected; 1470 passed / 0 failed / 1 skipped; 95.02% `src/` coverage; 47/47 dashboard invariants; 169-page combined PDF.
- **Transient audit cleanup:** removed superseded shards `ISA_20260522_workplan_implement.md` and `ISA_20260524_gnn_fifth_track.md` from `docs/_audit/` (outcomes live in shipped code, S08, and this ledger).
- **Post-v1 thermo polish @ `86b9557`:** single-sweep `decomposition_invariants_from_points`, interval worst-λ at margin peak, `build_float_real_residual()` API cleanup, publication metadata alias consolidation — gates 1473 passed / 95.02% coverage; see [`docs/_audit/THERMO_NUCLEAR_REVIEW_2026-05-26_v1_closure.md`](docs/_audit/THERMO_NUCLEAR_REVIEW_2026-05-26_v1_closure.md) Applied section.
