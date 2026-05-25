# Module: `FreeEnergy`

Boundary-form definitions of KL divergence, Shannon entropy, total
correlation, and variational free energy on a finite policy space.
Manuscript anchors:
[`../manuscript/2D_decomposition.md`](../../manuscript/2D_decomposition.md)
(uses these quantities to state Theorem 5.1) and
[`../manuscript/2F_geometry.md`](../../manuscript/2F_geometry.md)
(re-expresses the total correlation as a Bregman divergence to the
m-projection — Proposition 7.3).

## Overview

`FreeEnergy` is the *numerical primitives* layer of the boundary
fragment.  Every other Lean module (`Decomposition`, `Geometry`,
`BernoulliToy`, `Heterogeneous`) consumes one or more of its
definitions to state a higher-level identity.  The module is
deliberately Mathlib-free: every quantity is a simple `Float`-valued
reduction over a `Finset`-style finite support that the caller
supplies, so the file compiles on stock Lean 4 v4.29.0.

Mathlib analogs (slated for the Mathlib refinement payload-discharge)
are noted in each definition's docstring; the Mathlib refinement
swaps `Float`/`safeLog` for `Real`/`Real.log` and re-discharges the
boundary forms using `Mathlib.Probability.Entropy.Basic` and
`Mathlib.Analysis.SpecialFunctions.Log.Basic`. See
[`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).

## Definitions provided

| Lean name | Type | Mathematical meaning |
|---|---|---|
| `supportSum` | `List (PolicySpace K Pol) → (PolicySpace K Pol → Float) → Float` | $\sum_{\pi \in s} f(\pi)$ — finite-support reduction. |
| `logFloor` | `Float` (`1e-300`) | Numerical floor used in `safeLog` to avoid `log 0`. |
| `safeLog` | `Float → Float` | `log (max x logFloor)`.  Mathlib analog: `Real.log`. |
| `shannonEntropy` | `JointDist K Pol → List … → Float` | $H(q) = -\sum_\pi q(\pi)\log q(\pi)$. |
| `kl` | `(p q : JointDist K Pol) → List … → Float` | $D_{\mathrm{KL}}(p \| q) = \sum_\pi p(\pi)\big(\log p(\pi) - \log q(\pi)\big)$. |
| `totalCorrelation` | `(q : JointDist K Pol) → (s : List …) → (sumStreamEntropies : Float) → Float` | $I(q) = \sum_k H(q^k) - H(q)$.  Boundary form: caller supplies `sumStreamEntropies = Σ_k H(q^k)`; the fragment returns `sumStreamEntropies - shannonEntropy q s`. |
| `IsNonNegMultiInformation` | `(q : JointDist K Pol) → (s : List …) → (sumStreamEntropies : Float) → Prop` | The predicate `0.0 ≤ totalCorrelation q s sumStreamEntropies` — non-negativity exposed as a witness obligation (discharged by Mathlib KL-non-negativity). |
| `variationalFreeEnergy` | `JointDist K Pol → (logE G : PolicySpace K Pol → Float) → Float → List … → Float` | $F[q] = \gamma\,\mathbb{E}_q[G] - \mathbb{E}_q[\log E] - H(q)$. |
| `marginalFreeEnergy` | per-stream variant on `Pol k → Float` | $F[q^k] = \gamma\,\mathbb{E}_{q^k}[G_k] - \mathbb{E}_{q^k}[\log E_k] - H(q^k)$. |

Nine definitions in total (the seven boundary primitives above plus
`totalCorrelation` and `IsNonNegMultiInformation`).

## Theorems provided

| Lean name | Statement | Status |
|---|---|---|
| `totalCorrelation_def` | `totalCorrelation q s sumStreamEntropies = sumStreamEntropies - shannonEntropy q s` by `rfl` (definitional unfolding). | proved (`rfl`) |
| `totalCorrelation_vanishes_at_meanField` | Given `sumStreamEntropies = shannonEntropy q s`, `totalCorrelation q s sumStreamEntropies = sumStreamEntropies - sumStreamEntropies` (mean-field collapse, proved by `unfold` + `rw`). | proved |
| `totalCorrelation_eq_kl_to_mprojection` | Proposition 7.3 boundary witness form (see below). | witness |

Three theorems in total.

## Key theorem (Proposition 7.3)

`totalCorrelation_eq_kl_to_mprojection` — boundary form of the
identity that registers the total correlation as a KL distance to the
m-projection.  In the manuscript this is **Proposition 7.3** (label
`prop_6_3` in
[`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml),
section anchor `geometry.dual_coords`, status `witness`).

