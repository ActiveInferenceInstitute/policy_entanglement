# Closing

The framework introduced here has four properties that we believe make it worth investing in:

1. **Theoretical economy.** A single coupling parameter recovers the mean-field baseline, the hierarchical AIF limit, the sophisticated-inference recursion, and a continuum of intermediate structures.

2. **Decomposition theorem.** The free-energy decomposition ([[THMREF:thm_4_1]]) gives a clean accounting of when coupling pays for itself — a result that is both analytically tractable and biologically interpretable.

3. **Geometric principle.** The framework lives on a dually-flat manifold and traces an e-geodesic away from the mean-field submanifold. Revertibility is m-projection. Phase structure is symmetry-breaking on the entanglement manifold.

4. **Lean-formalizability.** The constructions are built from objects already in mathlib, and the core theorems are stated in a form amenable to incremental formalization. We project [[THMREF:thm_4_1]] as a 2-month Lean target.

The work plan, ordered: (i) the Lean type-level statement of [[THMREF:thm_4_1]] is in place at [`lean/ActinfPolicyEntanglement/Decomposition.lean`](../lean/ActinfPolicyEntanglement/Decomposition.lean) — proof refinement to a fully discharged Mathlib-backed proof is the Phase 7 task tracked in [`docs/reference/phase7_plan.md`](../docs/reference/phase7_plan.md); (ii) the $K=2$ closed-form simulation is implemented in [`src/lean/bernoulli_toy.py`](../src/lean/bernoulli_toy.py) and exercised by 18 tests in [`tests/test_bernoulli_toy.py`](../tests/test_bernoulli_toy.py); (iii) write the manuscript along the [[SECREF:companion_paper]] outline (this is the manuscript); (iv) integrate the framework into the AII GEO-INFER and Codomyrmex repositories as a structuring principle for multi-agent coordination; (v) explore the open questions in [[SECREF:open_questions]] in collaboration with interested parties.

The framework is offered in the spirit of conceptual hygiene and constructive extension: it does not displace existing tools but situates them, and does not preclude embodiment-based architectures but provides a parametric alternative against which they can be compared.

---
