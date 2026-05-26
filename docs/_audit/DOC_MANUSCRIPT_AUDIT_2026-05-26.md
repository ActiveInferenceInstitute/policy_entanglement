# Documentation and Manuscript Claims Audit — 2026-05-26

**Project:** `actinf_policy_entanglement_lean` (private repo `docxology/policy_entanglement`)  
**Baseline commit:** `5e7be2d` (Round 10 thermo splits)  
**Auditor workflow:** Plan *Docs and claims audit* — automated gate stack, doc-drift pytest, claim-contract pytest, targeted manual passes, PDF spot-check.  
**Generated at:** 2026-05-26 (local gates; `release_readiness.json` timestamp `2026-05-26T01:07:47Z`)

---

## 1 — Gate summary

| Gate | Result | Measured value |
| --- | --- | --- |
| `make readiness` (pipeline + PDF + MathlibProofs + pytest + lint + report) | **PASS** (after transient ruff import-order drift cleared locally) | See rows below |
| `scripts/validate_manuscript.py` | **PASS** | 38 section files; rendered-token leak check clean |
| `scripts/validate_outputs.py` | **PASS** | 47 PNG figures; 14 simulation sidecars; variable ranges satisfied |
| `scripts/regression_gate.py` | **PASS** | 47/47 invariants; 22 Lean jobs; sorries/axioms/unsafe = 0 |
| Doc-drift pytest bundle (Phase 1C) | **PASS** | 31/31 |
| Claim-contract pytest bundle (HOW_TO_VERIFY §4) | **PASS** | 78/78 |
| `generate_theorem_map.py --check` | **PASS** | `_theorem_map.md` current |
| `generate_index.py --check` | **PASS** | `manuscript/INDEX.md` current |
| `scripts/validate_pdf.py` | **PASS** | 169 pages, margin contract OK |

### Live metrics (authoritative JSON)

Source: `output/reports/release_readiness.json`, `output/reports/test_results.json`

| Metric | Value |
| --- | --- |
| Pytest collected | 1455 |
| Passed / failed / skipped | 1454 / 0 / 1 |
| Coverage (`src/`) | 95.10% |
| Regression invariants | 47/47 |
| Lean lake jobs | 22 |
| Combined PDF pages | 169 |
| PDF size | 14.42 MB |
| PNG figures | 47 (46 registered + 1 optional coupling graph) |
| Rendered manuscript markdown | 38 |
| Theorem registry rows | 21 (5 proved, 11 witness, 3 boundary, 1 forwarder, 1 roadmap) |
| MathlibProofs build | passed; 29 local theorems; hygiene clean |
| Pipeline wall-clock | 732.85 s (slowest: `regression_gate.py` 456.7 s) |

### Variable provenance (validate_manuscript)

| Class | Count |
| --- | --- |
| hyperparameter-derived | 121 |
| sidecar-derived | 160 |
| analytic-computation | 26 |
| registry-derived | 17 |
| source-scan-derived | 11 |
| uncategorized | 18 |

---

## 2 — Documentation findings

### Automated coverage (green)

- **`tests/test_status_docs.py`** — README, AGENTS, docs, and manuscript prose contain no stale live-count literals vs `test_results.json` / PDF info.
- **`tests/test_agents_readme_audit.py`** — required folder-level `AGENTS.md` / `README.md` present; no forbidden drift literals in audited trees.
- **`tests/test_python_api_coverage.py`** — every public `src/` identifier documented in `docs/reference/python_api*.md`.
- **`tests/test_project_wide_hyperlinks.py`** — no broken relative links project-wide.
- **`tests/test_veridical_status_doc.py`** — `veridical_status.md` table ↔ `labels.yaml` theorem registry aligned on kinds, numbers, statuses, Lean modules.
- **`tests/test_claim_strength_table.py`** — S07 claim-strength legend ↔ `methods_and_assumptions.md` evidence ladder.

### Manual cross-doc consistency

| Surface | Finding | Severity |
| --- | --- | --- |
| Publication URL | `manuscript/config.yaml`, README, AGENTS, abstract, CONTRIBUTING all use `https://github.com/docxology/policy_entanglement` | OK |
| `publication.doi` | Empty by design; `validate_manuscript` publication-metadata gate accepts pending DOI | Intentional open |
| ActiveInferenceInstitute URLs | Present only as **upstream** citations (`fep_lean`, `GeneralizedNotationNotation`) in lean docs, citations.yaml, S05, FAQ — not mistaken for this repo's canonical URL | OK |
| `docs/reference/lean_reference.md` vs `labels.yaml` | Automated theorem-map and veridical-status tests enforce alignment; manual spot-check of decomposition row matches MathlibProofs + boundary split | OK |
| `src/gnn/`, `src/reporting/` | No folder-level `AGENTS.md` (not in required audit set per `test_agents_readme_audit.py`) | Informational |
| `docs/modules/*.md` | May lag newest GNN surface; API coverage tests pass for public symbols | Informational |
| `docs/_audit/`, `docs/CHANGELOG.md` | Exempt from count gates; historical round narrative only | OK |

### Transient blocking issue (resolved)

Initial `make readiness` failed at **ruff import-order** on five files (`regression_gate.py`, `regression_pytest.py`, `readiness.py`, `validation_cli.py`, `variables_sidecars.py`). Local `uvx ruff check --fix` restored a clean tree matching commit `5e7be2d`; subsequent lint, mypy, and readiness report steps passed. No source edits required beyond formatter normalization on unrelated files already in the worktree.

