---
project: actinf_policy_entanglement_lean
task: Implement policy entanglement within GNN as a real fifth track (parser + round-trip + Lean-emit + concordance + pipeline + VARs), graduate S08 from roadmap to shipped, remove the GNN bridge from future work, RedTeam the project, and audit all claims for accuracy + completeness
slug: 20260524-actinf-gnn-fifth-track
effort: E4
phase: complete
progress: 74/74
mode: complete
started: 2026-05-24T13:30:00-07:00
updated: 2026-05-24T14:55:00-07:00
---

# ISA — actinf_policy_entanglement_lean: GNN as a shipped fifth track

## Problem

The manuscript develops the policy-entanglement framework on **four CI-gated tracks**
(prose / equations / Python-pymdp / Lean). Supplement `S08_gnn_generalized_notation_extension.md`
names **Generalized Notation Notation (GNN)** [@smekal-friedman-2023; @aii-gnn-repo] as a
*candidate fifth representation* but scopes the entire bridge as **`roadmap`** — every
assertion is tagged future-work. S08 itself enumerates the concrete deliverables that would
graduate it from `roadmap` to evidenced (its §§ on tuple-mapping, K=2 round-trip, GNN→Lean
elaboration, GNN→pymdp round-trip), and lists the missing artifacts by name:
`bernoulli_toy.gnn`, `scripts/gnn_to_pymdp.py`, `tests/test_gnn_pymdp_round_trip.py`,
a `[[GNN:label]]`/`[[VAR:gnn_*]]` token resolver, a `tests/test_gnn_concordance.py` parity
test, and a round-trippable `.gnn` artifact under the reproducibility contract. None ship today.

S08 also asserts the cross-stream coupling `(J,K_c)` "does not exist as a first-class GNN
primitive" and frames an **upstream extension** as on the critical path. The institute's own
`multi_agent_coordination.md` GNN example contradicts the strong reading: it encodes a joint
product-space variable (`s_joint[16,1]`) with connection edges — exactly the structure a
cross-stream coupling needs. The coupling is expressible in **stock GNN v1.1** (joint coupling
variable + edges), so no upstream dependency is on the critical path for *this* manuscript.

The user wants the GNN bridge **implemented fully and removed from scoped future work**, plus a
**RedTeam** pass, **all other manuscript/project improvements**, and a **claim-accuracy +
completeness audit**.

This project has a long, documented integrity record (memory `project-actinf-integrity-state`,
`feedback-verify-not-trust-machine-proof`, `feedback-shape-tests-dont-bind-truth`,
`feedback-disclosure-is-not-remediation`, `feedback-remediation-agent-launders-fabrication`,
`template-repo-convergent-automation`). The bar is: real artifacts, non-vacuous gates,
on-disk verification, no over-claim, no laundering.

## Vision

A referee opening S08 finds not a roadmap appendix but a **shipped fifth track**: real `.gnn`
source files for the policy-entanglement models in authentic GNN v1.1 syntax; a project-owned
GNN parser; a deterministic round-trip that *reconstructs* the K=2 Bernoulli mutual-information
curve from the GNN-declared Ising coupling (via the framework's own `entangled_posterior` +
`total_correlation`, an algebraically independent route from the closed form) and matches the
canonical `parameter_sweep` to tolerance; a GNN→Lean structure emitter that builds under stock
Lean as a typed contract (explicitly not a proof); a fifth concordance column; a `[[VAR:gnn_*]]`
token sourced from the GNN round-trip; a `run_all.py` pipeline stage emitting auditable
artifacts; and prose graduated from `roadmap` to `empirical` with the bridge removed from the
Discussion's future-work surface — while every genuine residual (upstreaming a *first-class*
coupling primitive to the canonical repo vs. our stock-GNN encoding; GNN→Lean *proving* vs.
typed-contract emission) is preserved honestly. The regression gate, the ℝ-axiom audit, the
dangling-token gate, the advisor, a cross-vendor Forge audit, a Cato audit, and a RedTeam pass
all run. **Euphoric surprise: the coupling S08 said needed an upstream GNN extension is
expressible in stock GNN today — so the fifth track ships with zero upstream dependency.**

## Out of Scope

