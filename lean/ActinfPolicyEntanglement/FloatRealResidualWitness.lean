/- `ActinfPolicyEntanglement.FloatRealResidualWitness` — machine-readable
   Float↔ℝ residual scaffold (roadmap / witness row, not a closed bridge).

   The shipped Float pipeline is corroborated numerically by dashboard
   invariants and Monte-Carlo concentration tests; this module records
   the caller-supplied residual bounds as a typed witness shell without
   claiming a Flocq-style IEEE-754 or interval-arithmetic proof. -/

namespace ActinfPolicyEntanglement

/-- **Boundary witness for Float↔ℝ residual audit**: caller-supplied
worst-case decomposition residual, Monte-Carlo MI concentration radius,
and capstone conjunct tolerance.  Values are populated from
`output/reports/float_real_residual.json` on each pipeline run. -/
structure FloatRealResidualWitness where
  max_decomposition_residual : Float
  montecarlo_mi_concentration_radius : Float
  capstone_conjunct_tolerance : Float
  montecarlo_mi_closed_form : Float
  montecarlo_mi_sample_mean : Float

/-- **Witness form (roadmap row)**: re-publishes the supplied residual
fields; does not discharge Float↔ℝ equivalence. -/
theorem floatRealResidual_witness (w : FloatRealResidualWitness) :
    w.max_decomposition_residual = w.max_decomposition_residual
      ∧ w.montecarlo_mi_concentration_radius = w.montecarlo_mi_concentration_radius
      ∧ w.capstone_conjunct_tolerance = w.capstone_conjunct_tolerance
      ∧ w.montecarlo_mi_closed_form = w.montecarlo_mi_closed_form
      ∧ w.montecarlo_mi_sample_mean = w.montecarlo_mi_sample_mean :=
  ⟨rfl, rfl, rfl, rfl, rfl⟩

end ActinfPolicyEntanglement
