# Heterogeneous Inference: Mixed VFE/EFE Ensembles and the Coupling-Tax Bound

## Three-level update hierarchy

The framework induces a natural three-level hierarchy of online updates:

1. **Level 1 (within-stream).** Update $q^k_\lambda$ for each stream, holding $J, K_c, \lambda$ fixed.
2. **Level 2 (coupling structure).** Update $J, K_c$ as parameters of a generative model (e.g., Dirichlet-coupling for $J$, gradient on free energy of free energy for $K_c$).
3. **Level 3 (coupling precision).** Update $\lambda$ by gradient on $F[q_\lambda]$.

Each level has a clean interpretation:
- Level 1: ordinary perception/policy inference. Time scale: per-step.
- Level 2: habit/preference learning. Time scale: trials to days.
- Level 3: precision-like learning on the *coupling* itself — a model-level account of context-dependent coordination. Time scale: task phases or learning contexts.

## Coupled marginal updates

For stream $k \in \mathcal{P}$ (planning), the coordinate-descent update on $q^k_\lambda$ is the standard fixed-point:

$$q^k_\lambda(\pi^k) \;\propto\; \exp\!\Big(\!\!\!\!\!\!\!\!\!\!\underbrace{\log E_k(\pi^k) - \gamma G_k(\pi^k)}_{\text{single-stream EFE term}}\!\!\!\!\!\!\!\!\!\!\;+\!\!\!\!\!\!\underbrace{\sum_{j\neq k}\langle \log\Phi_{kj}(\pi^k,\pi^j)\rangle_{q^j}}_{\text{coupling messages from other streams}}\!\!\!\!\!\!\!\!\Big)$$

where $\Phi_{kj}(\pi^k,\pi^j) = \exp(\lambda J_{kj}(\pi^k,\pi^j) - \gamma\lambda K_{c,kj}(\pi^k,\pi^j))$. This is exactly *belief propagation on a coupled factor graph* with the coupling potentials $\Phi_{kj}$ as factors.

This recovers `pymdp`-style factorized inference [@heins-2022] as the $\lambda = 0$ limit, and generalizes it to coupled structure.

## The VFE-only suboptimality bound

For $k \in \mathcal{V}$ (VFE-only, reflexive), the stream takes a one-step gradient on its marginal free energy without iterative message passing. We compare to the coordinate-descent step taken by the full coupled inference.

**[[THMREF:thm_8_1]] (Heterogeneous coupling tax).** Let $q^k_*$ be the coordinate-descent step for stream $k$ in the coupled ensemble at coupling $\lambda$, and $q^k_\circ$ be the one-step VFE gradient step ignoring couplings. Define the coupling magnitude $\|\Phi\|_\infty = \max_{j,k,\pi^k,\pi^j}|\log \Phi_{kj}(\pi^k,\pi^j)|$. Then:

[[EQ:coupling_tax_bound]]

for a constant $C$ depending only on $|\Pi^k|$ and the curvature of $G_k$.

**Proof sketch.** Taylor-expand the coordinate-descent fixed-point
equation in $\lambda$ around the mean-field point $q^k_\circ$. The
zeroth-order term is the single-stream MF posterior; the first-order
correction is the linear coupling-message contribution; the second-order
term involves cross-coupling between messages from different streams.
KL divergence is locally a Bregman divergence with Hessian equal to the
Fisher information,
$D_{\mathrm{KL}}(p\,\|\,q) \;=\; \tfrac{1}{2}\,\|\nabla\!\log p - \nabla\!\log q\|_{F^{-1}}^{2} + O(\|\nabla\!\log p - \nabla\!\log q\|^{3})$,
so the leading correction is $O(\lambda^2)$ with prefactor controlled by
$\|\Phi\|_\infty^2$. Higher-order terms are absorbed in $O(\lambda^3)$
under the standing assumption that $J$ and $K_c$ are bounded.

