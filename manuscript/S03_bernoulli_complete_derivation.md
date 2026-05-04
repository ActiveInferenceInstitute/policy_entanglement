# K=2 Bernoulli — Complete Derivation

Reproduces the calculation in [[SECREF:examples.bernoulli]] with full algebra.  Companion code:
[`src/lean/bernoulli_toy.py`](../src/lean/bernoulli_toy.py); Lean boundary:
[`lean/ActinfPolicyEntanglement/BernoulliToy.lean`](../lean/ActinfPolicyEntanglement/BernoulliToy.lean).

## Setup

Two binary streams $\pi^1, \pi^2 \in \{0,1\}$ with symmetric Bernoulli($\tfrac12$)
mean-field marginals
$E_1(\pi^1) = E_2(\pi^2) = \tfrac12$, zero per-stream EFE, and the
*swing-1 Ising* coupling

$$
J(\pi^1,\pi^2) \;=\; \mathbf{1}[\pi^1 = \pi^2] - \tfrac12,
\qquad J \in \{+\tfrac12,-\tfrac12\}.
$$

## Joint posterior

The unnormalised joint at coupling $\lambda$ is
$\tilde q_\lambda(\pi) = \tfrac14\,\exp(\lambda\,J(\pi))$.  The normaliser is

$$
Z(\lambda) \;=\; \tfrac14\big(2 e^{\lambda/2} + 2 e^{-\lambda/2}\big)
\;=\; \tfrac12\,(e^{\lambda/2}+e^{-\lambda/2})
\;=\; \cosh(\lambda/2).
$$

Hence the normalised joint:

$$
q_\lambda(\pi^1=\pi^2) \;=\; \frac{e^{\lambda/2}}{4\cosh(\lambda/2)},
\qquad
q_\lambda(\pi^1\ne\pi^2) \;=\; \frac{e^{-\lambda/2}}{4\cosh(\lambda/2)}.
$$

The *aligned mass* (sum over the two aligned atoms) is

$$
P_a(\lambda) \;\equiv\; q_\lambda(\pi^1=\pi^2) \cdot 2
\;=\; \frac{e^{\lambda/2}}{2\cosh(\lambda/2)}
\;=\; \frac{1}{1+e^{-\lambda}}
\;=\; \sigma(\lambda).
$$

## Marginals (uniform by symmetry)

By inspection, summing over $\pi^2$:

$$
q_\lambda^1(\pi^1=0) = \tfrac12 P_a + \tfrac12(1-P_a) = \tfrac12,
\qquad q_\lambda^1(\pi^1=1) = \tfrac12.
$$

Marginals are uniform Bernoulli($\tfrac12$) for any $\lambda$ —
*marginal invariance* of the Ising deformation.

## Joint and marginal entropies

Using natural log throughout:

$$
H(q_\lambda^k) \;=\; \log 2 \quad (k=1,2).
$$

For the joint, the four atoms have masses
$\{P_a/2, P_a/2, (1-P_a)/2, (1-P_a)/2\}$, so

$$
H(q_\lambda) \;=\; -2\cdot\frac{P_a}{2}\log\frac{P_a}{2}
                 \;-\;2\cdot\frac{1-P_a}{2}\log\frac{1-P_a}{2}.
$$

Expand:

$$
H(q_\lambda) \;=\; -P_a(\log P_a - \log 2) - (1-P_a)(\log(1-P_a) - \log 2)
             \;=\; H_b(P_a) + \log 2,
$$

where $H_b(p) = -p\log p - (1-p)\log(1-p)$.

## Closed-form mutual information

By definition $I(q_\lambda) = \sum_k H(q_\lambda^k) - H(q_\lambda)$:

$$
\boxed{\;
I(\lambda) \;=\; 2\log 2 - H_b(\sigma(\lambda)) - \log 2
\;=\; \log 2 - H_b(\sigma(\lambda)).\;}
$$

Equivalently, using the identities
$\log\big((1+e^\lambda)/2\big) = \log\cosh(\lambda/2) + \lambda/2$
and $\sigma - \tfrac12 = \tfrac12\tanh(\lambda/2)$, one obtains the
**second canonical form**

