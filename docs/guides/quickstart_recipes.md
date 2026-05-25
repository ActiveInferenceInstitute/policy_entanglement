# Quickstart recipes

Copy-paste recipes for the most common tasks in this project.  All
commands assume the project's working directory is
`projects/actinf_policy_entanglement_lean/`.

## Compile the Lean boundary fragment

```bash
cd lean && lake build
```

Expected output: `Build completed successfully (22 jobs).`

(The 22 jobs include the 17 `ActinfPolicyEntanglement.*` submodules —
Basic, BernoulliToy, Constructive, Convexity, Coupling,
Decomposition, FreeEnergy, Geometry, Heterogeneous, JointDist,
MarkovBlanket, Monotonicity, Scalar, Spectral,
SpectralWitnesses, ConnectionsWitnesses —
the `ActinfPolicyEntanglement` root, the
`FepSketches.PolicyEntanglementBoundary` re-export, the `FepSketches`
root, and two Lake-internal targets.)

## Run the Python test suite

```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
```

Expected output: live collection count from `output/reports/test_results.json` (≥ 95 % coverage on
`src/`).[^test-count]  The test budget grows over time;
see [`reference/statistics_reference.md`](../reference/statistics_reference.md)
section 7 for the live per-suite breakdown and
[`reference/veridical_status.md`](../reference/veridical_status.md) for
the authoritative pass / coverage tally.

[^test-count]: Value at the time of writing.  Live query:
    `cd projects/actinf_policy_entanglement_lean && uv run pytest --co -q | tail -1`.

## Render the manuscript PDF

From the project root:

```bash
uv run python scripts/build_pdf.py
uv run python scripts/validate_pdf.py
```

Outputs: `projects/actinf_policy_entanglement_lean/output/pdf/actinf_policy_entanglement_lean_combined.pdf`,
plus the per-section slide PDFs and HTML files (one per section file
under `manuscript/`; current count is **21 numbered body sections**
(`1B`, `1C`, `2B`–`2J`, `3B`, `4B`–`4E`, `5B`–`5D`, `6B`, `6C`) plus
6 part dividers (`1A_`, `2A_`, …, `6A_`), `0A_abstract.md`,
`99_bibliography.md`, and 7 supplementary appendices `S01_…`–`S07_…`).

## Run every analysis script in one shot

```bash
uv run python scripts/run_all.py
```

This runs all analysis / validation scripts in canonical order —
`build_lean.py`, `generate_figures.py`, `dump_archetypes.py`,
`parameter_sweep.py`, `simulate_pymdp.py`,
`simulate_multi_k.py` (round 3), `simulate_long_horizon.py` (round 3),
`simulate_revertibility.py` (round 3), `simulate_robustness.py`,
`simulate_btai.py`, `simulate_adversarial.py`,
`manuscript_variables.py`, `build_dashboard.py`,
`generate_index.py`, `generate_theorem_map.py`,
`inject_manuscript_variables.py`, `validate_outputs.py`, and
`validate_manuscript.py`, then `regression_gate.py` — as a CI-style
gate.  The live count is exposed in the manuscript as
`[[VAR:run_all_script_count]]`.

## Inspect the K = 2 Ising mutual information at a single λ

```python
from lean.bernoulli_toy import ising_mutual_information, empirical_mutual_information
print("closed-form:", ising_mutual_information(1.5))
print("empirical:  ", empirical_mutual_information(1.5))
```

## Compute the entanglement decomposition for a custom joint

```python
import numpy as np
from lean.decomposition import entanglement_decomposition_rhs

q = np.array([[0.4, 0.1], [0.2, 0.3]])
mf = [np.array([0.6, 0.4]), np.array([0.6, 0.4])]
G  = [np.zeros(2), np.zeros(2)]
J  = np.array([[0.5, -0.5], [-0.5, 0.5]])
Kc = np.zeros((2, 2))
terms = entanglement_decomposition_rhs(q, mf, G, J, Kc, gamma=1.0, lam=0.5)
print("Σ F[q^k]:    ", terms.sum_marginal_free_energies)
print("γ·λ·E[K_c]:  ", terms.coupling_cost_term)
print("logZ − λ·E[J]:", terms.coupling_prior_term)
print("I(q):        ", terms.multi_information_term)
print("total:       ", terms.total)
```

## Verify the m-projection minimizes KL (Prop 7.2)

```python
import numpy as np
from lean.geometry import m_projection_minimises_kl

rng = np.random.default_rng(seed=42)
q   = rng.dirichlet(np.ones(6)).reshape(2, 3)
candidate = [np.array([0.5, 0.5]), np.array([0.4, 0.4, 0.2])]
print(m_projection_minimises_kl(q, candidate))   # True
```

## Verify the e-geodesic property (Theorem 7.4)

```python
from lean.geometry import is_e_geodesic
import numpy as np

J  = np.array([[0.5, -0.5], [-0.5, 0.5]])
Kc = np.array([[0.1, -0.2], [-0.3, 0.4]])
print(is_e_geodesic(J, Kc, gamma=1.0, pi_index=(0, 0), lams=[-1.0, 0.0, 1.0, 2.0]))   # True
```

## Test the O(λ²) coupling-tax bound (Theorem 9.1)

```python
import numpy as np
from lean.heterogeneous import (
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
uv run python scripts/build_pdf.py
uv run python scripts/validate_pdf.py
```

## Find every Lean theorem that still carries `sorry`

```bash
grep -rn 'sorry' lean/ActinfPolicyEntanglement/*.lean
```

Expected: **0 strict `sorry`** in the boundary fragment — the
17 boundary submodules under
[`lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/)
all compile and type-check on stock Lean 4 v4.29.0. The substantive
stock-Lean algebraic subset is proved in the boundary fragment, while
analytic content outside the stock-Lean boundary is exposed as
witness-consuming theorems rather than `sorry` placeholders. The
fragment exposes 76
public theorems / lemmas, 11 structures, 39 defs (126 total
declarations).  Non-current Mathlib pseudo-code is not rendered in the
manuscript or shipped as source; the roadmap records analytic targets
and witness-payload scope only.
The per-theorem status table lives in
[`../reference/lean_reference.md`](../reference/lean_reference.md);
the Mathlib refinement plan (witness-payload-discharge roadmap; **0
deferred theorems remain** as of round 3) is in
[`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md);
the hygiene gate is enforced by
[`../../scripts/build_lean.py`](../../scripts/build_lean.py).

## Add a new manuscript section

1. Create the file with a numeric prefix that puts it in the desired
   render order (e.g. `04a_new_topic.md`).
2. Top heading is a single `#` (Pandoc → `\section{}`); subsections
   use `##`.  No hardcoded section numbers in headings.
3. List the new file in [`../manuscript/README.md`](../../manuscript/README.md).
4. Re-render with `scripts/build_pdf.py` and validate with `scripts/validate_pdf.py`.
