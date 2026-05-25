# K = 2 Bernoulli / Ising worked example

Manuscript section:
[`../manuscript/2E_examples.md`](../../manuscript/2E_examples.md) and
Appendix C
[`../manuscript/S03_bernoulli_complete_derivation.md`](../../manuscript/S03_bernoulli_complete_derivation.md).

## Convention note

The Bernoulli toy module uses the *appendix swing-½* convention:

$$
J(\pi^1, \pi^2) \;=\; \mathbf{1}[\pi^1 = \pi^2] \;-\; \tfrac{1}{2} \;\in\; \{\pm\tfrac{1}{2}\}
$$

with normalized prior $E_{MF} = \tfrac14$ on each of the 4 atoms.  The
manuscript body (§2E) uses the bilinear convention

$$
J \;=\; J_0\,(2\pi^1 - 1)(2\pi^2 - 1) \;\in\; \{\pm J_0\};
$$

the two are related by $\lambda_{\text{body}} \cdot J_0 =
\lambda_{\text{app}} / 2$, so $\lambda_{\text{app}} = 2\,J_0\,\lambda_{\text{body}}$.
The closed-form mutual information identity has equivalent forms in
both conventions (see manuscript
[`S03`](../../manuscript/S03_bernoulli_complete_derivation.md) for the
full reconciliation).  Below we work in the appendix swing-½
convention throughout.

## Setup

Two binary streams $\pi^1, \pi^2 \in \{0, 1\}$, symmetric Bernoulli(½)
mean-field marginals, zero EFE, and a swing-1 Ising coupling

$$
J(\pi^1, \pi^2) \;=\; \mathbf{1}[\pi^1 = \pi^2] \;-\; \tfrac{1}{2}.
$$

Aligned outcomes $(0,0)$ and $(1,1)$ get $J = +\tfrac{1}{2}$;
misaligned outcomes get $J = -\tfrac{1}{2}$.

## Closed-form posterior

The unnormalized joint at coupling $\lambda$ is
$0.25 \cdot \exp(\lambda \cdot J)$.  Normalizing gives the simple
form: each aligned atom gets probability $\tfrac{1}{2}\sigma(\lambda)$
and each misaligned atom gets $\tfrac{1}{2}(1-\sigma(\lambda))$, where
$\sigma(\lambda) = 1/(1+e^{-\lambda})$.

Marginals are uniform Bernoulli(½) by symmetry.

## Closed-form mutual information

$$
\boxed{\;
I(\lambda) \;=\; \log 2 \;-\; H_b\!\big(\sigma(\lambda)\big)
\;}
$$

with binary entropy $H_b(p) = -p \log p - (1-p)\log(1-p)$.  The
function

* equals 0 at $\lambda = 0$ (mean-field);
* is even in $\lambda$;
* is monotonically increasing in $|\lambda|$;
* saturates at $\log 2$ as $|\lambda| \to \infty$.

Implementations:

* Lean: `BernoulliToy.isingMutualInformation` (boundary; `floatExp` /
  `floatLog` stubs become `Real.exp` / `Real.log` under the Mathlib
  refinement — see [`MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)).
* Python: `ising_mutual_information(λ)` — closed form, plus
  `empirical_mutual_information(λ)` as a numeric cross-check from the
  posterior.  Tests verify they agree to floating tolerance.

The figure
[`../output/figures/ising_mi_curve.png`](../../output/figures/ising_mi_curve.png)
overlays the closed form and the empirical TC, demonstrating they
match across the entire λ ∈ [0, 6] range.

## Closed-form optimal coupling

Given a *utility surplus* $\Delta$ for aligned outcomes (capped at
$\Delta_{\max}$), the optimal coupling that maximizes
$\Delta \cdot \mathbb{E}_q[J] - I(q)$ is

$$
\lambda^*(\Delta) \;=\; 2\,\mathrm{arctanh}(\Delta / \Delta_{\max}).
$$

It is zero at $\Delta = 0$, monotonic in $\Delta$, and diverges as
$\Delta \to \pm\Delta_{\max}$.

* Lean: `BernoulliToy.optimalLambda` (def-level; uses
  `floatArctanh = ½·log((1+x)/(1-x))`, will swap to `Real.arctanh`
  under the Mathlib refinement).
* Python: `optimal_lambda(δ, δ_max)`.

Figure: [`../output/figures/optimal_lambda.png`](../../output/figures/optimal_lambda.png).

## Free-energy curve

$$
F(\lambda) \;=\; -\,\mathrm{utility}\cdot\big(2\sigma(\lambda)-1\big) \;-\; I(\lambda),
$$

monotonically decreasing in $|\lambda|$ for any $\mathrm{utility} \geq 0$
(and approaching the saturation value $-\,\mathrm{utility} - \log 2$
as $\lambda \to \infty$).

Figure: [`../output/figures/free_energy_curve.png`](../../output/figures/free_energy_curve.png).

## Phases (illustrative thresholds)

`coupling_phase_at(λ, λc1, λc2)` partitions the λ-axis into three
phases following the manuscript §10 picture:

* `disordered` for $\lambda < \lambda_{c}^{(1)}$;
* `mixed` ("skilled") for $\lambda_c^{(1)} \leq \lambda \leq \lambda_c^{(2)}$;
* `frozen` for $\lambda > \lambda_c^{(2)}$.

The default thresholds (0.5, 2.5) are *illustrative* — real critical
couplings depend on the model.  Figure:
[`../output/figures/phase_diagram.png`](../../output/figures/phase_diagram.png).

## Where to look

* Lean: [`BernoulliToy.lean`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean).
* Python: [`bernoulli_toy.py`](../../src/lean/bernoulli_toy.py).
* Tests: [`test_bernoulli_toy.py`](../../tests/test_bernoulli_toy.py).
* Figures: `output/figures/{ising_mi_curve, optimal_lambda, free_energy_curve, phase_diagram}.png`.
