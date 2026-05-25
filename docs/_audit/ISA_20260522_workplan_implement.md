---
project: actinf_policy_entanglement_lean
task: Implement the manuscript §Work plan items fully where genuinely session-completable, then remove the Work-plan framing from the manuscript without losing honest disclosure
slug: 20260522-actinf-workplan-implement
effort: E4
phase: build
progress: 5/46
mode: build
started: 2026-05-22T11:00:00-07:00
updated: 2026-05-22T11:00:00-07:00
---

# ISA — actinf_policy_entanglement_lean: Work-plan implementation + removal

## Problem

The manuscript's Discussion (`manuscript/6C_discussion_and_outlook.md`) ends with a
forward-pointing `## Work plan` of five items, cross-referenced from the abstract
(`0A`), the decomposition section (`2D`), the GNN supplement (`S08`), and `INDEX.md`.
The five items are heterogeneous in completability:

- **Item 2 (empirical extensions)** — 2a BTAI baseline (`src/simulation/btai_baseline.py`,
  372 lines, real MCTS implementation + `tests/test_btai_baseline.py`) and 2b
  adversarial-perturbation harness (`src/simulation/adversarial.py`, 288 lines, real
  implementation + `tests/test_adversarial.py`). **Both are genuinely implemented and
  unit-tested but are NOT run by `scripts/run_all.py` and emit no artifacts/VARs**, and
  the manuscript still frames them as "pre-registered" future work (4B §"Connections to
  BTAI" even calls the BTAI implementation "the gap"). This is the session-completable core.
- **Item 1a (11-row Mathlib4 discharge)** and **item 1b (Float↔ℝ formal bridge)** — the
  project's hard-won integrity record (memory `project-actinf-integrity-state`) is emphatic:
  these are genuine multi-week Lean research; a session "proof" is the documented
  recurrence-#8 laundered-fake failure mode. **MUST NOT be fabricated.**
- **Item 3 (cross-repo integration)** requires sister projects; **item 4 (community/DOI)**
  is release-time; **item 5 (GNN bridge)** is `roadmap` (S08 already scopes it thoroughly).

The user wants the work plan implemented fully and the work-plan framing removed from the
manuscript. The honest reading: ship everything genuinely doable + verify on disk; remove
the forward-pointing `## Work plan` framing; and preserve every open-residual disclosure in
the existing honest sections (Limitations / Threats to validity / Open Questions / S07
claim-strength / S08 GNN). Removing disclosure of un-done work would be concealment, the
inverse of the project's `feedback-disclosure-is-not-remediation` discipline.

## Vision

A referee opening the Discussion finds no "Work plan" section and no "pre-registered future"
framing for the BTAI/adversarial harnesses — instead those harnesses are shipped, run, and
reported with worked results and honest scope, while the genuinely-open residuals (Float↔ℝ
bridge, full Mathlib4 discharge, GNN bridge, cross-repo/community) live in Limitations and
Open Questions as the standard future-work surface of a research paper. The regression gate,
the ℝ-proof axiom audit, the dashboard/concordance/honesty pins, the advisor, and a
cross-vendor (Forge) audit all pass. Nothing is fabricated; nothing honestly-disclosed is lost.

## Out of Scope

- Fabricating or "laundering" the Float↔ℝ bridge (1b) or any of the 11 witness-row Mathlib4
  discharges (1a) — these stay honest roadmap residuals. (Recurrence-#8 guardrail.)
- Asserting an empirical *conclusion* for the BTAI head-to-head or adversarial study that a
  gated run has not actually established — graduate to "implemented + run + worked result",
  not "the hypothesis is confirmed".
- Cross-repository schema unification requiring other institute repos (item 3 beyond a local
  schema-export step), and DOI/public-URL minting (item 4) — release-time, not session work.
- Deleting open-work disclosure: the §Work plan removal must preserve every open residual in
  Limitations / Open Questions / Threats.
- Touching the verified ℝ formal core (`free_energy_decomposition_full`, the general-K kernel)
  except to re-verify it is still axiom-clean.

## Principles

- **No fabrication; verify on disk.** Every `[x]` cites a quoted artifact token (R1). Machine
  proofs are trustworthy only after I run the build + `#print axioms` + a negative control.
- **Disclosure ≠ removal.** Removing the "Work plan" framing must not remove the honest
  disclosure of open work; it relocates/preserves it. (`feedback-disclosure-is-not-remediation`.)
- **Every new gate must fail on a wrong input.** Any new VAR/validator gets a self-designed
  negative control proving non-vacuity. (`feedback-shape-tests-dont-bind-truth`.)
- **Graduate prose to match on-disk truth** — neither over-claim (assert unrun conclusions)
  nor under-claim (call implemented+tested code "a gap").
- **Run the project generator before trusting any number** (R8): the regression gate and
  `manuscript_variables`/`validate_outputs` are the oracle, not the prose about them.

## Constraints

Structural invariants pinned for every fix/delegated agent (R9):

- `scripts/regression_gate.py` must remain green (exit 0); project coverage ≥ 95% floor.
- Any MathlibProofs edit must keep `#print axioms` foundational-only (`propext`,
  `Classical.choice`, `Quot.sound`) — enforced by `scripts/build_mathlib_proofs.py` +
  `tests/test_mathlib_axiom_audit.py`. (Do not touch the ℝ core except to re-verify.)
- The manuscript renderer fails on dangling `[[SECREF:...]]` / `[[VAR:...]]` tokens — every
  removed/renamed reference must be repaired or the build breaks (this is a protective gate).
- Concordance/honesty pins must stay green: `tests/test_h1_headline_invariant.py`,
  `tests/test_witness_conformance.py`, `tests/test_mathlib_proofs_integrity.py`,
  `scripts/check_concordance.py`, plus README/abstract-agreement tests.
- Every manuscript `[[VAR:...]]` resolves from a real run via `manuscript_variables.json`;
  no hardcoded numbers (`scripts/validate_manuscript.py`).
- ISC ID-stability: never renumber on edit; splits → `ISC-N.M`; drops → tombstone.

## Goal

Implement every session-completable Work-plan item to verified completion — concretely, run
the BTAI (2a) and adversarial (2b) harnesses through new reproducible pipeline stages that
emit auditable artifacts (and, where a non-vacuous negative-control-backed gate exists, VARs),
and graduate their manuscript prose from "pre-registered future" to "shipped + run". Then
remove the `## Work plan` section and every "work plan" mention across the manuscript while
relocating the genuinely-open residuals (1a, 1b, 3, 4, 5) into Limitations / Open Questions /
Threats so no honest disclosure is lost. Done = regression gate green, ℝ-proof axiom audit
green, dangling-token gate green, advisor reviewed, Forge cross-vendor audit returns no
unaddressed critical, and the manuscript contains no forward-pointing "work plan" while
disclosing every open residual.

## Criteria

### Baseline & truth (R8/R10)
- [ ] ISC-1: `scripts/regression_gate.py` run once at OBSERVE; its real exit code + summary captured as baseline.
- [ ] ISC-2: BTAI module imports and `run_btai_scenario` executes on a worked input (real output captured).
- [ ] ISC-3: Adversarial module imports and `run_full_sweep`/`measure_drift` executes on a worked input (real output captured).
- [ ] ISC-4: Confirm on disk that no `run_all.py` stage runs btai/adversarial (grep of stage list).

### Item 2a — BTAI baseline (graduate to shipped+run)
- [ ] ISC-5: `scripts/simulate_btai.py` exists, is a thin orchestrator importing `src/simulation/btai_baseline.py`.
- [ ] ISC-6: Running it emits a deterministic sidecar `output/data/btai_baseline.json` (re-run byte-identical).
- [ ] ISC-7: Sidecar contains KL-vs-budget convergence to the closed-form Bernoulli reference posterior.
- [ ] ISC-8: Sidecar contains the fitted sample-complexity exponent across the budget grid.
- [ ] ISC-9: `scripts/simulate_btai.py` wired into `run_all.py` stage list (write-isolated).
- [ ] ISC-10: A figure artifact (`output/figures/btai_*.png`) is produced by the runner with PNG provenance metadata.
- [ ] ISC-11: Any new BTAI VAR added to `manuscript_variables` resolves from the real sidecar (no hardcode).
- [ ] ISC-12: If a BTAI gate is added to `validate_outputs.py`, a negative control proves it FAILS on a wrong value.
- [ ] ISC-13: `tests/test_btai_baseline.py` still green; new runner has ≥1 deterministic test.

### Item 2b — adversarial perturbation (graduate to shipped+run)
- [ ] ISC-14: `scripts/simulate_adversarial.py` exists, thin orchestrator importing `src/simulation/adversarial.py`.
- [ ] ISC-15: Running it emits a deterministic sidecar `output/data/adversarial_sweep.json` (re-run byte-identical).
- [ ] ISC-16: Sidecar contains the (ε,λ)-grid: measured KL drift, analytical Lipschitz bound, bound_ratio, bound_holds per scenario.
- [ ] ISC-17: Sidecar reports the empirical Lipschitz constant and the bound-holds fraction across the sweep.
- [ ] ISC-18: `scripts/simulate_adversarial.py` wired into `run_all.py` stage list (write-isolated).
- [ ] ISC-19: A figure artifact (`output/figures/adversarial_*.png`) is produced with PNG provenance metadata.
- [ ] ISC-20: Any new adversarial VAR resolves from the real sidecar (no hardcode).
- [ ] ISC-21: A discriminating gate (e.g. bound-holds fraction, or measured ≤ bound) is added with a negative control proving it FAILS when the bound is genuinely violated.
- [ ] ISC-22: `tests/test_adversarial.py` still green; new runner has ≥1 deterministic test.

### Manuscript prose graduation (truth-matching, no over/under-claim)
- [ ] ISC-23: 4B §"Connections to BTAI" rewritten: BTAI implementation is shipped+tested+run, not "the gap".
- [ ] ISC-24: 4B gains an honest worked-result line for BTAI (convergence/exponent) with explicit scope (full compute-matched study still scoped).
- [ ] ISC-25: 4B gains an honest worked-result line for the adversarial sweep (bound-holds, empirical Lipschitz) with scope.
- [ ] ISC-26: No graduated sentence asserts a head-to-head *conclusion* not established by the gated run (advisor-checked).

### Work-plan removal + residual preservation
- [ ] ISC-27: `## Work plan` section removed from `6C_discussion_and_outlook.md`.
- [ ] ISC-28: 6C title no longer contains "Work Plan".
- [ ] ISC-29: 6C prose mentions "Work plan item 1" / "the work plan" / "pre-registered in the work plan" removed or rephrased to Limitations/Open-Questions framing.
- [ ] ISC-30: 0A abstract "pre-registered as Work plan item 1(b)" rephrased — Float↔ℝ bridge still disclosed as the open residual (no concealment).
- [ ] ISC-31: 2D "Work plan item 1(b) … item 1(a)" rephrased to a Limitations/Open-Questions pointer; both residuals still disclosed.
- [ ] ISC-32: S08 "Work Plan item 5" / "Integration with the Discussion Work Plan" rephrased to point at Open Questions / Limitations (GNN still `roadmap`).
- [ ] ISC-33: `INDEX.md:37` "and Work Plan" updated.
- [ ] ISC-34: Float↔ℝ bridge (1b) disclosed in §Limitations or §Threats after removal (verify present).
- [ ] ISC-35: Mathlib4 11-row discharge (1a) disclosed in §Open Questions (6B Q14 already) — verify still pointed-to.
- [ ] ISC-36: GNN bridge (item 5) residual preserved (S08 + an Open-Questions pointer).
- [ ] ISC-37: cross-repo (3) + community/DOI (4) residuals preserved in Limitations/Threats.

### Integrity / no-fabrication anti-criteria
- [ ] ISC-38: Anti: NO new Lean proof of the Float↔ℝ bridge or the 11 witness rows is added/claimed this session.
- [ ] ISC-39: Anti: NO manuscript sentence claims an item is "done"/"closed"/"verified" that is not artifact-backed on disk.
- [ ] ISC-40: Anti: NO open residual silently disappears — every removed work-plan item is traceable to a surviving honest disclosure.
- [ ] ISC-41: Anti: NO new gate is vacuous — each has a negative control that fails on a wrong input.
- [ ] ISC-42: Anti: the verified ℝ core (`free_energy_decomposition_full`, general-K kernel) `#print axioms` stays foundational-only (re-verified).

### Final verification
- [ ] ISC-43: `scripts/regression_gate.py` green after all edits (exit 0, coverage ≥ floor).
- [ ] ISC-44: Manuscript renders with zero dangling `[[SECREF]]`/`[[VAR]]` tokens (validate_manuscript / build).
- [ ] ISC-45: Advisor invoked on the final artifact set (HARD at E4); findings addressed or logged.
- [ ] ISC-46: Forge cross-vendor audit (read-only) returns no unaddressed critical (R2a).

## Test Strategy

| isc | type | check | threshold | tool |
|-----|------|-------|-----------|------|
| ISC-1 | command | regression_gate exit code captured | exit recorded | Bash |
| ISC-6 | command | sidecar emitted, re-run diff empty | byte-identical | Bash + diff |
| ISC-12,21 | negative-control | gate FAILS on a wrong value | non-zero exit on bad input | Bash |
| ISC-27..33 | grep | "work plan" mentions removed/rephrased | 0 forward-pointing work-plan refs | Grep |
| ISC-34..37 | grep | residual still disclosed | ≥1 surviving mention each | Grep |
| ISC-42 | command | `#print axioms` foundational-only | only propext/Classical.choice/Quot.sound | build_mathlib_proofs |
| ISC-43 | command | full regression gate | exit 0 | regression_gate.py |
| ISC-44 | command | render/validate manuscript | 0 dangling tokens | validate_manuscript.py |
| ISC-45 | advisor | Inference.ts --mode advisor | logged | Inference.ts |
| ISC-46 | cross-vendor | Forge read-only audit | no unaddressed critical | Agent(Forge) |

## Features

| name | satisfies | depends_on | parallelizable |
|------|-----------|------------|----------------|
| baseline+truth | ISC-1..4 | — | no (first) |
| btai-stage | ISC-5..13 | baseline | yes (vs adversarial) |
| adversarial-stage | ISC-14..22 | baseline | yes (vs btai) |
| prose-graduation | ISC-23..26 | btai-stage, adversarial-stage | no |
| workplan-removal | ISC-27..37 | prose-graduation | no |
| integrity-gates | ISC-38..42 | all | no |
| final-verify | ISC-43..46 | all | no (last) |

## Decisions

- 2026-05-22: effort E4 (classifier timed out → fail-safe E3; escalated via context-override: integrity-critical, cross-cutting Lean/Python/manuscript, demands advisor + cross-vendor audit, user said "comprehensively/ultrathink"). `effort_source: context-override`.
- 2026-05-22: Items 1a/1b/3/4/5 classified NOT session-completable per the project's durable integrity record; honest residual treatment, NOT fabrication. This is the load-bearing scope decision.
- 2026-05-22: "Remove the work plan mention" executed as remove-framing + preserve-disclosure (relocate residuals to Limitations/Open-Questions), NOT delete-and-conceal.

## Changelog

(to be appended at LEARN)

## Verification

(to be appended at EXECUTE/VERIFY with quoted artifact tokens)
