# Information Geometry: Geodesics, Flatness, and Pythagorean Decomposition

## Dual coordinates and the mean-field submanifold

Equip the simplex of joint distributions on $\Pi$ with the standard dually-flat structure [@amari-1985; @amari-nagaoka-2000; @amari-2016]:

- *e*-affine (exponential) coordinates: natural parameters $\theta$ of an exponential family.
- *m*-affine (mixture) coordinates: expectation parameters $\eta = \nabla \psi(\theta)$ where $\psi$ is the log-partition.
- Riemannian metric: Fisher information.
- Canonical divergence: $D_{\mathrm{KL}}$.

The mean-field submanifold $\mathcal{M}_{\mathrm{MF}} \subset \mathcal{M}$ is the set of product distributions on $\Pi$. Standard facts:

**[[THMREF:prop_6_1]].** $\mathcal{M}_{\mathrm{MF}}$ is *e-flat* in $\mathcal{M}$: closed under exponential geodesics (interpolations affine in log-probability).  The Lean companion `Geometry.mfImage_isMeanField` machine-checks only the *definitional membership* $\textsf{IsMeanField}(\textsf{mfToJoint}\,m)$ (every product distribution is mean-field, by `rfl`); it does **not** discharge the e-flatness / closure-under-log-mixtures identity, which is the open real-analytic content scoped to the separate Mathlib layer (registry `status: proved` but `faithfulness: statement-restricted` — see `docs/reference/veridical_status.md`).

**[[THMREF:prop_6_2]] (m-projection / marginalization).** For any $q \in \mathcal{M}$, the *m-projection* onto $\mathcal{M}_{\mathrm{MF}}$ is given by taking marginals:
$$\hat{m}(q) = \prod_k q^k = \arg\min_{p \in \mathcal{M}_{\mathrm{MF}}} D_{\mathrm{KL}}(q\,\|\,p).$$

**[[THMREF:prop_6_3]] (Total correlation as Bregman divergence to projection).**
$$I(q) = D_{\mathrm{KL}}(q\,\|\,\hat m(q)).$$

Hence the multi-information appearing in [[THMREF:thm_4_1]] is
precisely the Bregman divergence from the joint posterior to its
mean-field projection — the geometric "departure" from the mean-field
surface.  Two corollaries follow immediately and are useful intuition
pumps for the rest of the manuscript:

* **Non-negativity.**  $I(q) \geq 0$ with equality iff $q$ is
  mean-field, recovering the entropy sub-additivity inequality
  $H(q) \leq \sum_k H(q^k)$ as the *expanded form* of [[EQREF:total_correlation]].
* **Pythagorean intuition.**  Because $\hat m(q)$ is the m-projection
  of $q$ onto $\mathcal{M}_{\mathrm{MF}}$, $I(q)$ is the *closest-point*
  KL distance from $q$ to the mean-field surface; everything farther
  on $\mathcal{M}_{\mathrm{MF}}$ is recovered by the Pythagorean
  decomposition [[EQREF:pythagorean]] below.

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

**Proof.** Expand $\log q_\lambda(\pi)$ using the definition of the
$\lambda$-entangled prior $\mathcal{E}_\lambda$ and the Gibbs form
[[SECREF:lambda_deformation.entangled_posterior]]: the only
$\lambda$-dependent terms are $\lambda J(\pi)$ and the normalizer
$\log Z(\lambda)$. Subtracting $\log Z(\lambda)$ — which is independent
of $\pi$ — leaves the e-geodesic identity

[[EQ:e_geodesic]]

so $\pi \mapsto \log q_\lambda(\pi) + \log Z(\lambda)$ is affine in
$\lambda$ at every fixed $\pi$ with slope $J(\pi) - \gamma K_c(\pi)$. ∎

The Lean companion (proved by forwarding to the linearity lemma in
`Coupling.lean`):

[[LEAN:thm_6_4]]

The affineness is straightforwardly observable numerically (see
[[EQREF:e_geodesic]]): at every $\pi$ the unnormalized log-weight
traces a *straight line* in $\lambda$ with slope
$J(\pi) - \gamma K_c(\pi)$.

[[FIG:log_weight_flow]]

The same geodesic is also visible in a *low-dimensional summary plane*
([[FIGREF:kl_geodesic_simplex]]): projecting the K=2 Ising joint onto
its aligned-corner mass and off-diagonal disparity traces a curve that
departs the mean-field anchor at $\lambda = 0$ and bends monotonically
toward an archetypal corner.