$$
I(\lambda) \;=\; \tfrac{\lambda}{2}\,\tanh(\lambda/2)\;-\;\log\cosh(\lambda/2).
$$

This is the form that appears naturally in [[SECREF:app.convexity]]'s
exponential-family decomposition (where $\psi(\lambda) =
\log\cosh(\lambda/2)$ is the log-partition).  The two forms are
algebraically identical; we use whichever is more convenient.

Sanity checks:

* $\lambda = 0$: $\sigma(0) = \tfrac12$, $H_b(\tfrac12) = \log 2$, so
  $I(0) = 0$ ✓ (mean-field).
* $\lambda \to \infty$: $\sigma(\lambda) \to 1$, $H_b \to 0$, so
  $I \to \log 2$ ✓ (saturation at one-bit alignment).
* Even in $\lambda$: $\sigma(-\lambda) = 1 - \sigma(\lambda)$ and
  $H_b$ is symmetric around $p = \tfrac12$, so $I(-\lambda) = I(\lambda)$ ✓.
* Numerical: at $\lambda = 1$, $I(1) = \log 2 - H_b(\sigma(1)) \approx 0.1109$;
  $\tfrac{1}{2}\tanh(0.5) - \log\cosh(0.5) \approx 0.1109$ ✓.

## Optimal coupling lambda* from a target alignment

Define the **expected alignment** of the joint posterior as

$$
\alpha(\lambda) \;\equiv\; 2\sigma(\lambda) - 1 \;=\; \tanh(\lambda/2),
$$

ranging from $0$ at $\lambda = 0$ (uniform) to $\pm 1$ at $\lambda \to \pm\infty$
(perfectly aligned / anti-aligned).  Given a *target alignment*
$\Delta \in (-\Delta_{\max}, \Delta_{\max})$ with $\Delta_{\max} = 1$,
inverting $\alpha(\lambda) = \Delta$ yields

$$
\boxed{\;\lambda^*(\Delta) \;=\; 2\,\mathrm{arctanh}\!\big(\Delta/\Delta_{\max}\big).\;}
$$

This is the closed-form coupling that *realises* the target alignment
$\Delta$; it is the inverse of the alignment–coupling correspondence,
not a Lagrangian first-order condition.

* $\Delta = 0 \Rightarrow \lambda^* = 0$ (mean-field).
* $\Delta \to \pm\Delta_{\max} \Rightarrow \lambda^* \to \pm\infty$
  (frozen archetypes).

**Connection to the comparative-statics objective.** If instead one
seeks the $\lambda$ that maximises a *Lagrangian* of the form
$\Delta\,\alpha(\lambda) - \kappa\,I(\lambda)$ (utility-times-alignment
minus a multi-information cost with multiplier $\kappa > 0$), the
first-order condition gives a different formula: the slope of the
multi-information balances the slope of the alignment.  This is the
Lagrange-balance regime studied numerically in
[`scripts/parameter_sweep.py`](../scripts/parameter_sweep.py).  In
either interpretation, $\lambda^*$ inherits saturation at
$\Delta_{\max}$ and monotonicity in $\Delta$.

## Free-energy curve

With utility scalar $u$ giving the surplus per aligned outcome
($u = \Delta$ in the optimisation above),

$$
F(\lambda) \;=\; -\,u\,(2\sigma(\lambda)-1) \;-\; I(\lambda),
$$

monotonically decreasing in $|\lambda|$ for $u \geq 0$.  See
[`output/figures/free_energy_curve.png`](../output/figures/free_energy_curve.png).

## Numerical cross-check

The Python companion verifies every identity above to floating
tolerance (`< 1e-9`) at five values of $\lambda \in \{0, 0.5, 1, 2, 4\}$:

* `test_empirical_mi_matches_closed_form` — $I(\lambda) = $ TC of $q_\lambda$.
* `test_ising_mutual_information_zero_at_zero` — $I(0) = 0$.
* `test_ising_mutual_information_saturates_to_log2` — $I(50) \approx \log 2$.
* `test_ising_mutual_information_even_in_lambda` — symmetry.
* `test_optimal_lambda_*` — closed-form $\lambda^*(\Delta)$.

Run them with:
```bash
uv run pytest tests/test_bernoulli_toy.py -v
```