Lean signature:

```lean
theorem totalCorrelation_eq_kl_to_mprojection {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumStreamEntropies klToMProj : Float)
    (hWitness : sumStreamEntropies - shannonEntropy q s = klToMProj) :
    totalCorrelation q s sumStreamEntropies = klToMProj := by
  unfold totalCorrelation
  exact hWitness
```

The boundary fragment proves a *witness-consuming* form: the caller
commits `klToMProj` to a real KL value and supplies the algebraic
identity `hWitness : sumStreamEntropies − shannonEntropy q s =
klToMProj`; the fragment unfolds `totalCorrelation` and forwards the
witness.  The *full* identity

$$
I(q) \;=\; D_{\mathrm{KL}}\!\left(q \,\big\|\, \prod_{k=1}^{K} q^k\right) \;=\; \sum_{k=1}^{K} H(q^k) \;-\; H(q)
$$

requires Mathlib's KL chain rule and log-product expansion; the
Mathlib-refinement plan substitutes those in.  The Python mirror
`total_correlation_via_kl(q)` is *numerically* gated against the
direct sum-of-entropies form `total_correlation(q)` for arbitrary
Dirichlet samples (see
[`test_free_energy.py`](../../tests/test_free_energy.py)).

## Wiring

| Track | Resolves to |
|---|---|
| Manuscript section | [`§7 Information geometry`](../../manuscript/2F_geometry.md), Prop 7.3; also referenced from [`§5 Entanglement decomposition`](../../manuscript/2D_decomposition.md) (Theorem 5.1 consumes `variationalFreeEnergy`). |
| Lean module | [`FreeEnergy.lean`](../../lean/ActinfPolicyEntanglement/FreeEnergy.lean) (9 defs, 3 theorems). |
| Registry label | `prop_6_3` in [`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml) (Prop 7.3, status `witness`, lean name `totalCorrelation_eq_kl_to_mprojection`). |
| Python mirror | [`lean/free_energy`](../../src/lean/free_energy.py) — `shannon_entropy`, `kl_divergence`, `total_correlation`, `total_correlation_via_kl`, `free_energy`, `marginal_free_energy`, plus joint / marginal entropy helpers. |
| Test gate | [`test_free_energy.py`](../../tests/test_free_energy.py); pymdp-grounded version exercised by [`test_simulation_free_energy.py`](../../tests/test_simulation_free_energy.py). |
| Equation tokens | [[EQ:total_correlation]] (declared in registry), consumed by [[EQ:tc_decomp]] (Theorem 5.1). |

## Examples

The Python mirror gives the standard sanity-rail checks:

```python
import numpy as np
from lean.free_energy import (
    shannon_entropy, kl_divergence, total_correlation, total_correlation_via_kl,
)

# Uniform K=2 joint: H = log 4, TC = 0
q_unif = np.full((2, 2), 0.25)
assert abs(shannon_entropy(q_unif) - np.log(4)) < 1e-12
assert abs(total_correlation(q_unif)) < 1e-12

# Mean-field joint with non-uniform marginals: TC = 0
qa = np.outer([0.7, 0.3], [0.4, 0.6])
assert abs(total_correlation(qa)) < 1e-12

# Correlated joint: TC > 0, and the two equivalent formulae agree
rng = np.random.default_rng(seed=42)
qb = rng.dirichlet(np.ones(6)).reshape(2, 3)
assert total_correlation(qb) > 0
assert abs(total_correlation(qb) - total_correlation_via_kl(qb)) < 1e-9

# Self-KL is 0
assert abs(kl_divergence(qb, qb)) < 1e-12
```

## Cross-references

* [`decomposition_theorem.md`](decomposition_theorem.md) — Theorem 5.1
  consumes `variationalFreeEnergy` and `marginalFreeEnergy` from this
  module.
* [`information_geometry.md`](information_geometry.md) — Prop 7.3 is
  one of the five structural facts that anchor the dually-flat
  picture; the m-projection / KL identity is its Bregman-divergence
  reading.
* [`joint_dist.md`](joint_dist.md) — `m_projection`, `joint_marginal`,
  and `joint_marginals` are the supporting primitives consumed by
  `total_correlation_via_kl`.
* [`bernoulli_toy.md`](bernoulli_toy.md) — the closed-form K=2 Ising
  case exercises every helper in this module against an analytic
  ground truth.
* [`../reference/lean_reference.md`](../reference/lean_reference.md) —
  per-theorem status table; the Mathlib refinement roadmap for
  swapping `Float` / `safeLog` for `Real` / `Real.log` lives in
  [`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).
