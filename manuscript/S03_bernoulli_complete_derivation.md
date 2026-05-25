# Complete Derivation: Two-Stream Bernoulli Toy

Closed-form derivations of the multi-information $I(\lambda)$, the
*alignment-inversion* coupling
$\lambda^\star(\Delta_{\mathrm{align}}) = 2\,\operatorname{arctanh}(\Delta_{\mathrm{align}}/\Delta_{\max})$,
and the closed-form free-energy curve.  Appendix scaling gives
$I(\lambda) = (\lambda/2)\tanh(\lambda/2) - \log\cosh(\lambda/2)
            = \log 2 - H_b(\sigma(\lambda))$;
*not* $I(\lambda) = \log\cosh\lambda$ (which would be a derivation error).

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

The unnormalized joint at coupling $\lambda$ is
$\tilde q_\lambda(\pi) = \tfrac14\,\exp(\lambda\,J(\pi))$.  The normalizer is

$$
Z(\lambda) \;=\; \tfrac14\big(2 e^{\lambda/2} + 2 e^{-\lambda/2}\big)
\;=\; \tfrac12\,(e^{\lambda/2}+e^{-\lambda/2})
\;=\; \cosh(\lambda/2).
$$

Hence the normalized joint:

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
* Numerical: at $\lambda = 1$,
  $I(1) = \log 2 - H_b(\sigma(1)) \approx [[VAR:ising_mi_at_lam_1:.4f]]$;
  $\tfrac{1}{2}\tanh(\tfrac{1}{2}) - \log\cosh(\tfrac{1}{2}) \approx [[VAR:ising_mi_at_lam_1:.4f]]$ ✓.

## Coupling from a target alignment (alignment-inversion, *not* a VFE optimum)

Define the **expected alignment** of the joint posterior as

$$
\alpha(\lambda) \;\equiv\; 2\sigma(\lambda) - 1 \;=\; \tanh(\lambda/2),
$$

ranging from $0$ at $\lambda = 0$ (uniform) to $\pm 1$ at $\lambda \to \pm\infty$
(perfectly aligned / anti-aligned).  Given a *target alignment*
$\Delta_{\mathrm{align}} \in (-\Delta_{\max}, \Delta_{\max})$ with $\Delta_{\max} = 1$,
inverting $\alpha(\lambda) = \Delta_{\mathrm{align}}$ yields

$$
\boxed{\;\lambda^\star(\Delta_{\mathrm{align}}) \;=\; 2\,\operatorname{arctanh}\!\big(\Delta_{\mathrm{align}}/\Delta_{\max}\big).\;}
$$

This is the closed-form coupling that *realizes* the target alignment
$\Delta_{\mathrm{align}}$; it is the **inverse of the alignment–coupling
correspondence, *not* a free-energy first-order condition.**  We use the
name $\lambda^\star(\Delta_{\mathrm{align}})$ rather than
$\lambda^\star(\Delta_{\mathrm{util}})$ to make this explicit:
$\Delta_{\mathrm{align}}$ is a *target on the alignment axis*, not a
utility surplus.

* $\Delta_{\mathrm{align}} = 0 \Rightarrow \lambda^\star = 0$ (mean-field).
* $\Delta_{\mathrm{align}} \to \pm\Delta_{\max} \Rightarrow \lambda^\star \to \pm\infty$
  (frozen archetypes).