[[FIG:kl_geodesic_simplex]]

This places the framework in an exceptionally well-developed geometric setting. Concretely:

- **Revertibility** = m-projection. To revert an entangled posterior to mean-field, marginalize. This is an analytic, differentiable operation. The framework therefore predicts that marginal behavioral statistics are recoverable from coupled policies by the same projection used in the model; factor-isolation experiments are the right empirical design for testing that recovery rather than evidence that the biological system explicitly performs this operation.
- **Manifold envelope.** The "envelope" of joint distributions reachable with bounded coupling-potential norm is a tubular neighborhood of $\mathcal{M}_{\mathrm{MF}}$ in the Fisher metric, of radius proportional to $\lambda \cdot \|J - \gamma K_c\|$.
- **[[THMREF:prop_6_5]] (Pythagorean decomposition).** For any joint
$q$ and any reference mean-field distribution $q_0^*$, the dually-flat
Pythagorean theorem gives

[[EQ:pythagorean]]

so $D_{\mathrm{KL}}(q \,\|\, q_0^*)$ splits orthogonally into the
"departure from MF" term $I(q)$ and the "MF-to-MF distance" term
$D_{\mathrm{KL}}(\hat m(q) \,\|\, q_0^*)$ — see also [[EQREF:pythagorean]].

The Lean companion for [[THMREF:prop_6_5]] is a witness-consuming
boundary form: the caller supplies the dual-flat Pythagorean
decomposition as a structural witness (`dualFlat_pythagorean_witness`).
The current manuscript claims that typed contract plus the numerical
revertibility witness; the Mathlib4 discharge target is the finite-KL
chain rule and Bregman-divergence identity.

[[LEAN:prop_6_5]]

## Connection to alpha-projections and curved exponential families

For $\alpha \in [-1, 1]$, the $\alpha$-projection generalizes the $m$ ($\alpha = -1$) and $e$ ($\alpha = 1$) projections [@amari-2016]. The mean-field approximation in classical variational inference is *m-projection* of the true posterior onto $\mathcal{M}_{\mathrm{MF}}$ (minimize KL with $q$ as second argument, which is what variational lower bounds compute, modulo a sign convention cataloged in [[SECREF:notation.sign_conventions]]). Our $\lambda$-family is the *e-geodesic in the opposite direction*: starting from MF and moving outward along a chosen direction.

This duality is the deep reason the framework is well-behaved: we are not approximating a fixed target; we are *parametrically extending* the variational family to admit structure, and the m/e geometry guarantees that revertibility (back to MF) is the dual move to extension.

## Connection to escort distributions and deformed exponential families

For non-extensive entropies (Tsallis, Rényi), one obtains *escort distributions* and *$\phi$-deformed exponential families* [@naudts-2011; @amari-2016]. The same construction works for $q_\lambda$: replacing $\exp$ with a deformed exponential gives a $q$-deformed entanglement family. We do not develop this fully here, but flag it as a natural generalization for systems exhibiting non-extensive statistics, with an evident connection to information-theoretic measures of partial cognitive integration.

## Takeaways

> **1. The mean-field submanifold is e-flat.**
> Mean-field policy posteriors form an e-flat submanifold of the
> probability simplex ([[THMREF:prop_6_1]]); the $\lambda$-family
> *departs* this submanifold along an e-geodesic ([[THMREF:thm_6_4]]).
> (The boundary Lean companion checks only definitional mean-field
> membership; full e-flatness is the Mathlib-layer discharge target —
> `prop_6_1` is `status: proved`, `faithfulness: statement-restricted`.)
>
> **2. Marginalization is exactly m-projection.**
> Taking marginals is the KL-minimizing projection onto the
> mean-field submanifold ([[THMREF:prop_6_2]]) — *revertibility is
> dual to extension*. (The boundary companion pins the m-projection's
> KL value on the submanifold; information-projection minimality is the
> Mathlib-layer discharge target — `faithfulness: statement-restricted`.)
>
> **3. Pythagorean decomposition makes the cost explicit.**
> Total correlation $I(q_\lambda)$ equals the KL of $q_\lambda$ to
> its m-projection ([[THMREF:prop_6_3]]) — the multi-information cost
> in the decomposition theorem is *exactly* the squared "distance"
> from the mean-field manifold in the dual geometry.

---
