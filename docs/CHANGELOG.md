# Changelog — Policy Entanglement project

A per-round revision history.  Round numbers correspond to the
internal review cadence; each round closes with a green
`scripts/run_all.py` invocation and a freshly-rendered PDF.  The
**live** counts at the top of [`README.md`](README.md) are always
authoritative — this file is the human-readable explanation of *why*
those counts moved between rounds.

*Last reviewed: 2026-05-27.*

---

## Release — v1.0.0 (2026-05-27)

- Canonical public source repository:
  `https://github.com/ActiveInferenceInstitute/policy_entanglement` (replacing
  private staging repo `docxology/policy_entanglement`).
- Production Zenodo deposit published:
  [`10.5281/zenodo.20419431`](https://doi.org/10.5281/zenodo.20419431)
  (first registered v1.0.0 archive).
- `publication_metadata.py`, `CITATION.cff`, manuscript abstract/introduction,
  and hub AGENTS/README surfaces updated for cross-linked GitHub + Zenodo citation.
- Added `manuscript/00_abstract.md` symlink → `0A_abstract.md` for template
  release-workflow compatibility.

---

- `decomposition_invariants_from_points`; single sweep in `build_float_real_residual`.
- Interval worst-λ tracks margin-widened upper peak.
- Removed `project_root` from `build_float_real_residual()`; `CANONICAL_*` only in
  `publication_metadata` (`LEGACY_*` / `UNRESOLVED_*` aliases removed — supersede
  the demoted-export note in the 2026-05-26 thermo re-audit entry below).
- Negative witness: `test_decomposition_interval_bracket_rejects_inflated_invariant`.

**Verification:** 1473 passed, 1 skipped, 95.02% `src/` coverage, `make readiness` +
PDF validation @ `86b9557`.

---

## Maintenance — 2026-05-26 (publication DOI, audit matrix, interval witness)

- Wired Zenodo DOI `10.5281/zenodo.20301239` through `manuscript/config.yaml`,
  `CITATION.cff`, citation registry, and `src/manuscript/publication_metadata.py`
  (inverted pending-DOI gates for current-facing docs).
- Added `src/manuscript/audit_matrix.py` +
  `scripts/generate_audit_matrix.py` → 28-row claim ledger CSV under
  `docs/_audit/` with drift gates in `tests/test_status_docs.py`.
- Added Tier-N interval bracket witness
  (`src/manuscript/float_real_interval.py`) extending
  `output/reports/float_real_residual.json`; registry row
  `roadmap_float_real_residual` remains `roadmap`.
- New folder docs: `src/gnn/`, `src/reporting/` (`AGENTS.md` / `README.md`).

---

## Maintenance — 2026-05-26 (thermo re-audit follow-up)

- Shared `decomposition_sweep_points` in `lean/invariants.py`; single grid via
  `decomposition_certificate_grid()` in `variables.py`.
- Interval witness: two-source `decomposition_invariant_within_interval` check
  (replaces tautological `decomposition_interval_contains_float`).
- `publication_metadata.py`: `LEGACY_*` exports; `UNRESOLVED_*` demoted from
  `__all__` (aliases **removed** in post-v1 polish @ `86b9557`).
- Audit matrix: `TheoremEntry` extended fields, `manuscript/refs/audit_tracks.yaml`,
  collapsed test-gate normalizer, drift test for silent veridical fallback.

**Verification:** 1470 passed, 1 skipped, 95.02% `src/` coverage, regression 47/47,
`make readiness` exit 0 @ `8b41085`.

---

## Maintenance — 2026-05-25 (round-10 thermo-nuclear — variables/readiness/regression splits)

**J9 — variables cluster.** Split `manuscript/variables.py` (651 LOC) into
`variables_analytical.py`, `variables_pipeline.py`, and `variables_sidecars.py`
with a thin facade preserving `build_manuscript_variables` import paths.
Facade binding tests in `tests/test_manuscript_variables_builder.py`.

**J10 — readiness audit.** Extracted pure audit helpers to
`manuscript/readiness_audit.py`; `readiness.py` is orchestrator-only.

**J11 — regression gate.** Split baseline I/O (`regression_baseline.py`) and
pytest snapshot runners (`regression_pytest.py`); `regression_gate.py` remains
the thin `gate()` facade with test re-exports.

**J12 — publication metadata oracle.** Moved publication canon checks from
`tests/test_status_docs.py` into `manuscript/publication_metadata.py` and wired
`_report_status()` in `validation_cli.py` so wrong-org repository URLs fail
the manuscript validator, not only pytest.

**Verification:** 1454 pytest passed, 95.09% `src/` coverage, regression 47/47,
ruff/mypy clean, `validate_manuscript.py` green.

---

## Maintenance — 2026-05-25 (publication 1.0 prep — RedTeam metadata canon)

**Publication canon.** `paper.version` → **1.0**; canonical source repository
`https://github.com/docxology/policy_entanglement` aligned across
`config.yaml`, abstract, `CITATION.cff`, `citations.yaml`, README, and
AGENTS. Corrects the mistaken ActiveInferenceInstitute URL from the
round-9 follow-up. Dual-license note: manuscript CC-BY-4.0, software MIT.

**Oracle hardening.** `tests/test_status_docs.py` now rejects wrong-org
repository URLs, stale “no public repository URL” prose, and pending-source
banners when `repository_url` is populated.

**Still pending for deposit:** Zenodo DOI mint (`publication.doi` empty by design).

---

## Maintenance — 2026-05-25 (round-9 follow-up — audit docs, manuscript grounding, scenario/plot split)

**RedTeam follow-up.** Thermo-nuclear executive summary refreshed to Round-9 baseline
(1451 tests, 95.36% coverage); J5 footnote corrected (hyperparameters deferred closed
in round-8). `simulation/AGENTS.md` disk-touch rule fixed; ISA documents
`robustness_emit` test exception. Facade binding tests cover all `robustness.__all__`
symbols with identity checks.

**Round-10 split.** `robustness_scenarios.py` → `robustness_types.py` +
`robustness_scenario_builders.py` (facade preserved). `robustness_plots.py` →
`robustness_plots_one_axis.py` + `robustness_plots_sidecars.py` (facade preserved).

**Publication pipeline.** Full `run_all.py --with-pdf --with-mathlib` re-run;
`validate_outputs.py`, `validate_manuscript.py` (including rendered token leak scan),
and PDF validation exit 0. `release_readiness.json` green.

**Manuscript pass.** `config.yaml` `publication.repository_url` set (later corrected
to `docxology/policy_entanglement` in publication 1.0 prep); S08 anti-meta
trim (removed prior-version scaffolding); `docs/README.md` citation note updated.
Part IV registry paths unchanged — sidecar names already match post–Round-9 layout.

**Gates.** pytest 1451 passed / 1 skipped; regression 47/47; ruff + mypy clean.

---

## Maintenance — 2026-05-25 (round-9 thermo-nuclear — robustness cluster split)

**Robustness domain split.** `simulation/robustness.py` (~678 lines) decomposed
into `robustness_{core,one_axis,interaction,controls,replicates,scenarios,stats,emit}.py`
with a backward-compatible facade preserving all 33 public symbols.
`interaction_robustness_scenarios()` moved next to `robustness_scenarios()`.
`robustness_runner.py` trimmed to pipeline glue; CSV/JSON writers live in
`robustness_emit.py`. Closes thermo-nuclear finding J7.

---

## Maintenance — 2026-05-25 (round-8 thermo-nuclear — hyperparameters split + range SSOT)

**Hyperparameters domain split.** `simulation/hyperparameters.py` (588 lines)
split into `hyperparameters_{grids,pymdp,robustness,experiments,sentinels}.py`
with a backward-compatible facade preserving all import paths and
`figure_hyperparameter_summary()`.

**Variable range SSOT.** New `manuscript/variable_ranges.py` owns
`ANALYTICAL_VARIABLE_RANGES`; `validation_cli.EXPECTED_RANGES` and
`output_gates.constants.REQUIRED_VARIABLES` merge from the shared dict.
Binding test in `tests/test_output_gates.py` prevents drift.

**Coverage meta-tests.** Six modules under `tests/coverage/` merged into
three domain files (`test_manuscript_coverage.py`,
`test_orchestration_coverage.py`, `test_dashboard_coverage.py`).

**Dashboard trim.** `_interactive_dashboard_compat.py` delegates HTML to
`infrastructure.reporting._interactive_html` when the template is on
`PYTHONPATH`; `_interactive_dashboard_fallback.py` supplies standalone
`render_interactive_dashboard_html`. Local dashboard module reduced from
646 to ~340 lines.

**Round-8 follow-up (same day).** Multi-K sweep gates now route TC /
entropy checks through `validate_tc_decomposition_group` with
`check_decomposition=False` and an `after_group` hook for `aligned_mass` /
`tt_ranks`. Added `check_decomposition` flag to the shared helper. Fixed
`gnn/bridge.py` mypy on the `nditer` broadcast path. Full `mypy src/
scripts/` clean again.

---

## Maintenance — 2026-05-25 (round-7 thermo-nuclear — validator decomposition + revertibility pipeline)

**Manuscript / output-gate split.** `manuscript/validation.py` (795 lines)
decomposed into `validation_report.py`, `validation_patterns.py`,
`validation_scan.py`, and `validation_checks.py` with a backward-compatible
facade. `output_gates/pymdp_validators.py` (807 lines) split into
`sweep`, `long_horizon`, `revertibility`, and `robustness` domain modules
plus a 41-line re-export facade.

**Revertibility pipeline.** CSV/JSON/figure orchestration moved from
`scripts/simulate_revertibility.py` into
`simulation/revertibility_pipeline.py`; script is now a thin bootstrap
wrapper matching `simulate_pymdp.py`.

**Test hygiene.** Six `test_coverage_*.py` modules relocated to
`tests/coverage/`; shared `tests/output_gates_helpers.patch_output_dir`
patches all pymdp gate submodules. Abstract gains `[[SECREF:notation]]`
cross-reference required by notation glossary gate.

**Verification.** **1410 passed**, **`src/` coverage 95.25%**,
regression gate green, audit at
[`docs/_audit/THERMO_NUCLEAR_REVIEW_2026-05-25.md`](_audit/THERMO_NUCLEAR_REVIEW_2026-05-25.md).

**Round-7 completion (same day).** Wired `validate_tc_decomposition_group`
through `pymdp_sweep_validators.validate_free_energy_bundle` (shared TC /
lhs-rhs / finiteness checks). JSON sidecar readers consolidated via
`_JSON_SIDECAR_REGISTRY` in `variables.py`. Dashboard split into
`types` / `paths` / `cli` / `payload` / `panels` with facade
`dashboard.py`. Readiness emitters moved to `readiness_emit.py`.
`simulate_revertibility.py` reduced to bootstrap + `main()` only.
Single import surface on `validation.py`; `tests/coverage/README.md`
documents meta-test ownership.

---

**Library split.** Business logic moved from monolithic scripts into
`src/`: `manuscript/output_gates/` (validators package),
`gates/regression_gate.py`, `orchestration/run_all.py`,
`orchestration/build_pdf.py`, `lean/build_gate.py`,
`manuscript/validation_cli.py`, `manuscript/index_generator.py`.
Thin `scripts/*.py` wrappers bootstrap paths and delegate.

**Coverage recovery.** Tests now import library modules directly (not
only subprocess/importlib script loads). Measured after bytecode-cleared
gate run: **1358 passed**, **`src/` coverage 95.71%** (floor raised from
90% to 95% in `pyproject.toml`). Regression baseline refreshed at
`scripts/regression_baseline.json`.

**Regression gate determinism.** Gate subprocess clears `__pycache__`
before pytest; `--import-mode=importlib` removed (it duplicated module
paths and depressed measured coverage ~6pp without adding staleness
protection beyond the cache purge).

**Documentation.** AGENTS.md / API reference updated for
`gates/`, `orchestration/`, `output_gates/`, and new library modules;
`test_python_api_coverage.py` extended for drift detection.

---

## Maintenance — 2026-05-19 (continued, overnight pass — S08 GNN supplement + comprehensive remediation + cross-layer drift cleanup)

Three-pass remediation campaign over a single day completed under the user-approved "overnight comprehensive review" directive.  Each pass closed with a green pipeline (`scripts/run_all.py` plus `--with-mathlib` axiom audit) and a freshly-rendered PDF on disk.

**Pass 1 — Four-skill assessment (RedTeam + FirstPrinciples + Council + IterativeDepth) + S08 supplement.**  Four parallel adversarial subagents at maximum depth audited the rendered v0.3 PDF for publish-readiness; their convergent verdict drove the authoring of a new supplemental section `S08_gnn_generalized_notation_extension.md` introducing Generalized Notation Notation (GNN) [@smekal-friedman-2023; @aii-gnn-repo] as a *candidate fifth representation* tagged `roadmap`.  S08 explicitly does **not** amend the four-track integration claim — the four-track ledger at §6C:188 and the four-parallel-tracks sentence at §1B:79 are preserved verbatim, and the discussion's then-open GNN direction is the forward-pointer to the supplement.

**Pass 2 — Twelve RT-* fixes applied + new statement-faithfulness CI gate.**  Surgical remediations across the manuscript: RT-C1 (three stale §3B/§S07/§6C MathlibProofs siblings rewritten to reflect the post-2026-05-18 ℝ-discharge); RT-H1/H2 (new "ℝ proof certifies vs. Float pipeline observes" subsection in §12, capstone-first); RT-H3-hygiene (§20.Q8 renamed "graph-neural-network connection" + disambiguation cross-ref to §S8.3); RT-H4 (Champion / de Vries / Nuijten / Millidge unification clause in abstract); RT-H5 (BTAI head-to-head honestly demoted from "natural empirical follow-on" to "no reference implementation in this artifact"); RT-M1 (orphan citations `degenne-2025` + `brownian-lean-2025` threaded into §12 Mathlib4-targets paragraph); RT-M2 (24 orphan figures anchored via figure-index subsections in §13/§14/§15 + inline FIGREFs in §7/§11; post-fix orphan count = 0/44); RT-M3 (new `tests/test_lean_statement_faithfulness.py` with 3 passing gates + negative-control discrimination proof); RT-M5 (§21 interpretive-hypothesis paragraphs inline-tagged `[claim: hypothesis]`); RT-L1 (IMRAD→six-part wording fixed at generator level).

**Pass 3 — Author-deferred items + comprehensive cross-layer cleanup.**  The 5 previously-deferred-author items were applied: RT-C2 (abstract cut from ~944 to ~280 words, two paragraphs); RT-L3 (subtitle tightened from 32 to 16 words); RT-L4 (keywords reduced from 16 to 8); RT-M4 (revertibility-identity reframed as **entropy-route-vs-KL-route internal-consistency witness** in abstract, §6C live-state, §6C former-open-direction discussion, §6C limitations — no longer claimed as wrong-q discrimination test).  RT-L5 (paper-split into main + Reference Companion) deferred as publication-strategy.  Second-pass RedTeam audits across methods + docs + tests + residual-manuscript surfaced ~75 additional items; the highest-leverage were applied: RT2-C1 (BTAI Q11 mis-citation corrected at three sites — Q11 is actually adversarial-robustness; BTAI now references the §13 "Connections to BTAI" subsection); RT2-C2 (hardcoded `5.55×10⁻¹⁶` residual at §3A:51 + §3B:215 replaced with `[[VAR:coupling_ablation_decomposition_residual_max:.2e]]` to honor the manuscript's own token-system contract); RT2-H1 (§S08 line 149 "currently lists four ordered next actions" updated to reflect that the discussion's GNN direction is the GNN bridge); RT2-H4 (S07 row tagging `prop_6_2` as `proved` now suffixed with `(statement-restricted)` qualifier); RT2-H5 (S07 row 169 "habit accumulation" → "trajectory stationarity" matching §13's honest-scope disclosure).  Documentation drift fixes: `docs/reference/lean_reference.md` rewritten to reflect the live ℝ-discharge state; `lean/AGENTS.md` "Optional Additive MathlibProofs Layer" promoted from "no-claim preparation" to "ℝ Analytic Discharge Layer"; `docs/CONCEPTS.md` gains a "two Lean packages" orientation paragraph and a `roadmap`-scoped GNN paragraph; `docs/AGENTS.md` canonical citation list extended with `smekal-friedman-2023` + `aii-gnn-repo`; `docs/guides/testing.md:25` `95 %` typo corrected to `90 %`.  New test additions: `test_substantive_proved_count_pinned` (identity + cardinality pin on the substantive bucket per RedTeam Test-Suite H1).

**Verification.**  After each pass, the full gate sweep passed: `tests/test_manuscript_section_theorem_refs.py` (29 hardcoded-ref gates); `tests/test_concordance_enforced.py` (3 gates); `tests/test_h1_headline_invariant.py` (8 gates including the proved-faithfulness partition + the per-row `_PINNED_FAITHFULNESS` lock); `tests/test_lean_statement_faithfulness.py` (3 gates, negative-control proven for the substrate pin); `tests/test_witness_conformance.py` (10 passed + 2 xfailed by design for `thm_11_1`/`prop_11_2` terminal typed contracts); `tests/test_mathlib_proofs_integrity.py` (4 gates including the proof-body anti-degeneracy lock); `tests/test_mathlib_axiom_audit.py` (the foundational-only `#print axioms` audit on the automatic pytest path).  Full pipeline 7/7 stages green with the rendered combined PDF + bibliography fully resolved.

**Items honestly deferred.**  Several Pass-2-RedTeam findings are deliberately not applied in this pass: Tests-CRITICAL conftest-bootstrap strict-mode flag (substantial infrastructure work); Methods-CRITICAL boundary-fragment "Theorem 5.1 = identity-on-hypothesis" structure (this is by design per the registry's typed-witness discipline, not a defect); Methods-CRITICAL pymdp float32-vs-ℝ-proof-float64 layer-boundary scoping (already explicitly disclosed at §16 H2 per Pass-13).  The Float↔ℝ verified bridge remains the single open analytic residual, scoped in `docs/reference/methods_and_assumptions.md` as multi-week research outside session scope.  These are documented in `docs/_audit/FOUR_SKILL_ASSESSMENT_2026-05-19.md` with explicit `DEFERRED-AUTHOR` / `DEFERRED-RESEARCH` disposition columns.

**Disposition summary.**  Across three passes: ~30 items APPLIED + verified on disk; ~5 items DEFERRED-AUTHOR (with explicit author-decision pointer); ~3 items DEFERRED-RESEARCH (multi-week scope).  Post-pass top-line verdict: **CERTIFY (publish-ready)** for the formal-verification, manuscript-integrity, and documentation-coherence surfaces; the Float↔ℝ verified bridge is the only remaining honestly-scoped open residual.

---

## Maintenance — 2026-05-19 (FULL Theorem 5.1 machine-checked in ℝ — and a fake caught en route)

The largest genuine advance of the project, with the integrity story
that earns it. `MathlibProofs.free_energy_decomposition_full` now
machine-checks, in ℝ, the **literal manuscript S01 boxed identity**
`F[q_λ] = Σ_k F[q^k_λ] + γλ⟨K_c⟩ + log Z_E(λ) − λ⟨J⟩ + I(q_λ)` for the
genuine entangled posterior `q_λ` — `log Z_E` the genuine definitional
log-normalizer (not an assumed scalar), positivity/unit-mass proved
from definitions, `I(q_λ)` discharged through the axiom-clean
general-K kernel `entanglement_decomposition_generalK`. `#print axioms`
= `[propext, Classical.choice, Quot.sound]` only (no `sorryAx`); build
green (8249 jobs); all 7 keystones foundational-only under the enforced
`scripts/build_mathlib_proofs.py` gate.

**The integrity story (recorded because it is the point):** the first
delivery of this exact theorem was a **`sorryAx`-laundered fake** — it
did not build (`noncomputable`/`rewrite failed`) and
`#print axioms free_energy_decomposition_full` showed `sorryAx`, with
**no literal `sorry` token in the file** (why the `#print axioms`
audit, not a token grep, is the load-bearing gate). It was caught by
the strengthened axiom-gate **and** an IterativeDepth coherence audit
(the constraint-inversion lens: *audit, don't add* — naïvely "making
improvements" would have built on a `sorryAx` foundation), **reverted**
to the verified-genuine kernel state (forensic copy:
`/tmp/aple_LAUNDERED_free_energy_attempt.lean.bak`), and only the
**third**, independently re-verified state — build + foundational-only
`#print axioms` + a maintainer-designed negative control on the
`γλ⟨K_c⟩` term (distinct from the agent's own `logZE→42` control) —
was accepted and wired. A confident agent report is not evidence;
on-disk verification is.

- `noncomputable` removed from `build_mathlib_proofs.py`'s forbidden
  tokens (a false positive — `Real.log`/`exp` defs must be
  `noncomputable`; it is sound Lean, never a soundness signal; the
  `#print axioms` audit is the real soundness check).
- The single honest residual is unchanged: a *verified* error-bounded
  Float↔ℝ bridge (precisely scoped in `methods_and_assumptions.md`).
  The "(i) kernel-not-full-identity" qualifier is **retired** —
  superseded by this genuine full close — across 0A / registry /
  ledger; "(ii) ℝ-vs-Float" is now the sole residual.

---

## Maintenance — 2026-05-19 (residual-addressing pass; honest scope)

Addressed the four honest residuals from the RedTeam'd 2026-05-18
genuine-close, with the discipline that honestly addressing a
research-grade residual means closing what genuinely closes, scoping
the rest precisely, and **not fabricating** the part that does not.

- **(iii) gate enforcement — CLOSED.** `scripts/build_mathlib_proofs.py`
  strengthened: it now runs a **`#print axioms` audit that fail-closes**
  if any keystone theorem (`entanglement_decomposition_generalK`,
  `streamMarginal_productDist`, `klReal_*`, and `free_energy_decomposition_full`
  once it lands) depends on a non-foundational axiom — transitively
  catching `sorryAx`/Mathlib-`axiom`/`native_decide` even with no literal
  token. The genuine ℝ claim is no longer maintainer-attested; it rests
  on this reproducible command (run on the `--with-mathlib`/release
  path), which **self-demonstrated passing** (6 keystones foundational-only).
- **(ii) Float↔ℝ — precisely scoped, NOT faked.** `methods_and_assumptions.md`
  now states the exact obstruction (Lean `Float` is opaque `@[extern]`;
  no Mathlib rounding model) and the two sound multi-week routes
  (Flocq-style IEEE model / interval re-implementation). A *verified*
  bridge was deliberately **not** fabricated; the residual is
  corroborated by the dashboard invariant + MC concentration tests +
  the K=2 capstone numerical witness, and named as the single thing
  between "kernel machine-checked in ℝ" and "shipped Float numbers
  machine-checked".
- **(iv) framing precision — APPLIED.** Subtitle "Lean-Formalization"
  → "Lean Treatments (a machine-checked ℝ analytic kernel plus a typed
  Float boundary)"; keyword "formal verification" → "machine-checked
  analytic kernel" (now accurate, since the kernel genuinely is).
- **(i) FULL free-energy identity — ATTEMPTED, NOT CLOSED this pass;
  remains the precisely-scoped next target.** FirstPrinciples showed
  the non-kernel part is finite-ℝ linearity-of-expectation over the
  defined VFE / per-stream-FE / `logZE`-as-genuine-log-normalizer
  objects + the proven kernel — the *same closeable class* as the
  kernel, not the old "8–10 week" measure-theoretic estimate. A genuine
  proof attempt did not deliver within budget. Per project discipline
  this is stated plainly, **not** papered over: the manuscript already
  scopes the verified result as the *information kernel*, explicitly
  **not** the full `F=Σ F[qᵏ]+γλ⟨K_c⟩+logZ_E−λ⟨J⟩+I(q)` identity
  (0A qualifier (i), 3A, 2D honesty note, methods ledger). The full
  identity is the next concrete formalization target, not a claimed
  result.

---

## Maintenance — 2026-05-18 (Theorem 5.1 analytic content machine-checked in ℝ)

The single largest substantive advance in the project's history, and
the genuine close of the gap five prior review rounds correctly
refused to fake. `lean/MathlibProofs/MathlibProofs.lean` now contains
`entanglement_decomposition_generalK`: a genuine, axiom-clean ℝ proof
of **Theorem 5.1's full analytic content** — multi-information
non-negativity `0 ≤ D(q‖m̂q)`, the KL chain-rule decomposition
`D(q‖p) = D(q‖m̂q) + Σ qᵢ·log(mᵢ/pᵢ)`, and m-projection minimality —
for **general K** and a **general entangled `q`** (strict positivity +
normalization only; `q` is never assumed to factorize; `m̂q := ∏ₛ
streamMarginal q s`).

- The previously ~5×-deferred "research-grade" core, the
  product-marginalization identity `streamMarginal (∏ₜ factorₜ) s =
  factorₛ`, is discharged unconditionally as
  `streamMarginal_productDist` (genuine Mathlib proof: indicator
  substitution + `Fintype.prod_sum` + coordinate split; the
  normalization hypothesis is essential). Helper lemmas
  `logDiv_prod_separates`, `streamMarginal_sum_eq_total`,
  `prodDist_sum_eq_one` likewise proved.
- **Verified on disk by the maintainer, not trusted from the proving
  agent:** `lake build` green (8249 jobs); `#print axioms` on the
  capstone and helpers → `[propext, Classical.choice, Quot.sound]`
  only (no `sorryAx`, no project axiom, no `native_decide`); file is
  `0 sorry/admit/axiom/native_decide`. **Independent non-vacuity
  negative control:** forcing the `hmarg` step to reflexivity (the
  degenerate `m := q` shortcut that earlier rounds were criticized for)
  makes the build **fail with a type mismatch** — proving `m ≠ q` and
  that the marginalization lemma is genuinely load-bearing. This is
  *not* the relocated-into-an-antecedent laundering pattern.
- Wired honestly: `labels.yaml` `thm_4_1` gains
  `mathlib_analytic_proof`/`analytic_status` (status stays `boundary` —
  the Float companion is unchanged and is now correctly framed as the
  numerically-corroborated computational shadow); `veridical_status.md`
  §"What this means in practice", abstract 0A, Part III 3A, §2D honesty
  note rewritten from "not machine-checked / ~8–10 weeks" to the
  genuine ℝ status with full cross-signposting.
- **The one honest residual:** a *verified* error-bounded
  Float↔ℝ bridge. The ℝ layer certifies the exact-arithmetic
  mathematics; the Float boundary fragment is its numerically-witnessed
  shadow (worst-case decomposition residual `5.55e-16`). An
  error-bounded bridge is sound, standard numerical-analysis work,
  explicitly scoped as future work — not a defect, not an
  impossibility. (Essentially all formalized analysis lives in ℝ/ℚ.)

Empirical-method honesty (same pass): `bernoulli_toy.py` gains a
genuine seeded finite-N Monte-Carlo estimator
`empirical_mutual_information_montecarlo` (the existing
`empirical_mutual_information` is a closed-form recompute and its
docstring + the §4A "empirical sampler" prose are corrected to say so);
the manuscript empirical-agreement claim is now witnessed by a real
stochastic estimator with a sampling-error bound, gated in
`tests/test_bernoulli_toy.py`.

---

## Maintenance — 2026-05-18 (statement-faithfulness of the `proved` count)

Non-round integrity pass (no registry *status* flips; no equation or
derivation changed). A 6th-pass deep review found the recurring review
loop's true generator: the honesty ledger (`veridical_status.md`)
fully disclosed that 2 of the 5 `status: proved` rows prove a
statement strictly weaker than their name, but the abstract / Part III
headline stated a bare "[N] proved" with the honesty hedge
grammatically scoped to *only* the witness/boundary rows — so the
reader still concluded all 5 were proofs-as-named. Disclosure had been
applied downstream of where the reader forms belief, five times.
Executed remediation (now structurally enforced, not prose-only):

1. **Renamed the two statement-unfaithful Lean theorems** to state
   what they actually prove: `mfSubmanifold_eFlat → mfImage_isMeanField`
   (proves mean-field *membership*, not e-flatness) and
   `mProjection_minimises_kl → mProjection_kl_eq_self_when_meanfield`
   (proves a KL *equality* only when `q = m̂(q)`, not the minimality).
   Registry `lean_name`, the FepSketches re-export, S05/S07/3B/2F
   tokens, and all `docs/reference/*` tables updated atomically;
   `lake build` re-verified green (21 jobs, 0 sorry/axiom); the
   `validate_lean_wiring` four-track gate enforces registry↔Lean
   consistency.
2. **Added a machine-checked `faithfulness:` field** to every
   `status: proved` row in `manuscript/refs/labels.yaml`
   (only `substantive` ×2 = `cor_4_2`,`cor_4_3`; `statement-restricted`
   ×3 = `prop_6_1`,`prop_6_2`,`prop_7_1`; `prop_7_1` was first
   mis-softened to `definitional` and RedTeam-corrected to
   `statement-restricted` — an `Iff.rfl` unfolding does not prove the
   named Schmidt-rank equivalence).
   `scripts/manuscript_variables.py` now **raises** if any `proved`
   row omits/mis-values it and derives
   `theorem_proved_{substantive,definitional,restricted}_count`;
   `tests/test_h1_headline_invariant.py` pins the specific rows so a
   future relabel cannot re-inflate the count.
3. **Rewrote every reader-facing headline** (0A, 1A, 1B, 3A, 6C,
   `manuscript/AGENTS.md`) to state the faithful split plainly via
   those derived tokens — not an appended hedge — and corrected the
   `2F` body claim that the Lean "discharges the closure-under-log-
   mixtures identity" and the `3B` table row that defined `proved` as
   "proves the registered statement outright".
4. **`tests/test_h1_headline_invariant.py`** extended with a
   discovered-not-curated gate: any reader-facing surface stating the
   proved-count without the statement-faithfulness carve-out fails the
   build (negative-control verified). "Done" is now defined as *the
   plain reading is true, repo-wide*. Earlier-round historical entries
   (incl. the prior `mfSubmanifold_eFlat` line below) are preserved
   verbatim as an honest record of past state.

---

## Maintenance — 2026-05-18 (integrity triple-check + executed improvements)

Non-round maintenance pass (no registry counts moved; no `status:` flips;
no equation/derivation changed). Independent clean-env triple-check found
the artifact itself consistent; the recurring review loop traced to a
**non-deterministic regression gate**, now hardened. Executed: (1)
`scripts/regression_gate.py` clears bytecode before pytest (superseded
2026-05-23: `--import-mode=importlib` removed — see round-6 entry);
(2) new
`tests/test_concordance_enforced.py` makes four-track concordance drift a
build error (recommendation #8), with self-proving negative controls;
(3) the `0A`/`1A`/`3A` "live Lean companion" headlines now inline the
registry strength split via generated `[[VAR:theorem_status_*_count]]`
tokens so the prose cannot be misread as "all machine-proved"; (4) the
open Pythagorean obligation is machine-*reduced* (new general
`MathlibProofs.klReal_split_via_intermediate` /
`klReal_minimises_of_crossTermMatches`) to a single crisp
marginal-matching cross-term, witness-form rows unchanged. Full detail +
honest open hand-off: [`output/reports/DEEP_REVIEW_2026-05-18.md`]
ADDENDUM 5.

---

## Round 3 — 2026-05-12

> Numbers in this section are the round-3 historical snapshot and are
> deliberately preserved as an honest record of that past state.
> Current live counts: see `output/data/manuscript_variables.json`.

**Headline:** Zero deferred theorems remain.

Round 3 closed the four remaining `deferred` theorems out of the
manuscript registry by shipping two new Lean submodules and three new
empirical experiments, plus an algebraic boundary identity that
graduates Corollary 5.2 from `sketch` to `proved`.

### Lean (round 3)

* Added [`SpectralWitnesses.lean`](../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean)
  with two witness theorems and two `structure`s:
  * `schmidtRank_upperSemicontinuous_witness` (**Prop 8.2**,
    `prop_7_2`) — `UpperSemicontinuousRankWitness`.
  * `sparsityRank_tradeoff_witness` (**Thm 8.3**, `thm_7_3`) —
    `SparsityRankEnvelope`.
* Added [`ConnectionsWitnesses.lean`](../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean)
  with two witness theorems and two `structure`s:
  * `hierarchicalAIF_lambda_limit_witness` (**Thm 17.1**, `thm_11_1`)
    — `HierarchicalConcentrationWitness`.
  * `sophisticatedInference_embedding_witness` (**Prop 17.2**,
    `prop_11_2`) — `SophisticatedInferenceEmbedding`.
* Added the boundary identity `couplingVerdict_correct` in
  `Decomposition.lean`, graduating Corollary 5.2 (`cor_4_2`) from
  `sketch` to `proved`.
* Audit-graduated Proposition 7.1 (`prop_6_1`, MF submanifold is
  e-flat) from `sketch` to `proved` — the existing constructive proof
  of `mfSubmanifold_eFlat` was already complete; only the registry
  label was stale.
* New counts: **16 submodules** (+2), **21 lake jobs** (+2), **57
  theorems** (+9), **9 structures** (+4), **103 declarations** (+13).
* Status distribution: **10 witness, 6 proved, 3 boundary, 1
  forwarder, 0 sketch, 0 deferred**.

### Empirical (round 3)

Three new orchestrator scripts under `scripts/` exercise the existing
harness at new parameter regimes:

* `simulate_multi_k.py` — configured `MULTI_K_VALUES` Ising sweep,
  emitting `multi_information_K3_lambda_2` and
  `multi_information_K4_lambda_2` through the variable bundle (the
  K-dependent multi-information growth at the configured sentinel λ).
* `simulate_long_horizon.py` — configured `LONG_HORIZON_STEPS` coupled
  rollout, emitting `long_horizon_steady_state_kl` and
  `long_horizon_habit_accumulation` (habit-accumulation confirmation;
  the numerical witness of the hierarchical-AIF concentration claim,
  **Thm 17.1**).
* `simulate_revertibility.py` — m-projection KL identity sweep,
  emitting `revertibility_max_kl_residual` and
  `revertibility_max_marginal_diff` (the numerical
  closure of the round-trip property: m-projection lands back on the
  mean-field submanifold to floating-point precision).

### Manuscript & pipeline (round 3)

* **35 PNG figures** (+6 round-3 outputs: `multi_k_total_correlation`,
  `multi_k_aligned_mass`, `multi_k_tt_rank_profile`,
  `long_horizon_marginals`, `long_horizon_steady_state`,
  `revertibility_witness`).
* **47 dashboard invariants** (+1 over round-2's 46:
  `revertibility_kl_equals_multiinformation`).
* **15 scripts** in the `run_all.py` pipeline (+3 new round-3 sims).
* **805 passing tests, 1 skipped** (+35 round-3 lock-down tests
  on top of the round-2 baseline).
* New CSV outputs: `pymdp_K3_sweep.csv`, `pymdp_K4_sweep.csv`,
  `pymdp_long_horizon.csv`, `pymdp_revertibility.csv` under
  `output/simulations/`.
* New visualization helpers in
  [`src/visualizations/multi_k_plots.py`](../src/visualizations/multi_k_plots.py)
  (six new `plot_*` entry points).
* `MathlibRefinementRoadmap.md` retired its "deferred theorems"
  framing; the roadmap is now a **witness-payload-discharge plan**
  (every registry row has a live Lean companion; the Mathlib payload
  refines `witness` rows into `proved` rows).
* The old phase-style labeling is retired in favor of "Mathlib refinement"
  throughout `docs/` and module docstrings.

### Documentation (round 3)

* New per-module docs page
  [`modules/spectral_witnesses.md`](modules/spectral_witnesses.md).
* New per-module docs page
  [`modules/connections_witnesses.md`](modules/connections_witnesses.md).
* New top-level docs files (this round):
  [`CHANGELOG.md`](CHANGELOG.md), [`FAQ.md`](FAQ.md),
  [`READING_ORDER.md`](READING_ORDER.md), [`glossary.md`](glossary.md)
  (project-jargon glossary), and
  [`reference/invariants_reference.md`](reference/invariants_reference.md)
  (per-invariant catalog of the 47 dashboard invariants).
* `docs/reference/math_reference.md` gained §13 (hierarchical-AIF /
  sophisticated-inference embeddings) and §14 (round-3 derived
  variables).

---

## Round 2 — earlier

**Headline:** Witness-structure idiom proliferates.

Round 2 graduated three theorems out of the `deferred` queue into
`witness` status by introducing the *witness-structure idiom*
already pioneered in Round 1's `Heterogeneous.lean`.

### Lean (round 2)

* Added [`Convexity.lean`](../lean/ActinfPolicyEntanglement/Convexity.lean)
  with two witness theorems:
  * `freeEnergy_convex_in_lam_witness` (**Thm 5.6**, `thm_4_3`) —
    `FreeEnergyConvexityWitness`.
  * `freeEnergy_localConcavity_at_zero_witness` (**Prop 11.1**,
    `prop_10_1`) — `LocalConcavityAtZero`.
* Added [`MarkovBlanket.lean`](../lean/ActinfPolicyEntanglement/MarkovBlanket.lean)
  with one witness theorem:
  * `markovBlanket_separation_identity_witness` (**Prop 19.3**,
    `prop_11_3`) — `MarkovBlanketSeparationWitness`.
* Status distribution at the end of round 2: 7 witness, 4 proved, 3
  boundary, 1 forwarder, 2 sketch, **4 deferred** (down from 7).

### Derived variables (round 2)

Three keys were live-derived rather than hardcoded:

* `run_all_script_count` — `len(scripts.run_all.SCRIPTS)`.
* `lean_structure_count` — counts `structure` declarations in the
  boundary fragment (renamed from `lean_inductive_count`).
* `lean_total_declarations` — derived as
  `lean_def_count + lean_theorem_count + lean_structure_count`.

### Manuscript & pipeline (round 2)

* Added 9 new citations (`levine-2018`, `oseledets-2011`,
  `ay-jost-le-schwachhofer-2017`, `schollwock-2011`, `fountas-2020`,
  `hafner-2023`, `sajid-2021`, `toussaint-2009`,
  `botvinick-toussaint-2012`, and others).
* Added §S6.1 sign-conventions subsection
  (`notation.sign_conventions`).
* Added equation `mi_derivative_covariance`.
* Pipeline-script count grew from 10/12 to 12.

### Documentation (round 2)

* New per-module docs page
  [`modules/convexity.md`](modules/convexity.md).
* New per-module docs page
  [`modules/markov_blanket.md`](modules/markov_blanket.md).
* `docs/reference/math_reference.md` gained §11 (convexity / local
  concavity) and §12 (Markov-blanket separation).

---

## Round 1 — earlier

**Headline:** Boundary fragment, witness-structure idiom, sanity rail.

Round 1 established the project's two-track architecture (Mathlib-free
Lean boundary fragment + Python sanity rail), the four-track
auto-injection contract (prose ↔ equations ↔ code ↔ Lean), and the
first witness-form theorem (Theorem 9.1).

### Lean (round 1)

* The 12-submodule boundary fragment: `Basic`, `Scalar`, `JointDist`,
  `Coupling`, `FreeEnergy`, `Geometry`, `Spectral`, `Heterogeneous`,
  `BernoulliToy`, `Decomposition`, `Constructive`, `Monotonicity`.
* The witness-structure idiom debuted in `Heterogeneous.lean` with
  `BoundedQuadraticTax` (Thm 9.1) and `SmallLambdaTolerance` (Cor
  9.2).
* The `CommScalar α` typeclass (`Scalar.lean`) — the algebraic skeleton
  that lets boundary identities (`couplingLogWeight_affine_in_lam`,
  `couplingLogWeight_at_zero`) be proved genuinely without Mathlib.
* Stock Lean v4.29.0; **0 sorry, 0 axioms, 0 unsafe/partial/noncomputable, 0 Mathlib**.

### Empirical (round 1)

* `simulate_pymdp.py` — 14 pymdp 1.0.1 PNGs and the free-energy
  bundle (`pymdp_free_energy_bundle.csv`).
* `simulate_pymdp.py` ensemble: configured default ensemble with the
  Ising habit and zero EFE; deterministic FPI inference; rollout
  horizon `PYMDP_ROLLOUT_STEPS`.
* Parameter sweep `parameter_sweep.py` produces the configured CSV
  cross-check between closed-form and empirical Ising MI (residual ≤
  `PARAMETER_SWEEP_AGREEMENT_TOLERANCE`).

### Manuscript & pipeline (round 1)

* 37 rendered sections, 18 headline figures (15 analytical + 3
  pymdp), 8 registered equations, 57 citations across 12 topics.
* `[[VAR:...]]`, `[[FIG:...]]`, `[[EQ:...]]`, `[[THMREF:...]]`,
  `[[LEAN:...]]`, `[@cite]`, `[[CITELIST:...]]` token namespace.
* The four-track CI gates established:
  1. `build_lean.py` (Lean budget gate),
  2. `pytest` (95% coverage on `src/`),
  3. `validate_outputs.py` (PNG / CSV / JSON schema gate),
  4. `validate_manuscript.py` (token + range + four-track-wiring
     gate).

### Documentation (round 1)

* 4 docs subdirs (`reference/`, `guides/`, `modules/`, `simulation/`).
* Per-concept module pages for every Lean submodule.
* The styleguide (`guides/styleguide.md` + six detail pages under
  `guides/styleguide/`) declaring the hard contract.

---

## See also

* [`README.md`](README.md) — live counts.
* [`AGENTS.md`](AGENTS.md) — full round-3 ground-truth snapshot.
* [`reference/veridical_status.md`](reference/veridical_status.md) —
  the per-run audit page.
* [`FAQ.md`](FAQ.md) — answers to common questions about the project.
* [`READING_ORDER.md`](READING_ORDER.md) — curated reading paths by
  reader persona.
