# Information Geometry of the Entanglement Manifold

## Dual coordinates and the mean-field submanifold

Equip the simplex of joint distributions on $\Pi$ with the standard dually-flat structure [@amari-nagaoka-2000; @amari-2016]:

- *e*-affine (exponential) coordinates: natural parameters $\theta$ of an exponential family.
- *m*-affine (mixture) coordinates: expectation parameters $\eta = \nabla \psi(\theta)$ where $\psi$ is the log-partition.
- Riemannian metric: Fisher information.
- Canonical divergence: $D_{\mathrm{KL}}$.

The mean-field submanifold $\mathcal{M}_{\mathrm{MF}} \subset \mathcal{M}$ is the set of product distributions on $\Pi$. Standard facts:

**[[THMREF:prop_6_1]].** $\mathcal{M}_{\mathrm{MF}}$ is *e-flat* in $\mathcal{M}$: closed under exponential geodesics (interpolations affine in log-probability).

**[[THMREF:prop_6_2]] (m-projection / marginalization).** For any $q \in \mathcal{M}$, the *m-projection* onto $\mathcal{M}_{\mathrm{MF}}$ is given by taking marginals:
$$\hat{m}(q) = \prod_k q^k = \arg\min_{p \in \mathcal{M}_{\mathrm{MF}}} D_{\mathrm{KL}}(q\,\|\,p).$$

**[[THMREF:prop_6_3]] (Total correlation as Bregman divergence to projection).**
$$I(q) = D_{\mathrm{KL}}(q\,\|\,\hat m(q)).$$

Hence the multi-information appearing in [[THMREF:thm_4_1]] is precisely the Bregman divergence from the joint posterior to its mean-field projection — the geometric "departure" from the mean-field surface.

The Lean companions for these three propositions are auto-extracted
from the live source under
[`lean/ActinfPolicyEntanglement/Geometry.lean`](../lean/ActinfPolicyEntanglement/Geometry.lean)
and
[`lean/ActinfPolicyEntanglement/FreeEnergy.lean`](../lean/ActinfPolicyEntanglement/FreeEnergy.lean):

[[LEAN:prop_6_1]]

[[LEAN:prop_6_2]]

[[LEAN:prop_6_3]]

## The lambda-family is an e-geodesic

**[[THMREF:thm_6_4]].** The family $\{q_\lambda\}_{\lambda \in \mathbb{R}}$ is an *e-geodesic* in $\mathcal{M}$: $\log q_\lambda(\pi)$ is affine in $\lambda$ up to the normalizing constant. The geodesic departs $\mathcal{M}_{\mathrm{MF}}$ at $\lambda = 0$ in the direction defined by $J - \gamma K_c$.

**Proof.** $\log q_\lambda(\pi) = \sum_k \log E_k(\pi^k) - \gamma\sum_k G_k(\pi^k) + \lambda(J(\pi) - \gamma K_c(\pi)) - \log Z(\lambda)$. The function $\pi \mapsto \log q_\lambda(\pi) + \log Z(\lambda)$ is affine in $\lambda$ for each fixed $\pi$. ∎

The Lean companion (proved by forwarding to the linearity lemma in
`Coupling.lean`):

[[LEAN:thm_6_4]]

The affineness is straightforwardly observable numerically (see
[[EQREF:e_geodesic]]): at every $\pi$ the unnormalised log-weight
traces a *straight line* in $\lambda$ with slope
$J(\pi) - \gamma K_c(\pi)$.

[[FIG:log_weight_flow]]

The same geodesic is also visible in a *low-dimensional summary plane*:
projecting the K=2 Ising joint onto its aligned-corner mass and
off-diagonal disparity traces a curve that departs the mean-field
anchor at $\lambda = 0$ and bends monotonically toward an archetypal
corner.

[[FIG:kl_geodesic_simplex]]

This places the framework in an exceptionally well-developed geometric setting. Concretely:

- **Revertibility** = m-projection. To revert an entangled posterior to mean-field, marginalize. This is an analytic, differentiable operation. The framework predicts that biological systems should be able to recover marginal behavioral statistics from coupled policies, and this is what is empirically observed in factor-isolation experiments.
- **Manifold envelope.** The "envelope" of joint distributions reachable with bounded coupling-potential norm is a tubular neighborhood of $\mathcal{M}_{\mathrm{MF}}$ in the Fisher metric, of radius proportional to $\lambda \cdot \|J - \gamma K_c\|$.
- **[[THMREF:prop_6_5]] (Pythagorean decomposition).** For any joint $q$,
by the dually-flat Pythagorean theorem (see [[EQREF:pythagorean]]),
$D_{\mathrm{KL}}(q \,\|\, q_0^*)$ splits orthogonally into the
"departure from MF" term $I(q)$ and the "MF-to-MF distance" term
$D_{\mathrm{KL}}(\hat m(q) \,\|\, q_0^*)$, where $q_0^*$ is any
reference mean-field distribution.

The Lean companion for [[THMREF:prop_6_5]] (sketch placeholder; the
genuine identity requires the KL chain rule from Mathlib):

[[LEAN:prop_6_5]]

## Connection to alpha-projections and curved exponential families

For $\alpha \in [-1, 1]$, the $\alpha$-projection generalizes the $m$ ($\alpha = -1$) and $e$ ($\alpha = 1$) projections [@amari-2016]. The mean-field approximation in classical variational inference is *m-projection* of the true posterior onto $\mathcal{M}_{\mathrm{MF}}$ (minimize KL with $q$ as second argument, which is what variational lower bounds compute, modulo a sign convention). Our $\lambda$-family is the *e-geodesic in the opposite direction*: starting from MF and moving outward along a chosen direction.

This duality is the deep reason the framework is well-behaved: we are not approximating a fixed target; we are *parametrically extending* the variational family to admit structure, and the m/e geometry guarantees that revertibility (back to MF) is the dual move to extension.

## Connection to escort distributions and deformed exponential families

For non-extensive entropies (Tsallis, Rényi), one obtains *escort distributions* and *$\phi$-deformed exponential families* [@naudts-2011; @amari-2016]. The same construction works for $q_\lambda$: replacing $\exp$ with a deformed exponential gives a $q$-deformed entanglement family. We do not develop this fully here, but flag it as a natural generalization for systems exhibiting non-extensive statistics, and note that DAF's interest in connections to the Cognitive Integrity Framework and to information-theoretic measures of partial integration suggest this as a productive direction.

---
