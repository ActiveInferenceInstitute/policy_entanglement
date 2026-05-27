# Thermo-Nuclear Code Quality Review — v1 closure

**Project:** `actinf_policy_entanglement_lean`  
**Code baseline:** `8b41085` (thermo re-audit follow-up)  
**Docs baseline:** `85a8224` (v1 deep doc sweep)  
**Review date:** 2026-05-26  
**Scope A:** `float_real_interval.py`, `audit_matrix.py`, `variables.py`, `invariants.py`, `publication_metadata.py`  
**Scope B:** docs-only diff `8b41085..85a8224` (13 files, +62/−13)

---

## Verdict: **APPROVE**

v1 code is ship-ready. Interval witness is honestly Tier-N (not Flocq); sham longdouble and tautological contains flag are removed; audit matrix is collapsed into a single module. Docs diff is signposting-only with no claim regression.

---

## Findings (priority order)

| ID | Severity | Location | Finding |
| --- | --- | --- | --- |
| F1 | Informational | `float_real_interval.py:52-55`, `variables.py:84-95` | `decomposition_invariant_within_interval` is a **wiring integrity** check (same sweep + positive Decimal margin), not independent corroboration. Tier-N / roadmap labeling is correct. |
| F2 | Optional | `variables.py:85-87` | `build_float_real_residual` runs `decomposition_sweep_points` twice (direct + inside `decomposition_invariants`). Single-sweep refactor would delete redundant grid work. |
| F3 | Optional | `float_real_interval.py:46-48` | `decomposition_interval_worst_lambda` tracks max float residual, not max margin-widened upper bound. |
| F4 | Optional | `variables.py:81-83` | `project_root` parameter on `build_float_real_residual` is unused. |
| F5 | Optional | `publication_metadata.py:14-22` | `LEGACY_*` / `UNRESOLVED_*` alias layer is backward-compat sprawl; consolidate post-v1. |
| F6 | Low (mitigated) | `audit_matrix.py:38-44` | Silent fallback to `test_veridical_status_doc.py`; drift test `test_audit_matrix_no_silent_veridical_fallback` mitigates. |
| F7 | Clean | `invariants.py:304-368` | Shared `decomposition_sweep_points` is the right structural move; file under 1k lines. |
| F8 | Doc nit | `manuscript/AGENTS.md` | Duplicate `0A` phrasing in section-count bullet (fixed in closure commit). |

---

## Required fixes

None for v1 ship.

---

## Optional post-ship polish

- F2: single sweep in `build_float_real_residual`
- F3: align worst-λ metadata with interval peak or rename field
- F4: remove or wire `project_root`
- F5: deprecation window for redundant publication aliases
- Tests: negative case where `invariant_max_residual` is wrong → `within` is `False`

---

## Scope B — doc diff (`8b41085..85a8224`)

**APPROVE.** Pure signposting: §8 v1 audit snapshot, supersession notes, package lists, S01–S08 range, claim-matrix pointers. No over-claim of interval witness beyond Tier-N.

---

## Applied (post-v1 thermo polish)

| ID | Status | Change |
| --- | --- | --- |
| F2 | **Closed** | `decomposition_invariants_from_points`; single sweep in `build_float_real_residual` |
| F3 | **Closed** | `decomposition_interval_worst_lambda` tracks margin-widened interval peak |
| F4 | **Closed** | Removed unused `project_root` from `build_float_real_residual()` |
| F5 | **Closed** | Removed `LEGACY_*` / `UNRESOLVED_*` aliases; `CANONICAL_*` only in `__all__` |
| Test | **Closed** | `test_decomposition_interval_bracket_rejects_inflated_invariant` |

**Ship @ `86b9557`:** `make readiness` exit 0; `validate_pdf.py` pass; 1473 passed / 1 skipped; 95.02% coverage; combined PDF under `output/pdf/`.

---

## Post-polish re-verdict (`4b312d4..86b9557`)

**Verdict:** **APPROVE**

Optional findings F2–F5 are closed with structural refactors only: `decomposition_invariants_from_points` eliminates the redundant sweep; `decomposition_interval_worst_lambda` tracks the margin-widened peak in one pass; dead API surface (`project_root`, legacy publication aliases) is removed; tests add the negative inflated-invariant case and pin worst-λ to the interval peak.

| ID | Severity | Location | Finding |
| --- | --- | --- | --- |
| F1′ | Informational (carry-forward) | `float_real_interval.py`, `variables.py` | `decomposition_invariant_within_interval` remains a same-sweep wiring check — Tier-N labeling correct. |
| NP1 | Informational | `tests/test_audit_matrix_and_float_interval.py` | Worst-λ test inlines margin math; acceptable isolation, minor drift risk if formula changes. |

No new blockers. Review date: 2026-05-27.

---

## Related

- Prior round review: [`THERMO_NUCLEAR_REVIEW_2026-05-25.md`](THERMO_NUCLEAR_REVIEW_2026-05-25.md)
- Doc audit §8: [`DOC_MANUSCRIPT_AUDIT_2026-05-26.md`](DOC_MANUSCRIPT_AUDIT_2026-05-26.md)
- Root ledger: [`ISA.md`](../../ISA.md) v1 ship closure