**Connection to actual VFE optimization.** The genuine VFE-optimization
problem in this Bernoulli toy is: given a utility scalar $u$ that pays
$u$ per unit alignment via an EFE term $-u\,\alpha(\lambda)$, minimize
the framework free energy
$F_{\mathrm{VFE}}(\lambda) = -u\,(2\sigma(\lambda) - 1) + I(\lambda) = -u\,\tanh(\lambda/2) + I(\lambda)$
in $\lambda$ — note the $+I$ sign, consistent with the decomposition
theorem [[EQREF:tc_decomp]] in which multi-information enters with a
plus sign (sign conventions in [[SECREF:notation]]).  Using
$\mathrm{d}I/\mathrm{d}\lambda = \tfrac14\,\lambda\,\mathrm{sech}^2(\lambda/2)$
(differentiate the closed form $I = (\lambda/2)\tanh(\lambda/2) - \log\cosh(\lambda/2)$
and simplify with $\mathrm{d}\tanh(\lambda/2)/\mathrm{d}\lambda = \tfrac12\,\mathrm{sech}^2(\lambda/2)$),
the first-order condition is
$-\tfrac{u}{2}\,\mathrm{sech}^2(\lambda/2) + \tfrac{\lambda}{4}\,\mathrm{sech}^2(\lambda/2) = 0$,
which simplifies (since $\mathrm{sech}^2(\lambda/2) > 0$) to
$$
\boxed{\;\lambda^\star_{\mathrm{VFE}}(u) \;=\; 2u.\;}
$$
The second derivative is $\tfrac14\,\mathrm{sech}^2(\lambda/2)$ at $\lambda^\star$
modulo a correction of order $u$ through the chain rule, and is positive
on a neighborhood of $\lambda^\star$, confirming a strict minimum.
Thus the VFE-optimum is *linear* in the utility scalar; the
alignment-inversion formula $2\,\operatorname{arctanh}(u)$ agrees with it
only at small $u$ (Taylor:
$2\,\operatorname{arctanh}(u) = 2u + \tfrac23 u^3 + \cdots$) and
diverges from it as $u \to 1$.  The two should not be conflated:
$\lambda^\star_{\mathrm{VFE}}(u) = 2u$ is the answer to "what coupling
minimizes free energy under utility $u$?", while
$\lambda^\star(\Delta_{\mathrm{align}}) = 2\,\operatorname{arctanh}(\Delta_{\mathrm{align}})$
is the answer to "what coupling realizes a given target alignment
$\Delta_{\mathrm{align}}$?".

**A second, Lagrangian, interpretation.** If instead one seeks the
$\lambda$ that maximizes a *Lagrangian* of the form
$\Delta_{\mathrm{align}}\,\alpha(\lambda) - \kappa\,I(\lambda)$
(utility-times-alignment minus a multi-information cost with multiplier
$\kappa > 0$), the first-order condition gives yet another formula: the
slope of the multi-information balances the slope of the alignment.
This is the Lagrange-balance regime studied numerically in
[`scripts/parameter_sweep.py`](../scripts/parameter_sweep.py).  In every
interpretation, $\lambda^\star$ inherits saturation at $\Delta_{\max}$
and monotonicity in $\Delta_{\mathrm{align}}$, but the three formulas
($2\,\operatorname{arctanh}$, $2u$, Lagrange-balance) are distinct
quantities answering distinct questions.

## Free-energy curve

With utility scalar $u \geq 0$ giving the surplus per aligned outcome,
the toy's *Lagrangian-style scalarisation* of free energy is the
following — note this is a **distinct object** from the framework's
variational free energy $F[q_\lambda]$ of
[[SECREF:app.proof_decomp]]: here multi-information enters with a
**minus** sign (a reward-style scalarisation), whereas the
decomposition theorem's $F[q_\lambda]$ carries $+\,I(q_\lambda)$. The
same glyph $F$ is reused for brevity; the two are reconciled in the
remark immediately below.

$$
F(\lambda) \;=\; -\,u\,(2\sigma(\lambda)-1) \;-\; I(\lambda),
$$

monotonically decreasing in $|\lambda|$ for $u \geq 0$.  See
[`output/figures/free_energy_curve.png`](../output/figures/free_energy_curve.png).
This is a Lagrangian-style scalarisation rather than the framework's
$F[q_\lambda] = \log Z_E(\lambda) - \log Z(\lambda)$ identity from
[[SECREF:app.proof_decomp]]; the genuine VFE minimization in the same
toy with multi-information entering with a *plus* sign gives
$\lambda^\star_{\mathrm{VFE}}(u) = 2u$, derived in the previous
subsection.

## Numerical cross-check

The Python companion verifies every identity above to floating
tolerance (`< [[VAR:bernoulli_verification_tolerance:.0e]]`) at
[[VAR:bernoulli_verification_lambdas_count]] values of
$\lambda \in \{[[VAR:bernoulli_verification_lambdas]]\}$:

* `test_empirical_mi_matches_closed_form` — $I(\lambda)$ equals the TC of $q_\lambda$.
* `test_ising_mutual_information_zero_at_zero` — $I(0) = 0$.
* `test_ising_mutual_information_saturates_to_log2` — $I(50) \approx \log 2$.
* `test_ising_mutual_information_even_in_lambda` — symmetry.
* `test_optimal_lambda_*` — closed-form $\lambda^*(\Delta)$.

Run them with:
```bash
uv run pytest tests/test_bernoulli_toy.py -v
```
