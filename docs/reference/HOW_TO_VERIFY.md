# How to Verify This Artifact

> One-page recipe for reproducing the project's four CI-gated tracks and
> the headline ℝ-analytic discharge.  Each command is copy-pasteable; the
> three sections below are independent and can be run in any order, but
> the order shown is the natural cold-start sequence.

## 1.  Float boundary fragment (fast — ~5 minutes cold)

Verifies the typed-API surface every numbered theorem rides on.  Stock
Lean 4.29.0; **no Mathlib dependency**.

```bash
cd lean
lake build
```

Expected: 22 jobs, exit 0, zero `sorry`/`axiom`/`unsafe`/`partial`/
`noncomputable` declarations.  Each manuscript theorem with a Lean
companion has its source extracted live into
[`manuscript/S05_lean_code_skeleton.md`](../../manuscript/S05_lean_code_skeleton.md)
via the `[[LEAN:...]]` token system; the manuscript renderer's
`scripts/validate_manuscript.py` fails the build on any unresolved
token, so prose and Lean cannot drift silently.

## 2.  Mathlib ℝ analytic kernel (multi-hour cold, ~minutes warm)

Verifies the **headline Theorem 5.1** in $\mathbb{R}$ — the full S01
boxed free-energy identity
$F[q_\lambda] = \sum_k F[q^k_\lambda] + \gamma\lambda\langle K_c\rangle + \log Z_E(\lambda) - \lambda\langle J\rangle + I(q_\lambda)$ —
machine-checked under foundational-only `#print axioms` (no `sorryAx`,
no project-axiom).

```bash
# Option A — direct lake invocation (fastest if you know lake)
cd lean/MathlibProofs
lake build

# Option B — enforced script (recommended; runs the foundational-only
# axiom audit + integrity checks + two negative-control assertions)
uv run python scripts/build_mathlib_proofs.py

# Option C — automatic pytest path (recommended for CI; honest xfail
# if `lake` is unavailable, never silent pass)
uv run pytest tests/test_mathlib_axiom_audit.py -v
```

Cold build of the Mathlib v4.29.0 dependency tree is multi-hour; warm
re-builds (incremental) are minutes.  Expected: 8249 jobs green, exit
0, `#print axioms free_energy_decomposition_full` returns
`[propext, Classical.choice, Quot.sound]` only.  Two independent
negative controls (neutralising the `logZE` definitional body OR the
`γλ⟨K_c⟩` coupling term) each make the build fail — a deliberate
non-vacuity check.

The single open analytic residual is a *verified* error-bounded
Float$\leftrightarrow\mathbb{R}$ bridge linking the $\mathbb{R}$
proofs to the Float pipeline, scoped multi-week research in
[`methods_and_assumptions.md`](methods_and_assumptions.md).

## 3.  Numerical pipeline + manuscript render (~15-25 minutes)

Runs every simulation, regenerates every figure, re-derives every
`[[VAR:...]]` token from real outputs, renders the combined PDF, and
runs the validation gates.

```bash
# Full reviewer gate: numerical pipeline, PDF validation, MathlibProofs,
# pytest + coverage, lint, type check, and readiness report.
make readiness

# Or run stages individually
uv run python scripts/run_all.py --with-pdf --with-mathlib
uv run python scripts/build_pdf.py                     # PDF render only
uv run python scripts/validate_outputs.py              # post-render validation gates
uv run python scripts/regression_gate.py               # regression baseline check
uv run python scripts/readiness_report.py              # release summary
```

Expected outputs (on a clean run):
- `output/data/manuscript_variables.json` — every numerical claim in the manuscript flows from this file via the `[[VAR:...]]` token system.
- `output/figures/*.png` — all registered figures present with metadata; the live count is recorded in `output/reports/release_readiness.json`.
- `output/pdf/actinf_policy_entanglement_lean_combined.pdf` — combined manuscript with bibliography fully resolved.
- `output/reports/release_readiness.md` and `output/reports/release_readiness.json` — per-stage timings, PDF status, MathlibProofs status, figure registry status, and failed-stage summary.
- `output/reports/test_results.json` — generated pytest pass/fail/skip counts and `src/` coverage.

Current release-readiness snapshot: the generated report records all
readiness stages green, all registered figures present, PDF validation
passed, MathlibProofs passed, and a full pytest run with zero skipped
tests. Treat `output/reports/release_readiness.md` as the live source if
these values move.

## 4.  Reproducibility contract gates (any single-purpose verification)

Each of these tests is independent and can be run in isolation:

```bash
# Manuscript-tree hardcoded-ref / token / wiring gate
uv run pytest tests/test_manuscript_section_theorem_refs.py -v

# Concordance enforcement (prose ↔ Lean ↔ Python parity)
uv run pytest tests/test_concordance_enforced.py -v

# Headline-invariant pin (per-row faithfulness, the proved-bucket partition)
uv run pytest tests/test_h1_headline_invariant.py -v

# Statement-faithfulness CI (substantive vs statement-restricted rows)
uv run pytest tests/test_lean_statement_faithfulness.py -v

# Witness-conformance (independent-route content checks)
uv run pytest tests/test_witness_conformance.py -v

# MathlibProofs integrity (REQUIRED-keystone list + proof-body anti-degeneracy)
uv run pytest tests/test_mathlib_proofs_integrity.py -v

# Mathlib axiom audit (foundational-only `#print axioms` on automatic pytest path)
uv run pytest tests/test_mathlib_axiom_audit.py -v
```

## What "publish-ready" means

A reviewer should be able to:

1. Clone the repository and run §3 — get a green readiness report and a validated combined PDF whose every numerical value flows from the run.
2. Run §1 — verify that every numbered theorem has a type-checked Lean companion in stock Lean.
3. Run §2 — verify that the headline Theorem 5.1 is machine-checked in $\mathbb{R}$ with foundational-only `#print axioms`.

All three are reproducible commands, not maintainer-attested steps.  The single open residual (the verified Float↔ℝ bridge) is honestly scoped in [`methods_and_assumptions.md`](methods_and_assumptions.md) — it is multi-week research, not a session-completable obligation, and is *not* claimed closed by any prose in the artifact.

For the project's bigger-picture claim ledger see
[`veridical_status.md`](veridical_status.md); for the per-row
faithfulness audit see
[`veridical_status.md` §1](veridical_status.md);
for the Float↔ℝ residual obstruction see
[`methods_and_assumptions.md` §2-3](methods_and_assumptions.md).
