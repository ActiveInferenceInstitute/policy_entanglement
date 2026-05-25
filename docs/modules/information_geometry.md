# Information geometry of the entanglement manifold

How the framework lives on a *dually-flat statistical manifold* in the
sense of Amari [2000, 2016].  Manuscript section:
[`../manuscript/2F_geometry.md`](../../manuscript/2F_geometry.md).

## Setup

* Let $\mathcal{M}$ be the manifold of all (strictly positive) joint
  distributions on the finite policy space $\Pi$.
* Let $\mathcal{M}_{\mathrm{MF}} \subset \mathcal{M}$ be the
  *mean-field submanifold* — joints that factorize as
  $q(\pi) = \prod_k q^k(\pi^k)$.
* Two dual coordinate systems: **e-coordinates**
  ($\theta = \log q$) and **m-coordinates**
  ($\eta = \mathbb{E}_q[\cdot]$).

## Five structural facts

### 1. Mean-field submanifold is e-flat (Prop 7.1)

The set of MF distributions is closed under exponential mixtures: log
of a convex combination of MF distributions, plus a normalizing
constant, is again MF.

* Lean: `mfImage_isMeanField` (proved at boundary form: every
  `mfToJoint m` is mean-field by construction).
* Python: implicit (predicate `is_mean_field`).

### 2. m-projection minimizes KL (Prop 7.2)

For any joint `q`, the closest mean-field is the product of its
marginals:

$$
\prod_{k=1}^{K} q^k \;=\; \arg\min_{p \in \mathcal{M}_{\mathrm{MF}}}\, D_{\mathrm{KL}}(q \,\|\, p).
$$

* Lean: `mProjection_kl_eq_self_when_meanfield` (boundary; Mathlib supplies
  `kl_div_nonneg` + log-product expansion).
* Python: `m_projection_minimises_kl(q, candidate_marginals)` — tested
  against random Dirichlet samples.

### 3. Total correlation = KL to m-projection (Prop 7.3)

$$
I(q) \;=\; D_{\mathrm{KL}}\!\left(q \,\big\|\, \prod_{k=1}^{K} q^k\right).
$$

This re-expresses total correlation as the KL distance from `q` to
its m-projection — a *non-negativity* witness for `I(q)`.

* Lean: `totalCorrelation_eq_kl_to_mprojection` (witness-consuming
  boundary form: the caller supplies `klToMProj` and the algebraic
  identity `hWitness : sumStreamEntropies − shannonEntropy q s =
  klToMProj`, and the fragment discharges it by `unfold
  totalCorrelation; exact hWitness` — not a bare `rfl`; the full
  identity needs Mathlib's KL chain rule).
* Python: `total_correlation_via_kl(q)` — tested to match
  `total_correlation(q)` to floating tolerance.

### 4. {q_λ} is an exponential geodesic (Theorem 7.4)

The family of λ-entangled posteriors traces an *e-geodesic* through
the manifold: log-probabilities are affine in λ for each fixed π
(up to the normalizer):

$$
\log q_\lambda(\pi) \;=\; a(\pi) + b(\pi)\cdot\lambda - \log Z(\lambda),
$$

with $a(\pi) = \log E(\pi)$ and $b(\pi) = J(\pi) - \gamma\,K_c(\pi)$.

* Lean: `entangledFamily_eGeodesic` (proved by forwarder to
  `Coupling.couplingLogWeight_affine_in_lam`).
* Python: `is_e_geodesic(J, K_c, γ, π_index, lams)` — tested at every
  vertex of the K=2 Ising joint.

### 5. Pythagorean theorem (Prop 7.5)

For any joint `q` and any mean-field reference `q_0`:

$$
D_{\mathrm{KL}}(q \,\|\, q_0) \;=\; I(q) \;+\; D_{\mathrm{KL}}\!\left(\prod_k q^k \,\big\|\, q_0\right).
$$

The "departure from MF" splits cleanly into a *non-MF* component
(`I(q)`, residual entanglement) and an *MF-to-MF* component (KL
between marginal products).

* Lean: `dualFlat_pythagorean_witness` (witness form; takes the
  Mathlib-supplied identity `klVal = tcVal + residual` as a parameter
  and certifies it; the analytic content belongs in the separate
  additive `MathlibProofs` layer, where a row-specific witness
  construction can derive it from the KL chain rule).
* Python: `pythagorean_residual(q, mf_reference)` — tested to be
  ≈ 0 for random Dirichlet joints.

## Revertibility

Any joint can be *reverted* to its mean-field representation by
m-projection.  This is the central philosophical commitment of the
framework: coupling is never structural, always parametric.

* Lean: not in the current boundary fragment; revertibility is
  delivered at the predicate level via `IsMeanField` (existence of
  factorizing `m`).
* Python: `revertibility(q)` returns `m_projection(q)`.

## Why this matters

The dual-flat picture is the *right* place to think about the
mean-field deformation.  In particular:

* The λ-deformation is a **straight line in e-coordinates**, so we
  inherit clean convexity / convergence guarantees.
* The Pythagorean identity decomposes the deviation cleanly into
  meaningful pieces (TC and MF-to-MF KL).
* m-projection gives a unique, differentiable retraction to the MF
  submanifold — important for ablation / safety arguments.

## Where to look

* Lean: [`Geometry.lean`](../../lean/ActinfPolicyEntanglement/Geometry.lean).
* Python: [`geometry.py`](../../src/lean/geometry.py).
* Tests: [`test_geometry.py`](../../tests/test_geometry.py).
