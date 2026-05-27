# Audit Snapshots

This directory holds dated, evidence-preserving audit artifacts that
support current documentation and manuscript claims.

Files here are intentionally historical. Do not rewrite old evidence to
make it match current status; add a newer snapshot or a supersession note
when the live method stack changes. Current-facing claims belong in
`README.md`, `AGENTS.md`, `docs/reference/`, `manuscript/`, and generated
reports under `output/reports/`.

**Supersession (v1 closure @ `85a8224`):** removed transient ISA shards
`ISA_20260522_workplan_implement.md` (abandoned workplan) and
`ISA_20260524_gnn_fifth_track.md` (GNN outcomes live in code, S08, and
root `ISA.md`). See [`DOC_MANUSCRIPT_AUDIT_2026-05-26.md`](DOC_MANUSCRIPT_AUDIT_2026-05-26.md) §8 and root
[`ISA.md`](../../ISA.md) v1 ship closure.

**Supersession (post-v1 thermo polish @ `86b9557`):** closed optional findings
F2–F5 from the v1 thermo closure review; see Applied section in
[`THERMO_NUCLEAR_REVIEW_2026-05-26_v1_closure.md`](THERMO_NUCLEAR_REVIEW_2026-05-26_v1_closure.md)
and [`DOC_MANUSCRIPT_AUDIT_2026-05-26.md`](DOC_MANUSCRIPT_AUDIT_2026-05-26.md) §9.

| Snapshot | Role |
| --- | --- |
| [`DOC_MANUSCRIPT_AUDIT_2026-05-26.md`](DOC_MANUSCRIPT_AUDIT_2026-05-26.md) | Full doc-drift + claim-contract gate sweep; §8 v1 gate snapshot; §9 post-polish snapshot |
| [`pymdp_lean_manuscript_matrix_2026-05-21.csv`](pymdp_lean_manuscript_matrix_2026-05-21.csv) | Live claim audit matrix (28 rows; regenerate via `scripts/generate_audit_matrix.py --write`) |
| [`MATHLIB_AXIOM_AUDIT.md`](MATHLIB_AXIOM_AUDIT.md) | Dated static `#print axioms` witness for MathlibProofs keystone (referee-readable without rebuild) |
| [`THERMO_NUCLEAR_REVIEW_2026-05-25.md`](THERMO_NUCLEAR_REVIEW_2026-05-25.md) | Round-7–10 code-quality audits + applied fixes (superseded by v1 closure review) |
| [`THERMO_NUCLEAR_REVIEW_2026-05-26_v1_closure.md`](THERMO_NUCLEAR_REVIEW_2026-05-26_v1_closure.md) | v1 ship thermo-nuclear sign-off @ `8b41085` / `85a8224`; post-polish F2–F5 closed @ `86b9557` |
| [`FOUR_SKILL_ASSESSMENT_2026-05-19.md`](FOUR_SKILL_ASSESSMENT_2026-05-19.md) | Pass-2 RedTeam deferred-item disposition (FAQ/CHANGELOG reference) |
| [`ISA_20260525_robustness_cluster.md`](ISA_20260525_robustness_cluster.md) | Round-9 robustness cluster module boundaries |
