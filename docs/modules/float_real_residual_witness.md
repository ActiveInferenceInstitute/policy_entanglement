# FloatRealResidualWitness — Float↔ℝ residual scaffold

Manuscript section:
[`../manuscript/3B_lean_formalization.md`](../../manuscript/3B_lean_formalization.md)
(§3B formal-verification treatment) and the roadmap row
`roadmap_float_real_residual` in
[`../manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml).

Lean source:
[`FloatRealResidualWitness.lean`](../../lean/ActinfPolicyEntanglement/FloatRealResidualWitness.lean).

## Role in the boundary fragment

`FloatRealResidualWitness` is the 17th boundary submodule and the
typed-API home of the **Float↔ℝ residual audit**.  The shipped
pipeline computes in `Float` (and pymdp/JAX float32), while the
machine-checked free-energy identity
(`MathlibProofs.free_energy_decomposition_full`) is a proof in `ℝ`.
The gap between the two number systems is a genuine, precisely-scoped
research item (Lean `Float` is opaque `@[extern]`; the two sound
routes are a Flocq-style IEEE model or an interval
re-implementation).  This module does **not** close that gap: it
records the caller-supplied residual bounds as a typed witness shell
without claiming an IEEE-754 or interval-arithmetic proof.

## Witness structure

```lean
structure FloatRealResidualWitness where
  max_decomposition_residual : Float
  montecarlo_mi_concentration_radius : Float
  capstone_conjunct_tolerance : Float
  montecarlo_mi_closed_form : Float
  montecarlo_mi_sample_mean : Float
```

The fields are populated on each pipeline run from
`output/reports/float_real_residual.json` (the structure's
`max_decomposition_residual` corresponds to the JSON's
`decomposition_lhs_eq_rhs_max_residual`; the other four fields map
to same-named JSON keys).

## Theorem

```lean
theorem floatRealResidual_witness (w : FloatRealResidualWitness) :
    w.max_decomposition_residual = w.max_decomposition_residual
      ∧ w.montecarlo_mi_concentration_radius = w.montecarlo_mi_concentration_radius
      ∧ w.capstone_conjunct_tolerance = w.capstone_conjunct_tolerance
      ∧ w.montecarlo_mi_closed_form = w.montecarlo_mi_closed_form
      ∧ w.montecarlo_mi_sample_mean = w.montecarlo_mi_sample_mean :=
  ⟨rfl, rfl, rfl, rfl, rfl⟩
```

As a witness-form (roadmap) row, it re-publishes the supplied
residual fields; the underlying Float↔ℝ equivalence is **not**
discharged here.  The numeric corroboration for the shipped Float
pipeline lives in the dashboard invariants and the Monte-Carlo
concentration tests — see
[`../reference/veridical_status.md`](../reference/veridical_status.md)
and the residual-tracking tests in
[`../tests/test_meta_files_and_float_residual.py`](../../tests/test_meta_files_and_float_residual.py).

## See also

- [`../reference/lean_reference.md`](../reference/lean_reference.md) — per-theorem status table
- [`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md) — witness-payload-discharge plan (the Float↔ℝ bridge is the stated unbuilt residual)