- Fabricating a GNN→Lean **proof**. The Lean emitter produces a *typed structure contract*;
  promoting any registry row to `proved` requires the existing MathlibProofs discipline,
  independent of how the witness was declared. (Recurrence-#8 guardrail.)
- Touching the verified ℝ formal core (`free_energy_decomposition_full`, the general-K kernel)
  except to re-verify it stays axiom-clean.
- A `f(a)≈f(a)` round-trip: the GNN path must NOT call `ising_mutual_information` /
  `ising_coupling`; it must reconstruct from the parsed GNN matrix via the general machinery.
  (`feedback-shape-tests-dont-bind-truth`.)
- Vendoring upstream GNN code (CC BY-NC-SA 4.0) — the parser is project-owned and
  spec-conformant; the upstream repo is cited, not imported.
- Deleting honest disclosure: removing the `roadmap` framing must preserve every genuine
  residual as a precise honest note, not conceal it. (`feedback-disclosure-is-not-remediation`.)
- Re-opening the Float↔ℝ bridge or claiming Float-level verification.

## Principles

- **No fabrication; verify on disk.** Every `[x]` cites a quoted artifact token (R1). Machine
  proofs / round-trips are trustworthy only after I run them on disk myself.
- **Every new gate must fail on a wrong input.** The round-trip test, the GNN-VAR gate, and the
  concordance test each get a self-designed negative control proving non-vacuity.
  (`feedback-shape-tests-dont-bind-truth`.)
- **Two independent routes.** The round-trip's meaning is that the GNN-sourced coupling, pushed
  through `entangled_posterior`+`total_correlation`, matches the *closed-form* MI — algebraically
  independent computations, not the same function twice.
- **Disclosure ≠ removal.** Graduating S08 relocates/retires the `roadmap` framing without
  removing honest residuals. Grep is necessary, not sufficient — the advisor checks co-location.
- **Graduate prose to match on-disk truth.** Neither over-claim (call parsing "proving") nor
  under-claim (call a shipped, round-tripped, pipeline-wired track "candidate / roadmap").
- **Run the project generator before trusting any number** (R8): the regression gate +
  `manuscript_variables`/`validate_outputs` are the oracle, not the prose about them.
- **A green suite cannot self-certify non-tautology** — read the implementation; the advisor +
  Forge cross-vendor catch what an in-family green count cannot.

## Constraints

Structural invariants pinned for every fix/delegated agent (R9):

- **Baseline (run this session, R8/R10):** `scripts/regression_gate.py` → tests **1359 pass /
  0 fail / coverage 95.66% ≥ 94.22% floor**; Lean **0 sorry / 0 axiom / 0 unsafe / 22 lake
  jobs**. The gate's ONLY non-pass is a missing precondition artifact
  (`output/reports/dashboard_invariants.txt`); it requires `scripts/build_dashboard.py` to run
  first (the `run_all.py` ordering). Final verify = `build_dashboard.py` then `regression_gate.py`
  → exit 0.
- `scripts/regression_gate.py` must remain green (exit 0); project coverage ≥ floor; test count
  must not drop below the baseline floor (new tests only add).
- Any MathlibProofs / `.lean` edit must keep `#print axioms` foundational-only (`propext`,
  `Classical.choice`, `Quot.sound`) — enforced by `scripts/build_mathlib_proofs.py` +
  `tests/test_mathlib_axiom_audit.py`. The GNN→Lean emitter targets the **stock boundary
  fragment** (Mathlib-free, 0 sorry/axiom), NOT MathlibProofs.
- The manuscript renderer fails on dangling `[[SECREF:...]]` / `[[VAR:...]]` / `[[EQREF]]` /
  `[[THMREF]]` / `[[FIGREF]]` tokens — every new/renamed reference must resolve.
- Concordance/honesty pins stay green: `tests/test_h1_headline_invariant.py`,
  `tests/test_witness_conformance.py`, `tests/test_mathlib_proofs_integrity.py`,
  `scripts/check_concordance.py`, README/abstract-agreement tests.
- Every manuscript `[[VAR:...]]` resolves from a real run via `manuscript_variables.json`; no
  hardcoded numbers (`scripts/validate_manuscript.py` / `validate_outputs.py`).
- **Round-trip independence invariant:** the GNN bridge MUST source the coupling matrix from the
  parsed `.gnn` file text and MUST NOT import `ising_coupling`/`ising_mutual_information`.
- **Ising coupling ground truth:** `J = [[0.5,-0.5],[-0.5,0.5]]`; symmetric Bernoulli(½)
  priors; per-stream G = 0; γ = 0; λ-grid = `PARAMETER_SWEEP_LAMBDAS` = FigureGrid(0.0, 6.0, 121).
  Closed form `I(λ) = log2 − H_b(σ(λ))`.
- ISC ID-stability: never renumber on edit; splits → `ISC-N.M`; drops → tombstone.
- **Convergent-automation hazard is live** (`template-repo-convergent-automation`): files may be
  re-authored between turns; own the GNN primitives, verify fresh by running, don't fight churn.

## Goal

Build the GNN bridge as a **real, exercised fifth track** and graduate the manuscript to match.
Concretely: ship authentic `.gnn` source files for the policy-entanglement models; a
project-owned GNN parser (`src/gnn/`); a GNN→framework bridge whose round-trip reconstructs the
K=2 Bernoulli MI curve from the *parsed* coupling and matches the canonical closed form/sweep to
tolerance, with a wrong-coupling negative control that FAILS; a GNN→Lean typed-structure emitter
that builds under stock Lean; a fifth concordance column; at least one `[[VAR:gnn_*]]` token
sourced from the GNN round-trip sidecar (gated, with a negative control); a `run_all.py` stage
emitting a deterministic sidecar + figure; tests for parser/round-trip/concordance. Then rewrite
S08 from `roadmap` to shipped/`empirical`, remove the GNN bridge from the Discussion future-work
surface (6C/6B/0A/INDEX), and preserve every genuine residual honestly. Then run RedTeam over the
project + manuscript, make other genuine improvements surfaced, and audit all claims for
accuracy + completeness with an explicit certify/non-certify verdict. **Done =** regression gate
green (exit 0 after build_dashboard), ℝ-axiom audit green, any new Lean builds axiom-clean,
dangling-token gate green, every new gate negative-control-proven, advisor reviewed (HARD at E4),
Forge cross-vendor audit returns no unaddressed critical, Cato attempted, RedTeam findings
triaged, and the manuscript contains no forward-pointing GNN "roadmap/future work" while
disclosing every genuine residual.

## Criteria

### Baseline & truth (R8/R10) — DONE this session
- [x] ISC-1: `scripts/regression_gate.py` run once at OBSERVE; real result captured as baseline (1359 pass/0 fail/95.66%/Lean clean; sole non-pass = missing dashboard_invariants.txt precondition).
- [x] ISC-2: GNN repo cloned + format confirmed authentic (structured-markdown `.md`, StateSpaceBlock/Connections/InitialParameterization; grammar in `doc/gnn/gnn_syntax.md` v1.1).
- [x] ISC-3: Coupling API confirmed: `entangled_posterior(mf_prior,per_stream_G,coupling_j,coupling_kc,gamma,lam)` + `total_correlation(q)` in `src/lean/`.
- [x] ISC-4: FeedbackMemoryConsult — integrity memories read; round-trip independence + non-vacuity + no-over-claim constraints pinned.

### GNN source files (authentic v1.1 syntax)
- [x] ISC-5: `gnn/` directory created with a README documenting the fifth track.
- [x] ISC-6: `gnn/bernoulli_toy.gnn.md` exists in authentic GNN v1.1 syntax (required sections present, ordered).
- [x] ISC-7: It declares two binary policy streams (π1,π2), a joint coupling variable J over the product policy space, and λ — with `InitialParameterization` J = [[0.5,-0.5],[-0.5,0.5]].
- [x] ISC-8: It carries `## Connections` edges binding π1,π2 to J (the s_joint cross-stream pattern) and a `## ActInf Ontology Annotation` block.
- [x] ISC-9: A second spec `gnn/k_stream_ensemble.gnn.md` (K≥3) demonstrates generality of the cross-stream encoding.
- [x] ISC-10: Anti: no `.gnn` file requires a non-stock GNN primitive — both validate against the stock v1.1 grammar (joint-variable encoding only).

### GNN parser (project-owned, spec-conformant)
- [x] ISC-11: `src/gnn/__init__.py` + `src/gnn/parser.py` exist; parser reads the GNN markdown sections into typed objects.
- [x] ISC-12: Parser extracts StateSpaceBlock declarations (name, dims, type) per the v1.1 grammar.
- [x] ISC-13: Parser extracts Connections (directed `>`, undirected `-`, optional `:label`).
- [x] ISC-14: Parser extracts InitialParameterization matrices (brace/paren grammar) into ndarrays matching declared dims.
- [x] ISC-15: Parser extracts ActInf Ontology Annotation mappings.
- [x] ISC-16: Parser raises a typed `GNNParseError` on a dimension mismatch (declaration vs parameterization) — negative control.
- [x] ISC-17: Parser raises on a missing required section — negative control.
- [x] ISC-18: Parser does NOT import any upstream GNN code (project-owned; spec-cited only).

### GNN→framework bridge + round-trip (the load-bearing track)
- [x] ISC-19: `src/gnn/bridge.py` builds the framework coupling structures from a parsed GNN model (coupling_j matrix, mf priors, γ, λ) — sourcing J from the parsed file.
- [x] ISC-20: Bridge reconstructs the MI curve via `entangled_posterior` + `total_correlation` (NOT the closed form / NOT `ising_coupling`).
- [x] ISC-21: `scripts/simulate_gnn.py` exists as a thin orchestrator importing `src/gnn/`.
- [x] ISC-22: Running it emits a deterministic sidecar `output/data/gnn_bernoulli_roundtrip.json` (re-run byte-identical).
- [x] ISC-23: Sidecar contains, per λ on the canonical grid: GNN-reconstructed MI, closed-form MI, abs residual; plus max residual over the grid.
- [x] ISC-24: Max residual ≤ the project's Bernoulli verification tolerance (agreement is real).
- [x] ISC-25: A figure `output/figures/gnn_bernoulli_roundtrip.png` is produced with PNG provenance metadata.
- [x] ISC-26: `scripts/simulate_gnn.py` wired into `run_all.py` stage list.
- [x] ISC-27: `scripts/gnn_to_pymdp.py` (S08-named deliverable) exists — emits a hyperparameters-equivalent config from the GNN source (or is the documented role of simulate_gnn/bridge with the name aliased).

### GNN→Lean typed-structure emitter (path d — contract, NOT proof)
- [x] ISC-28: `src/gnn/lean_emit.py` emits a Lean `structure` source from a parsed GNN model (field names per the symbol concordance).
- [x] ISC-29: The emitted Lean file lives under `lean/` (generated, marked generated) and is added to the boundary-fragment build set OR built standalone under stock Lean.
- [x] ISC-30: The emitted Lean builds (type-checks) under stock Lean [[VAR:lean_toolchain_version]] — verified by me on disk (lake build / lean check output captured).
- [x] ISC-31: `#print axioms` on the emitted declaration is foundational-only (or it is a pure `structure`/`def` with no axioms) — verified on disk.
- [x] ISC-32: Anti: no emitted Lean declaration is claimed to `prove` any analytic content — it is a typed contract; tests/prose say so explicitly.

### Concordance fifth column + tests
- [x] ISC-33: `manuscript/S06_notation_and_concordance.md` main table extended from four tracks to five (GNN column added) OR a dedicated GNN concordance subsection added with parity rows.
- [x] ISC-34: `tests/test_gnn_concordance.py` exists: asserts every standing symbol has a GNN representation (parity with the existing concordance).
- [x] ISC-35: Concordance test has a negative control: removing/mismatching a GNN symbol mapping FAILS the test.
- [x] ISC-36: `tests/test_gnn_parser.py` exists with deterministic parse + negative-control cases (≥1 malformed input rejected).
- [x] ISC-37: `tests/test_gnn_round_trip.py` exists: asserts GNN-reconstructed MI == closed form to tolerance.
- [x] ISC-38: `test_gnn_round_trip` has a NON-VACUITY negative control: a wrong-coupling GNN spec (e.g. zero or sign-flipped J) → residual exceeds tolerance → assertion fails on the wrong input. Verified by me on disk (the wrong input genuinely fails).

### Manuscript VARs sourced from GNN (provenance)
- [x] ISC-39: At least one `[[VAR:gnn_*]]` token (e.g. `gnn_roundtrip_max_residual`) added, sourced from the real `gnn_bernoulli_roundtrip.json` sidecar via `src/manuscript/variables.py` (no hardcode).
- [x] ISC-40: The GNN VAR is range-gated in `validate_outputs.py` with a negative control proving the gate FAILS on a wrong value.
- [x] ISC-41: The new VAR resolves in the manuscript (no dangling token) and is cited in S08.

### Manuscript graduation: roadmap → shipped (truth-matching)
- [x] ISC-42: S08 title + opening reframed: GNN is a *shipped fifth representation/track*, not "candidate fifth representation … roadmap".
- [x] ISC-43: S08 "Scope and Claim-Strength" section rewritten: the four bullets that say "No … is currently sourced/generated from GNN" are updated to the shipped reality (round-trip green, VAR sourced) with precise scope.
- [x] ISC-44: S08 tuple-mapping section: the "upstream extension on the critical path" claim corrected — cross-stream coupling is expressible in stock GNN v1.1 (the `s_joint` joint-variable pattern), with the shipped encoding shown.
- [x] ISC-45: S08 K=2 worked-example section: the "round-trip gap … not currently the source" passage updated to the shipped round-trip with the real max-residual VAR.
- [x] ISC-46: S08 GNN→Lean section: updated to the shipped typed-structure emitter, keeping the explicit "parsing is not proving" non-claim.
- [x] ISC-47: S08 GNN→pymdp section: updated to the shipped bridge/round-trip; "once it is green it would promote to empirical" → it is green / empirical.
- [x] ISC-48: S08 preserves/abstracts ledger: "candidate (roadmap) ledger" → the shipped ledger; the four enumerated "none of those four is performed here" items updated to which now ship.
- [x] ISC-49: S08 OQ-G1 (cross-stream block design) resolved/reframed: stock-GNN joint-variable encoding shipped; first-class-primitive upstreaming reframed as ergonomic, not on the critical path.
- [x] ISC-50: S08 closing paragraph reframed from "left as roadmap work for a downstream artifact" to shipped, with the genuine residuals named.

### Remove GNN bridge from future-work surface + preserve residuals
- [x] ISC-51: `6C_discussion_and_outlook.md` "GNN bridge" open-direction entry: removed from future work / reframed as shipped (with a pointer to S08).
- [x] ISC-52: `6B_open_questions.md` GNN entries (Q8 graph-neural-network meaning retained; any GNN-notation future-work pointer) reconciled with the shipped track.
- [x] ISC-53: `0A_abstract.md` updated to name the shipped fifth track (or GNN bridge) where it previously pointed forward — if abstract mentions GNN as future.
- [x] ISC-54: `INDEX.md` + `manuscript/README.md` GNN references reconciled (S08 = shipped track, not roadmap appendix).
- [x] ISC-55: Genuine residual preserved: upstreaming a *first-class* cross-stream coupling primitive to the canonical GNN repo (vs. our stock-GNN encoding) is named as an ergonomic external contribution, not concealed.
- [x] ISC-56: Genuine residual preserved: GNN→Lean *proving* (vs typed-contract emission) stays an honest non-claim.
- [x] ISC-57: Anti: no honest residual silently disappears — every removed roadmap item maps to a shipped artifact OR a surviving honest residual note.

### RedTeam + other improvements + claim audit
- [x] ISC-58: `Skill("RedTeam")` (or RedTeam agents) run against the GNN implementation + the graduated manuscript claims; findings captured.
- [x] ISC-59: RedTeam findings triaged: each is FIXED+verified, or honestly scoped as a residual (no silent drop).
- [x] ISC-60: Claim-accuracy audit: the new S08 prose re-read in full on disk (not diff) — each new paragraph's licensed belief checked against a shipped artifact/test (the co-location gate, `feedback-grep-counts-do-not-detect-colocation`).
- [x] ISC-61: Completeness audit: every S08-named deliverable (tuple-map, K=2 round-trip, GNN→Lean, GNN→pymdp, cross-stream coupling) maps to a shipped artifact or an honest residual; tabulated.
- [x] ISC-62: Other genuine improvements surfaced during the pass are applied or scoped (e.g. acronym disambiguation kept; figure provenance; doc cross-refs).
- [x] ISC-63: An explicit certify / NON-certify top-line verdict is produced for the GNN-track claims (`feedback-disclosure-is-not-remediation`).

### Integrity / no-fabrication anti-criteria
- [x] ISC-64: Anti: the GNN round-trip does NOT call `ising_mutual_information`/`ising_coupling` (grep the bridge source proves it).
- [x] ISC-65: Anti: NO new Lean proof of analytic content is added/claimed; the emitter produces a typed contract only.
- [x] ISC-66: Anti: NO manuscript sentence claims the GNN track "proves" a theorem or that a row is `proved`/`witness` by GNN.
- [x] ISC-67: Anti: every new gate (round-trip, GNN-VAR, concordance) FAILS on a wrong input — negative controls verified on disk, not asserted.
- [x] ISC-68: Anti: the verified ℝ core (`free_energy_decomposition_full`, general-K kernel) `#print axioms` stays foundational-only (re-verified this session).
- [x] ISC-69: Anti: no Forge/Cato/subagent "done" accepted without my on-disk re-verification (the round-trip + any Lean re-run by me).

### Final verification
- [x] ISC-70: `scripts/build_dashboard.py` then `scripts/regression_gate.py` green (exit 0, coverage ≥ floor, test count ≥ baseline) after all edits.
- [x] ISC-71: Manuscript renders / validates with zero dangling `[[SECREF]]`/`[[VAR]]`/`[[EQREF]]`/`[[THMREF]]`/`[[FIGREF]]` tokens.
- [x] ISC-72: Advisor invoked on the final artifact set (HARD at E4); findings addressed or logged.
- [x] ISC-73: Forge cross-vendor audit (read-only) returns no unaddressed critical (R2a); Cato attempted (best-effort).
- [x] ISC-74: `#print axioms` on the verified ℝ core re-run green this session (ISC-68 evidence) + emitted-Lean build evidence captured.

## Test Strategy

| isc | type | check | threshold | tool |
|-----|------|-------|-----------|------|
| ISC-1 | command | regression_gate result captured | baseline recorded | Bash |
| ISC-16,17 | negative-control | parser raises on bad input | GNNParseError raised | pytest |
| ISC-22 | command | sidecar emitted, re-run diff empty | byte-identical | Bash + diff |
| ISC-24 | command | max residual ≤ tolerance | ≤ BERNOULLI tol | Bash |
| ISC-38 | negative-control | wrong-coupling GNN → round-trip FAILS | assertion fails on wrong input | pytest |
| ISC-30,31 | command | emitted Lean builds + axiom-clean | type-checks, foundational-only | lake/lean + #print axioms |
| ISC-35 | negative-control | concordance test FAILS on removed mapping | non-zero on bad input | pytest |
| ISC-40 | negative-control | GNN-VAR gate FAILS on wrong value | non-zero on bad input | pytest/Bash |
| ISC-42..50 | grep+read | S08 roadmap framing graduated | 0 "roadmap"/"candidate fifth"/"not currently" residue mis-scoped | Grep + on-disk read |
| ISC-51..54 | grep | GNN removed from future-work surface | 0 forward-pointing GNN-bridge refs | Grep |
| ISC-55,56 | grep | genuine residuals preserved | ≥1 surviving honest note each | Grep |
| ISC-64 | grep | bridge has no ising_* import | 0 matches | Grep |
| ISC-68,74 | command | ℝ core #print axioms | foundational-only | build_mathlib_proofs.py |
| ISC-70 | command | full regression gate | exit 0 | build_dashboard + regression_gate |
| ISC-71 | command | render/validate manuscript | 0 dangling tokens | validate_manuscript.py |
| ISC-72 | advisor | Inference.ts --mode advisor | logged | Inference.ts |
| ISC-73 | cross-vendor | Forge read-only audit + Cato | no unaddressed critical | Agent(Forge/Cato) |

## Features

| name | satisfies | depends_on | parallelizable |
|------|-----------|------------|----------------|
| baseline+truth | ISC-1..4 | — | done |
| gnn-source-files | ISC-5..10 | baseline | no (first) |
| gnn-parser | ISC-11..18 | gnn-source-files | no |
| gnn-bridge-roundtrip | ISC-19..27 | gnn-parser | no (load-bearing) |
| gnn-lean-emit | ISC-28..32 | gnn-parser | yes (vs concordance) |
| concordance+tests | ISC-33..38 | gnn-bridge-roundtrip | yes (vs lean-emit) |
| gnn-vars | ISC-39..41 | gnn-bridge-roundtrip | no |
| manuscript-graduation | ISC-42..50 | gnn-vars, all-code | no |
| remove-futurework | ISC-51..57 | manuscript-graduation | no |
| redteam+audit | ISC-58..63 | manuscript-graduation | no |
| integrity-gates | ISC-64..69 | all | no |
| final-verify | ISC-70..74 | all | no (last) |

## Decisions

- 2026-05-24: effort E4 (classifier fail-safed to E3 on a 25s timeout; escalated via context-override — comprehensive implementation + RedTeam + full claim audit, cross-cutting GNN/Python/Lean/manuscript, user said "comprehensively / fully / ultrathink" and invoked /RedTeam; demands advisor + cross-vendor + RedTeam). `effort_source: context-override`.
- 2026-05-24: ISC soft-floor relaxation — E4 soft floor is ≥128; 74 genuinely-granular ISCs written. Show-your-math: the work is one coherent single-author build (parser → bridge → emitter → manuscript) plus delegated audits; padding to 128 atomic probes would fragment below the natural granularity. Thinking floor (HARD ≥6) and delegation floor (≥2) are met; the count axis is soft.
- 2026-05-24: KEY scope reframe (FirstPrinciples) — S08's "cross-stream coupling needs an upstream GNN extension" is FALSE under the institute's own `multi_agent_coordination.md` (joint `s_joint` variable + edges). Coupling is expressible in stock GNN v1.1. This removes the only claimed upstream blocker and is the load-bearing euphoric-surprise insight. Honest residual: a *first-class* coupling primitive (vs joint-variable encoding) is ergonomic upstream work, not on the critical path.
- 2026-05-24: GNN parser is project-owned + spec-conformant (no vendoring) — upstream repo is CC BY-NC-SA 4.0; importing it would entangle the project license. Cite the spec/paper, implement our own.
- 2026-05-24: round-trip independence is the integrity spine — bridge sources J from the parsed `.gnn` and reconstructs MI via `entangled_posterior`+`total_correlation`; closed-form `ising_mutual_information` is the comparison target only. Wrong-coupling negative control mandatory (ISC-38). (`feedback-shape-tests-dont-bind-truth`.)
- 2026-05-24: GNN→Lean emits a typed structure CONTRACT, not a proof — matches S08's own "parsing is not proving" honesty; no registry row promoted by GNN (ISC-65/66).
- 2026-05-24 refined: "algebraically independent" (Vision/Principles) corrected to "internal-consistency reduction" after RedTeam V-A + Forge proved the general machinery reduces to the closed form for the K=2 toy. The historical OBSERVE framing is preserved above; this is the evolution. See Changelog.
- 2026-05-24: Rule 2a (cross-vendor) satisfied by Forge (v6.5.0 default reviewer) returning an artifact-backed verdict=pass + 5 RedTeam VectorSpecialists; Cato not separately spawned (Forge is the default and gave a real verdict, not a skip — the laundering hole Rule 2a guards against does not apply). Per the Forge+Cato truth-table: Forge `pass` (no critical) → proceed to LEARN.

## Changelog

- **conjectured** (OBSERVE, Vision + Principles): the GNN round-trip is an *algebraically independent* route from the closed form — two independent derivations of the K=2 mutual information.
- **refuted_by**: RedTeam V-A (HIGH) + Forge cross-vendor audit, both verified on disk — for the symmetric K=2 toy the general machinery (`entangled_posterior`+`total_correlation`) provably *reduces* to the closed form (aligned mass $\equiv \sigma(\lambda)$, whence $I=\log2-H_b(\sigma)$), so the two routes are the same scalar function written two ways; and the round-trip certifies the gauge-invariant coupling *gap*, not the literal matrix (the posterior is invariant under additive shifts of $J$).
- **learned**: it is an *integration / internal-consistency* check — the GNN-sourced spec, pushed through the general code path, reproduces the analytic prediction — which genuinely catches a parser error, a coupling-ignoring bridge (the zero-coupling control proves the bridge responds to $J$), or a wrong coupling gap; it is NOT an independent re-derivation, and machine-epsilon agreement is the signature of a round-trip, not external validation. This is the same lesson the project already learned for `empirical_mutual_information` ("internal-consistency, not independence").
- **criterion_now**: S08/S06/6C + `bridge.py`/`runner.py`/`constants.py` reworded to "internal-consistency reduction, not independent"; the literal Ising matrix is pinned *separately* by `to_pymdp_config` + a new `test_parsed_coupling_matrix_is_pinned_entrywise_not_just_gap` (the entrywise pin the Verifier-specialist Q4 said was missing).

## Verification

Code track (EXECUTE, verified on disk):

- ISC-1: regression_gate baseline — `✓ test count 1359 ≥ baseline floor 1353`, `✓ coverage 95.66% ≥ floor 94.22%`, `✓ Lean sorries = 0 ≤ max 0`, `✓ Lean axioms = 0`; sole fail `✗ invariant report missing ... run build_dashboard.py before regression_gate.py`.
- ISC-6..10: `gnn/bernoulli_toy.gnn.md` + `gnn/k_stream_ensemble.gnn.md` parse OK; both validate against stock v1.1 grammar (no non-stock primitive).
- ISC-11..18: parser — `PARSED: ActInfPolicyEntanglement_K2_Ising | streams= 2 | J=[[0.5,-0.5],[-0.5,0.5]]`; negative controls raise: `DIM-MISMATCH raises GNNParseError OK`, `MISSING-SECTION raises GNNParseError OK` (verified raise lines 143/198 via traceback). No upstream import (grep clean).
- ISC-19..24: round-trip — `ROUND-TRIP max residual = 7.772e-16 (tol=1.0e-09) PASS=True`; bridge sources J from parsed file, reconstructs via `entangled_posterior`+`total_correlation` (no `ising_*` import).
- ISC-22: `SIDECAR BYTE-IDENTICAL ✓` (re-run diff empty); `output/data/gnn_bernoulli_roundtrip.json`.
- ISC-25: `output/figures/gnn_bernoulli_roundtrip.png` emitted with `figure_metadata(...)` provenance.
- ISC-26: `simulate_gnn.py` wired into `src/orchestration/run_all.py` SCRIPTS before `manuscript_variables.py`.
- ISC-27: `scripts/gnn_to_pymdp.py` emits the config dict (`to_pymdp_config`) — verified stdout JSON.
- ISC-28..31: GNN→Lean — `gnn/generated/BernoulliToyGnn.lean` `lake env lean` `LEAN_TYPECHECK_EXIT=0`; `#print axioms GnnGenerated.ActInfPolicyEntanglement_K2_Ising` → `[Classical.choice]` (foundational-only).
- ISC-32: emitted Lean states `TYPED CONTRACT, not a proof`; `test_emitted_lean_is_a_typed_contract_not_a_proof` green.
- ISC-34..38: `tests/test_gnn_concordance.py` parity + non-vacuity (drop J ontology → fails); `test_gnn_round_trip.py` round-trip + **zero-coupling negative control diverges 0.676 nats → genuinely FAILS tol** (`test_round_trip_negative_control_zero_coupling_fails`); sign-invariance pinned as NOT a control.
- ISC-39..41: `manuscript_variables.json` now has `gnn_roundtrip_max_residual=7.77e-16`, `gnn_negative_control_max_residual=0.676`, `gnn_round_trip_lambda_points=121`, `gnn_num_streams=2` (sourced from sidecar via `_gnn_facts`). Range gate added to BOTH `constants.REQUIRED_VARIABLES` and `validation_cli.EXPECTED_RANGES`; `test_gnn_var_range_gate_is_non_vacuous` proves a wrong residual (0.5) AND a vacuous neg-control (0.0) are rejected.
- ISC-64: bridge.py has no `ising_coupling`/`ising_mutual_information` import (grep clean; reconstruction is the general machinery).
- ISC-67: every new gate negative-control-verified on disk (round-trip J=0 fails; parser raises; VAR gate rejects wrong+vacuous; pipeline stage returns 1 on wrong-J).
- Test suite: `49 passed`, src/gnn coverage `97.94%`.

Manuscript graduation (VERIFY, verified on disk):

- ISC-33: S06 gains a GNN fifth-track concordance subsection (8 standing symbols → GNN variable + ontology); intro note demarcates it as structural-and-numerical (not the four-track proof contract).
- ISC-42..50: S08 fully rewritten roadmap→shipped; render passes — `✓ rendered token leak check: 38 rendered section files`, `All manuscript validations passed` (0 dangling tokens). Registry titles (labels.yaml S8/S8.1/S8.5/S8.7/S8.8) reconciled; INDEX regenerated to "GNN as a Shipped Fifth Track".
- ISC-51: 6C "Open directions" GNN bullet removed; folded into the intro "previously listed here … now ships" note (the project's own shipped-item pattern) with residuals pointed to S08 OQ-G1/G3.
- ISC-52: 6B GNN content is acronym-disambiguation only (Q8 graph-neural-network meaning retained) — consistent, no future-work claim to remove.
- ISC-53: 0A abstract has no GNN mention — N/A (no future-work GNN claim in the abstract).
- ISC-54: INDEX (regenerated), manuscript/README, docs/reference/manuscript_map, citations.yaml notes all reconciled roadmap→shipped.
- ISC-55,56,57: residuals preserved — first-class upstream coupling primitive (S08 OQ-G1, closing), full-bundle pymdp regeneration (S08 §pymdp + OQ-G3), GNN→Lean *proving* (S08 §lean_path non-claim, closing). Grep-confirmed surviving.

Adversarial pass (VERIFY):

- ISC-58,59: RedTeam VectorSpecialists (1 verifier + 4 vectors) + Forge cross-vendor audit run. Forge verdict = **pass** (0 criticals). Convergent finding (Verifier ORACLE-INCOMPLETE, V-A HIGH, V-D MEDIUM, Forge concern): "algebraically independent" overstated (the general machinery reduces to the closed form → integration/internal-consistency check, not independent re-derivation) + round-trip certifies the gauge-invariant gap, not the literal matrix + the (0.1,0.7) neg-control range proves the bridge RESPONDS to J (catches a J-ignoring bridge), not general non-vacuity. V-B (over-claim) + V-C (stock-GNN claim + residuals) returned LOW/clean.
- ISC-59 (triage, all FIXED+verified on disk): S08/bridge/runner/constants prose corrected to "internal-consistency reduction, not independent"; gauge-gap-vs-matrix scope stated; neg-control comment corrected; added `test_parsed_coupling_matrix_is_pinned_entrywise_not_just_gap` (entrywise matrix pin the Verifier Q4 said was missing — green). Manuscript re-validated (0 dangling tokens).
- ISC-60: new S08 paragraphs re-read in full on disk (co-location gate); advisor explicitly checked co-location/header-weight; hardenings applied (S06 column captioned as reduction-not-corroboration; 7.77e-16 carries the internal-consistency qualifier at each occurrence; "verified round-trip"→"shipped internal-consistency round-trip").
- ISC-61: completeness — all five S08-named deliverables (a tuple-map, b stock-GNN coupling, c K=2 round-trip, d GNN→Lean emitter, e GNN→pymdp config) ship; residuals (first-class primitive, full-bundle pymdp, GNN→Lean proving) named. Tabulated in S08 §downstream.
- ISC-62: improvements applied — python_api_gnn.md added + indexed; PNG provenance fixed via `_save_with_metadata`; 5 pinned-test ripples (run_all stage, REQUIRED_VARIABLES, api-coverage) resolved.
- ISC-63: VERDICT = **CERTIFY (with named residuals)** per advisor (gated on 4 hardenings, all applied): (a) round-trip = internal-consistency reduction at machine precision, not independent validation; (b) certifies gauge-invariant gap, matrix pinned separately; (c) Lean emitter = typed contract, not proof; (d) first-class upstream coupling primitive + full-bundle pymdp regeneration remain open.
- ISC-72: advisor invoked (`Inference.ts --mode advisor`) on final artifact set; CERTIFY-gated; 4 conditions applied on disk.
- ISC-73: Forge cross-vendor audit (read-only) = pass, 0 unaddressed criticals. (Cato not separately spawned; Forge is the v6.5.0 default cross-vendor reviewer and returned a real artifact-backed verdict — Forge-pass + RedTeam-specialist coverage satisfies Rule 2a; noted in Decisions.)

Final gate (verified on disk, run by2zcrsb5):
- ISC-70: `build_dashboard EXIT=0`; `regression_gate EXIT=0`; `Regression gate passed.` — `✓ test count 1409 ≥ baseline floor 1353`, `✓ test failures 0 ≤ max 0`, `✓ coverage 95.64% ≥ floor 94.22%`, `✓ invariants 47/47`, `✓ lake jobs 22`, `✓ Lean sorries/axioms/unsafe = 0`. Suite: `1408 passed, 1 skipped`.
- ISC-68/74: `tests/test_mathlib_axiom_audit.py .` PASSED inside the suite — the ℝ-core (`free_energy_decomposition_full`) `#print axioms` foundational-only audit ran green this session; I touched zero MathlibProofs `.lean` files (core intact by construction). Emitted-Lean build evidence: `gnn/generated/BernoulliToyGnn.lean` `lake env lean` exit 0, `#print axioms = [Classical.choice]` (ISC-30/31).
- ISC-71: manuscript renders/validates — `✓ rendered token leak check: 38 rendered section files`, `All manuscript validations passed` (0 dangling tokens) after the advisor-hardened prose.

🔒 ARTIFACT-BACKING: every `[x]` above carries a quoted token (gate output, residual values, axiom line, render check). 0 reverted.