**Cognitive interpretation.** Reflexive controllers can sit inside a coupled ensemble and pay only a *quadratic* cost (in coupling strength) for not running the full message-passing inference. For small-to-moderate $\lambda$, this is a negligible tax; for large $\lambda$, the reflexive controller becomes systematically suboptimal. This gives a quantitative answer to the engineering question: *how reactive can my low-level controllers be without losing the benefits of higher-level planning?* Answer: reactive is fine until $\lambda^2 \|\Phi\|_\infty^2$ becomes comparable to the per-step free-energy budget.

The $O(\lambda^2)$ envelope (see [[EQREF:coupling_tax_bound]]) is
verified empirically by the companion code in
[`src/lean/heterogeneous.py`](../src/lean/heterogeneous.py)
(`coupling_tax_within_quadratic_bound`) and gated against the analytic
prediction in
[`tests/test_heterogeneous.py`](../tests/test_heterogeneous.py); for
the symmetric K=2 Ising toy with the standard `(J, K_c, γ, modes)`
of `make_ising_ensemble` the fitted curvature is
$C \approx [[VAR:coupling_tax_curvature_C:.4f]]$ (visualized below).

[[FIG:coupling_tax_quadratic]]

The Lean companion is the current boundary statement for the quadratic
tax witness. The genuine analytic discharge is the Bregman / KL Taylor
expansion, scoped to the Mathlib4 layer:

[[LEAN:thm_8_1]]

The reflexive-stream tolerance corollary [[THMREF:cor_8_2]] then
inverts the bound to deliver a tolerance-explicit `lam_max`: from
[[EQREF:coupling_tax_bound]], setting
$C\,\lambda^2\,\|\Phi\|_\infty^{2} = \varepsilon$ gives
$\lambda_{\max}(\varepsilon) = \sqrt{\varepsilon \,/\,(C\,\|\Phi\|_\infty^{2})}$,
which is the closed form the Lean witness `SmallLambdaTolerance`
packages. Higher-order corrections from the $O(\lambda^{3})$ remainder
shrink $\lambda_{\max}$ by a multiplicative factor that approaches $1$
as $\varepsilon \downarrow 0$, so the small-tolerance asymptotic
$\lambda_{\max} \sim \sqrt{\varepsilon}$ is exact.

[[LEAN:cor_8_2]]

## Updating lambda: precision-like learning on coupling

Treat $\lambda$ as a free parameter and minimize $F[q_\lambda]$ via gradient.

The cleanest expression of the gradient uses the closed
exponential-family form
$F[q_\lambda] = \log Z_E(\lambda) - \log Z(\lambda)$
([[SECREF:decomposition.optimal]] [[THMREF:thm_4_2]]), where
$Z_E$ is the entangled-prior normalizer and $Z$ is the joint
posterior normalizer.  Differentiating with the standard
exponential-family identities
$\partial \log Z_E/\partial \lambda = \langle J\rangle_{\mathcal{E}_\lambda}$
and
$\partial \log Z/\partial \lambda = \langle J - \gamma K_c\rangle_{q_\lambda}$
gives the **total** gradient along the family $\lambda \mapsto q_\lambda$,

$$
\frac{\mathrm{d} F[q_\lambda]}{\mathrm{d} \lambda}
\;=\; \langle J\rangle_{\mathcal{E}_\lambda} \;-\; \langle J\rangle_{q_\lambda}
\;+\; \gamma\,\langle K_c\rangle_{q_\lambda}.
$$

The same answer can be unpacked in the Gibbs decomposition of
[[SECREF:decomposition]]:
$F[q_\lambda] = \sum_k F[q_\lambda^k] + \gamma\lambda\langle K_c\rangle_{q_\lambda}
              + \log Z_E(\lambda) - \lambda\langle J\rangle_{q_\lambda} + I(q_\lambda)$.
Holding $q$ frozen at its current iterate gives the *explicit* partial

