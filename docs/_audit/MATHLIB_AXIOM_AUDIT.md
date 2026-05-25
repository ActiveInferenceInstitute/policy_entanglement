# MathlibProofs ℝ-keystone axiom audit — static witness

> **Dated reproducible witness** so a reviewer can confirm the manuscript's
> central formal-verification claim *without* rebuilding Lean+Mathlib. This is a
> committed snapshot; the live gate is `scripts/build_mathlib_proofs.py` (run on
> the automatic pytest path by `tests/test_mathlib_axiom_audit.py` whenever the
> Lean toolchain is present — fail-closed on any non-foundational axiom).

- **Audit date:** 2026-05-24
- **Command:** `uv run python scripts/build_mathlib_proofs.py`
- **Exit code:** `0`
- **Toolchain:** `leanprover/lean4:v4.29.0` + Mathlib (the `lean/MathlibProofs/` package)
- **Result:** all 9 keystone theorems `#print axioms` foundational-only — i.e. only
  `propext`, `Classical.choice`, `Quot.sound` (no `sorryAx`, no `native_decide`,
  no project-introduced axiom).

## Verbatim `#print axioms` output (this run)

```
info: MathlibProofs.lean: 'MathlibProofs.free_energy_decomposition_full' depends on axioms: [propext, Classical.choice, Quot.sound]
info: MathlibProofs.lean: 'MathlibProofs.multiInformation_nonneg_at_joint' depends on axioms: [propext, Classical.choice, Quot.sound]
info: MathlibProofs.lean: 'MathlibProofs.streamMarginal_pos' depends on axioms: [propext, Classical.choice, Quot.sound]

>>> #print axioms audit (keystone theorems must be foundational-only)
OK  MathlibProofs builds, clean local hygiene, and 9 keystone theorem(s) #print-axioms
    foundational-only (streamMarginal_productDist, logDiv_prod_separates, klReal_nonneg,
    klReal_split_via_intermediate, klReal_minimises_generalK,
    entanglement_decomposition_generalK, free_energy_decomposition_full,
    streamMarginal_pos, multiInformation_nonneg_at_joint)
```

## What this certifies (and what it does not)

- **Certifies:** the full S01 free-energy decomposition identity for the genuine
  entangled posterior (`free_energy_decomposition_full`) and its supporting
  general-K kernel are machine-checked in ℝ with no `sorry`/`sorryAx` and no
  non-foundational axiom. The capstone uses `m := ∏ₛ streamMarginal q s` (not
  `m := q`); `hmarg` is discharged internally (`streamMarginal_productDist`), so
  it is not a load-bearing antecedent.
- **Does NOT certify:** the executable Float pipeline. The Float↔ℝ bridge between
  this real proof and the Float-arithmetic Python layer is the single open
  verification-stack residual (genuine multi-week Lean research; never to be
  fabricated). See `docs/reference/methods_and_assumptions.md` and the manuscript
  abstract / §3A "What is proved."
- **Faithfulness:** registry `status: proved` distinguishes 2 substantive rows
  (`cor_4_2`, `cor_4_3`) from 3 statement-restricted rows (`prop_6_1`, `prop_6_2`,
  `prop_7_1`); see `docs/reference/veridical_status.md`. This axiom audit is about
  the ℝ analytic keystone, which is `boundary` status with the ℝ discharge
  documented on `thm_4_1`.