---

## 3 — Manuscript claim findings

### Mechanical binding (automated — all green)

- No unresolved `[[FIG/EQ/VAR/SECREF/THMREF/LEAN]]` tokens in source or rendered leak scan.
- No hard-coded grid sizes / seeds / λ lists outside registry injection (validate_manuscript hardcoded-numeric gate).
- Citations resolve via `citations.yaml`; theorem refs partition headline buckets (`test_h1_headline_invariant.py`).
- Lean companions extract to S05; every registered companion resolves (`test_veridicality.py`).
- Witness rows conform to typed contracts with numeric corroboration (`test_witness_conformance.py`).
- Mathlib keystone integrity + foundational-only axiom audit pass.

### Section-priority content review (manual)

| Section | Assessment |
| --- | --- |
| `0A_abstract.md` | Claim-strength ledger, Float↔ℝ open bridge, Mathlib vs boundary split, correct repo URL — aligned with veridical_status |
| `1A_part1_introduction.md`, `1B_motivation.md` | No stale "candidate track" language for pymdp/GNN |
| `2D_decomposition.md`, `S01_proof_of_decomposition_theorem.md` | Honest boundary vs MathlibProofs proved split; no over-claim on Float companion |
| `3B_lean_formalization.md`, `S05_lean_code_skeleton.md`, `S06_notation_and_concordance.md` | Four-track concordance enforced by tests; fep_lean link is upstream catalog reference |
| `4B_empirical_suite.md`, `4C_pymdp_harness.md`, `4E_pymdp_validation.md` | pymdp tracks described as shipped with sidecar gates |
| `6C_discussion_and_outlook.md` | Anti-meta trim holds; FEP/AIF framed as normative frame not direct biological validation |
| `S08_gnn_generalized_notation_extension.md` | Fifth track explicitly **empirical/structural**, not proof-promoting; round-trip VAR bound; open OQ-G2 noted honestly |

### Prose vs ledger

- **Float↔ℝ bridge:** SYNTAX.md and abstract/discussion consistently scope as roadmap/open; `FloatRealResidualWitness.lean` registered as boundary — no prose claiming closure.
- **GNN fifth track:** S08 states shipped parser, round-trip, Lean typed-contract emitter; does not promote theorem rows — matches `veridical_status.md` and regression sidecars.
- **No `??` or `[?]`** in combined PDF intermediates (log grep clean).

---

## 4 — Known intentional open items

| Item | Status | Gate behavior |
| --- | --- | --- |
| Zenodo DOI | `publication.doi` empty in `config.yaml` | Publication metadata gate allows pending DOI with populated `repository_url` |
| Float↔ℝ formal bridge | Open interface; residual witness sidecar | Documented in abstract, SYNTAX, methods_and_assumptions |
| Audit matrix CSV | Stub (1 row) in claim-strength machinery | Not blocking; expand in Round 11 |
| OQ-G2 (S08 heterogeneous-stream Triple Play annotation) | Explicitly "not yet specified" | Open question, not a shipped claim |

---

## 5 — Recommended Round 11 follow-ups

1. **Expand audit matrix CSV** beyond the single stub row so claim-strength tables bind more prose rows mechanically.
2. **Optional `src/gnn/AGENTS.md`** — document parser / runner / lean_emit module boundaries (informational; not in required folder set).
3. **Refresh `docs/modules/*.md`** if GNN public surface grows beyond current API doc subsections.
4. **DOI mint** — human step when Zenodo deposit is ready; gates already wired for post-mint validation.

---

## 6 — Sign-off

| Success criterion (plan) | Met |
| --- | --- |
| Phase 1 commands green | Yes |
| Doc drift tests green | Yes (31/31) |
| Claim-contract tests green | Yes (78/78) |
| No contradictory publication metadata | Yes |
| Audit report filed | This document |

**Verdict:** Documentation and manuscript claims are **consistent with live implementation and gates** at commit `5e7be2d`. No blocking doc or claim failures remain after the ruff normalization during readiness re-run.

---

## 7 — Supersession (2026-05-26, publication DOI + audit matrix + Float interval witness)

Follow-on work from the *Publication DOI, Full Audit Matrix, Docs Sweep, and Float Bridge* plan (same audit snapshot file; historical §1–§6 preserved).

| Item | Change |
| --- | --- |
| Zenodo DOI | Live: `10.5281/zenodo.20301239` in config, CFF, README/AGENTS/docs hubs, abstract/introduction; `publication_metadata.py` forbids pending-DOI prose on current-facing paths |
| Claim audit matrix | `docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv` regenerated (28 rows: 21 registry theorems + 7 cross-track rows); `scripts/generate_audit_matrix.py --write/--check` |
| Float interval witness | `src/manuscript/float_real_interval.py` → bracket fields in `float_real_residual.json`; documented in `methods_and_assumptions.md` §2 as Tier **N** corroboration (not route (b) discharged) |
| Folder docs | `src/gnn/`, `src/reporting/` AGENTS/README added; hub AGENTS updated with DOI + matrix pointer |

Re-run gates: `make readiness`, doc-drift bundle, HOW_TO_VERIFY §4 claim-contract bundle (see updated `release_readiness.json` after readiness completes).