$$
\left.\frac{\partial F}{\partial \lambda}\right|_{q\ \text{frozen}}
= \gamma\,\langle K_c\rangle_{q} - \langle J\rangle_{q}
  + \langle J\rangle_{\mathcal{E}_\lambda},
$$

while the implicit chain rule along $q_\lambda$ contributes the
multi-information's $\lambda$-sensitivity

$$
\frac{\mathrm{d} I(q_\lambda)}{\mathrm{d} \lambda}
= \mathrm{Cov}_{q_\lambda}\!\big(J - \gamma K_c,\; \log q_\lambda - \log \hat m(q_\lambda)\big).
$$

This Fisher-style covariance has the same algebraic form as the term
that drives standard precision learning, and the two paths agree
term-by-term: when
$q_\lambda$ minimizes $F$ at each $\lambda$ along the family, the
explicit and implicit pieces collapse to the closed-form gradient
above.

Updating $\lambda$ by a step of $-\eta \cdot \mathrm{d}F/\mathrm{d}\lambda$ is therefore
**precision-like learning on coupling** — formally analogous to
precision learning [@friston-2014; @schwartenbeck-2015; @limanowski-2024] but scoped to
cross-stream dependence rather than confidence in one stream.  The
model-level question is not "how confident am I in my policy?" but
"how strongly should my different policies be coupled right now?"
Any cognitive reading in terms of arousal, vigilance, or flexibility
is a hypothesis that would need direct joint-action measurements.

## Habit accumulation and revertibility

Habit learning under coupled $E$ is straightforward Bayesian updating on $J$ as a Dirichlet-distributed parameter [@friston-2017]:

$$E_{\lambda,\mathrm{new}}(\pi) \propto \exp\!\Big(\sum_k \log E_k(\pi^k) + \lambda J_{\mathrm{new}}(\pi)\Big), \qquad J_{\mathrm{new}}(\pi) = J(\pi) + \alpha \cdot q_\lambda(\pi) \cdot \mathrm{success\_signal}.$$

Over learning, $J$ accumulates structure shaped by which joint policy regions repeatedly minimize $G_\lambda$. This is a formal analog of AIF habit learning [@friston-2017] in which the updated prior is joint rather than single-stream: the manuscript claims a coupled-prior update rule and numerical habit-accumulation sidecar, not a direct biological implementation of habit formation.

**Revertibility.** The framework distinguishes *coupling-rich* habit from *coupling-poor* (mean-field) habit. To revert a coupling-rich habit to its mean-field component, take the m-projection: $E_k^{\mathrm{MF}}(\pi^k) = \sum_{\pi^{-k}} E(\pi)$. The coupling structure $J$ is recoverable via $J = \log E - \sum_k \log E_k^{\mathrm{MF}}$ (up to the normalizer). This yields an analytic decomposition of any habit into its marginal and coupled components, establishing revertibility as a structural property of the framework rather than a contingent feature.

## Takeaways

> **1. Reflexive controllers can ride along with planners — for a
> bounded price.**
> The coupling tax a VFE-only stream pays for joining an EFE
> ensemble is $O(\lambda^2)$, not $O(\lambda)$
> ([[THMREF:thm_8_1]]) — second-order small for small couplings.
>
> **2. The tolerance corollary makes the bound actionable.**
> [[THMREF:cor_8_2]] gives a concrete coupling-norm threshold
> below which a reflexive stream is *guaranteed* to remain within
> a chosen tolerance of optimal — answering "how reflexive can my
> low-level controllers be while still benefiting from high-level
> planning?"
>
> **3. $\lambda$ is a precision-like coupling weight, learnable from
> free energy.**
> Updating $\lambda$ by gradient on $F$ is a formal analog of
> precision learning; tonic over- and under-coupling become
> testable hypotheses about joint-statistical signatures, not
> diagnostic conclusions (cf. [[SECREF:phase]]).

---
