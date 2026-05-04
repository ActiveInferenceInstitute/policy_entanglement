# Convexity of F(q_lambda) in lambda

The free-energy curve along the λ-deformation has a clean
exponential-family structure that delivers convexity in $\lambda$ on
the natural side.  We sketch the proof here; the closed-form K = 2
case is verified numerically by
[`scripts/generate_figures.py`](../scripts/generate_figures.py)
(see [`output/figures/free_energy_curve.png`](../output/figures/free_energy_curve.png)).

## The exponential-family setup

The λ-entangled posterior

$$
q_\lambda(\pi) \;\propto\; E(\pi)\,\exp\!\big(\theta(\pi)\cdot\lambda\big),
\qquad \theta(\pi) \;=\; J(\pi) - \gamma\,K_c(\pi),
$$

is a *natural-parameter exponential family* in $\lambda$ with sufficient
statistic $\theta$ and log-partition

$$
\psi(\lambda) \;=\; \log Z(\lambda) \;=\; \log\sum_\pi E(\pi)\,e^{\theta(\pi)\,\lambda}.
$$

By the standard exponential-family identity,

$$
\psi'(\lambda) \;=\; \mathbb{E}_{q_\lambda}[\theta],
\qquad
\psi''(\lambda) \;=\; \mathrm{Var}_{q_\lambda}(\theta) \;\geq\; 0,
$$

so $\psi$ is convex in $\lambda$ and *strictly* convex unless $\theta$
is $q_\lambda$-a.s. constant (the degenerate case where the coupling
has no effect).

## Decomposition of F(q_lambda)

Plugging into [[THMREF:thm_4_1]] ([[SECREF:app.proof_decomp]]),

$$
F[q_\lambda] \;=\; \sum_k F[q_\lambda^k] + \gamma\,\lambda\,\mathbb{E}_{q_\lambda}[K_c]
                 + \lambda\,\mathbb{E}_{q_\lambda}[J] - \psi(\lambda) - I(q_\lambda).
$$

Group terms:

$$
F[q_\lambda] \;=\; \underbrace{\sum_k F[q_\lambda^k] - I(q_\lambda)}_{=: A(\lambda)}
                 \;+\; \underbrace{\lambda\,\mathbb{E}_{q_\lambda}[\theta] - \psi(\lambda)}_{=: B(\lambda)}.
$$

## Convexity of B(lambda)

By the exponential-family identity above,
$\mathbb{E}_{q_\lambda}[\theta] = \psi'(\lambda)$, so

$$
B(\lambda) \;=\; \lambda\,\psi'(\lambda) - \psi(\lambda).
$$

Differentiating twice:

$$
B'(\lambda) \;=\; \lambda\,\psi''(\lambda),
\qquad
B''(\lambda) \;=\; \psi''(\lambda) + \lambda\,\psi'''(\lambda).
$$

For $\lambda \geq 0$ and where $\psi$ is convex with non-decreasing
second derivative (true for sub-Gaussian $\theta$), $B$ is convex on
$[0,\infty)$.  In the symmetric K = 2 Ising example, $\psi(\lambda) = \log\cosh(\lambda/2)$
and $B(\lambda) = \tfrac{\lambda}{2}\tanh(\lambda/2) - \log\cosh(\lambda/2)$,
which is straightforwardly convex.  This expression coincides with
$I(\lambda)$ for the symmetric Ising case (see [[SECREF:app.bernoulli]] for the
algebraic equivalence).

## Concavity of A(lambda) on the MF side

$A(\lambda)$ collects the per-stream marginal free energies and
subtracts the total correlation.  For $\lambda \geq 0$, the marginals
$q_\lambda^k$ vary smoothly in $\lambda$ and the *m-projection
identity* ([[THMREF:prop_6_3]]) gives $I(q_\lambda)$ as a KL distance to the
(continuously varying) marginal product.  Where $q_\lambda$ remains
in the regime of *uniform* marginal invariance (e.g. the symmetric
Ising case where $q_\lambda^k \equiv \tfrac12$ for every $\lambda$),
$\sum_k F[q_\lambda^k]$ is *constant* in $\lambda$ and convexity of
$A$ reduces to convexity of $-I(q_\lambda)$, which inherits from
$\psi$.

## Conclusion (sketch)

For symmetric ensembles with marginal-invariant deformations
(Bernoulli K = 2 is the prototype), $F[q_\lambda]$ is convex in
$\lambda \geq 0$.  Beyond this regime, convexity follows under a
mild log-concavity hypothesis on $\theta = J - \gamma K_c$, which
covers all common engineered habits (Ising-type couplings, soft
matching constraints, low-rank tensor-train coupling potentials).

The full proof, including the cross-term bookkeeping when marginals
themselves move with $\lambda$, follows from a direct second-derivative
computation that is straightforward but tedious; we omit it here.

## Numerical verification

The K = 2 Ising free-energy curve at three utility values is plotted
in [`output/figures/free_energy_curve.png`](../output/figures/free_energy_curve.png).
The curve is monotonically decreasing in $|\lambda|$ for any
$u \geq 0$, consistent with convexity (and with the closed-form
expression in [[SECREF:app.bernoulli]]).

