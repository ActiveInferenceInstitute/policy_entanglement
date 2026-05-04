# Quickstart recipes

Copy-paste recipes for the most common tasks in this project.  All
commands assume the project's working directory is
`projects/actinf_policy_entanglement_lean/`.

## Compile the Lean boundary fragment

```bash
cd lean && lake build
```

Expected output: `Build completed successfully (14 jobs).`

## Run the Python test suite

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
```

Expected output: 119 / 119 passing, ≥ 90 % coverage.

## Render the manuscript PDF

From the parent template root:

```bash
cd ../..
uv run python scripts/03_render_pdf.py --project actinf_policy_entanglement_lean
```

Outputs: `projects/actinf_policy_entanglement_lean/output/pdf/actinf_policy_entanglement_lean_combined.pdf`,
plus 25 per-section slide PDFs and 26 HTML files.

## Run every analysis script in one shot

```bash
uv run python scripts/run_all.py
```

This runs `generate_figures.py`, `manuscript_variables.py`,
`dump_archetypes.py`, `parameter_sweep.py`, and finally
`validate_outputs.py` as a CI-style gate.

## Inspect the K = 2 Ising mutual information at a single λ

```python
from src.bernoulli_toy import ising_mutual_information, empirical_mutual_information
print("closed-form:", ising_mutual_information(1.5))
print("empirical:  ", empirical_mutual_information(1.5))
```

## Compute the entanglement decomposition for a custom joint

```python
import numpy as np
from src.decomposition import entanglement_decomposition_rhs

q = np.array([[0.4, 0.1], [0.2, 0.3]])
mf = [np.array([0.6, 0.4]), np.array([0.6, 0.4])]
G  = [np.zeros(2), np.zeros(2)]
J  = np.array([[0.5, -0.5], [-0.5, 0.5]])
Kc = np.zeros((2, 2))
terms = entanglement_decomposition_rhs(q, mf, G, J, Kc, gamma=1.0, lam=0.5)
print("Σ F[q^k]:    ", terms.sum_marginal_free_energies)
print("γ·λ·E[K_c]:  ", terms.coupling_cost_term)
print("λ·E[J] − logZ:", terms.coupling_prior_term)
print("−I(q):       ", terms.total_correlation_gain)
print("total:       ", terms.total)
```

## Verify the m-projection minimises KL (Prop 6.2)

```python
import numpy as np
from src.geometry import m_projection_minimises_kl

rng = np.random.default_rng(seed=42)
q   = rng.dirichlet(np.ones(6)).reshape(2, 3)
candidate = [np.array([0.5, 0.5]), np.array([0.4, 0.4, 0.2])]
print(m_projection_minimises_kl(q, candidate))   # True
```

## Verify the e-geodesic property (Theorem 6.4)

```python
from src.geometry import is_e_geodesic
import numpy as np

J  = np.array([[0.5, -0.5], [-0.5, 0.5]])
Kc = np.array([[0.1, -0.2], [-0.3, 0.4]])
print(is_e_geodesic(J, Kc, gamma=1.0, pi_index=(0, 0), lams=[-1.0, 0.0, 1.0, 2.0]))   # True
```

## Test the O(λ²) coupling-tax bound (Theorem 8.1)

```python
import numpy as np
from src.heterogeneous import (
    InferenceMode, coupling_tax, coupling_tax_within_quadratic_bound
)

mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
G  = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
J  = np.array([[0.5, -0.5], [-0.5, 0.5]])
Kc = np.array([[0.2, -0.1], [-0.1, 0.2]])
modes = [InferenceMode.VFE, InferenceMode.EFE]

# Numerical coupling tax at lambda = 0.1
tax = coupling_tax(mf, G, J, Kc, gamma=1.0, lam=0.1, modes=modes)
print(f"tax(λ=0.1) = {tax:.6e}")

# Bound holds for small λ (with safety factor 2):
ok = coupling_tax_within_quadratic_bound(
    mf, G, J, Kc, gamma=1.0, lam=0.05, modes=modes, safety_factor=2.0,
)
print(f"O(λ²) bound holds: {ok}")
```

## Run a single failing test in isolation

```bash
uv run pytest tests/test_decomposition.py::test_decomposition_consistency_at_zero_lambda -v
```

## Refresh manuscript figures and re-render the PDF

```bash
uv run python scripts/run_all.py
cd ../..
uv run python scripts/03_render_pdf.py --project actinf_policy_entanglement_lean
```

## Find every Lean theorem that still carries `sorry`

```bash
grep -rn 'sorry' lean/ActinfPolicyEntanglement/*.lean
```

Expected: 10 occurrences; per-theorem status table is in
[`lean_reference.md`](../reference/lean_reference.md), Mathlib refinement plan is in
[`../reference/phase7_plan.md`](../reference/phase7_plan.md).

## Add a new manuscript section

1. Create the file with a numeric prefix that puts it in the desired
   render order (e.g. `04a_new_topic.md`).
2. Top heading is a single `#` (Pandoc → `\section{}`); subsections
   use `##`.  No hardcoded section numbers in headings.
3. List the new file in [`../manuscript/README.md`](../../manuscript/README.md).
4. Re-render with `scripts/03_render_pdf.py`.
