# Framework Connections II: KL/Path-Integral Control, Options Frameworks, Products-of-Experts, and Copula Variational Inference

This sub-section continues [[SECREF:connections]] by mapping the
entanglement framework onto stochastic optimal control, hierarchical
reinforcement learning, and probabilistic-modeling connections that
sit between the active-inference and ML communities. The canonical
tutorial on the control-as-inference / maximum-entropy RL viewpoint
[@levine-2018] is the natural ML-side companion for the active-inference
recoveries developed below.

## KL / Path-Integral Stochastic Optimal Control

Path-integral and KL control [@kappen-2005; @todorov-2006;
@theodorou-todorov-2012; @rawlik-toussaint-vijayakumar-2013]
solve stochastic optimal control via free-energy duality:

$$V(x) = -\frac{1}{\rho}\log \mathbb{E}_{p_{\mathrm{free}}}[\exp(-\rho C(\tau))]$$

where $C(\tau)$ is the trajectory cost (renamed from the standard $J$
to avoid clashing with our habit potential $J$) and $p_{\mathrm{free}}$
is the uncontrolled-dynamics prior. The control-effort cost is the KL
between the controlled and uncontrolled measures.

**Connection.** At $K = 1$, $\lambda = 1$ the framework reduces to
the classical single-stream log-partition–value-function duality
[@kappen-2005; @todorov-2006; @theodorou-todorov-2012;
@rawlik-toussaint-vijayakumar-2013]:
$V(x) = -(1/\rho)\log\mathbb{E}_p[\exp(-\rho C(\tau))]$, where
$\mathcal{E}_1 = E_1 \cdot \exp(J - \gamma K_c)$ plays the role of
the Gibbs-controlled trajectory measure. This is the well-known
special case; the genuinely novel content of the framework is at
$K \geq 2$, where our $E_k(\pi^k)$ plays the role of the per-stream
uncontrolled prior and the coupling potential $\lambda J$ encodes
*cross-stream control coupling* — the sense in which a "joint" KL
controller pays a coupling cost beyond the marginal control efforts.
A multi-stream value-function formulation follows in principle from
the same log-partition duality; we sketch but do not develop it here.

**Smooth-deformation precedents.** Smooth scalar deformations of
variational families have prior history in the structured-VI
literature. Li and Turner [@li-turner-2016] introduce $\alpha$-Rényi
divergence variational inference: $\alpha = 1$ recovers the standard
ELBO, $\alpha \to 0$ recovers the log marginal likelihood. Tran, Blei,
and Airoldi [@tran-2015] augment mean-field with copula dependency;
the recent Fu–Smith–Panagiotelis vector-copula extension
[@fu-smith-panagiotelis-2025] adds learnable dependency between
blocks. Our $\lambda$ differs from these by parametrizing the
*policy-posterior factorization structure*, not the *divergence* (as in
$\alpha$-Rényi-VI) or the *dependency form alone* (as in copula VI):
at $\lambda = 0$ we have strict mean-field, and at $\lambda > 0$ we
have a coupling-deformed factorization whose structure is controlled
by the habit and preference potentials $(J, K_c)$.

## Options framework / Hierarchical RL

The options framework and hierarchical-RL literature [@sutton-1999;
@barto-mahadevan-2003; @bacon-harb-precup-2017] introduce
temporally-extended actions ("options") as semi-MDPs with initiation
sets, intra-option policies, and termination conditions. The
planning-as-inference
program [@toussaint-2009; @botvinick-toussaint-2012] casts policy
search as Bayesian posterior inference over trajectories, giving the
options decomposition a probabilistic-graphical-model reading.

**Connection.** An option can be represented as a
*temporally-coupled policy stream*: a high-level decision (which option
to invoke) and a low-level intra-option policy. This is a parametric
$K = 2$ embedding with $J$ encoding the option-membership structure
(high $J$ on configurations where intra-option policy matches the
invoked option, low $J$ otherwise). Termination conditions correspond
to boundary conditions on the entangled posterior only after the
modeler encodes them in that factorization.

The framework therefore gives an option-like parametric embedding with
*probabilistic, soft, learnable option-boundary weights* via
$\lambda$-tunable coupling. It does not replace option discovery or
termination learning; those algorithmic choices must be supplied by the
modeler or by a separate option-learning layer.

## Product of Experts and Mixture of Experts

Product of Experts (PoE) [@hinton-2002] combines models multiplicatively:

$$P(x) \propto \prod_j f_j(x).$$

Our $\mathcal{E}_\lambda(\pi) = \prod_k E_k(\pi^k) \cdot \exp(\lambda J(\pi))$
is a PoE on the joint policy space, with the coupling potential acting
as one additional expert. The framework therefore inherits PoE's
compositionality: combining experts that each capture a piece of the
policy-coupling structure.

Mixture of Experts (MoE), conversely, is *additive* combination —
corresponding to a different geometric structure ($m$-mixtures rather
than $e$-products). The two are dual.

## Copula variational inference

Copula VI [@tran-2015; @nelsen-2006] retains mean-field marginals
while modeling dependence via a copula. Our framework's
$\lambda$-deformation realizes the same copula-density form when the
modeler supplies the CDF reparameterization and chooses $J$ as the
log-density of the desired copula family.
Define per-stream marginal CDFs $u^k = F_{E_k}(\pi^k) \in [0,1]$.
Under this reparametrization, the entangled prior
$\mathcal{E}_\lambda(\pi) = \prod_k E_k(\pi^k)\,\exp(\lambda J(\pi)) /
Z_E$ maps to a copula density

$$c(u^1, \ldots, u^K) = \exp\!\bigl(\lambda J(\pi(u^1, \ldots, u^K))\bigr)$$

on the unit hypercube (up to the normalizer $Z_E$). The framework
therefore recovers the parametric copula-density slice of copula
variational inference [@tran-2015; @fu-smith-panagiotelis-2025] with copula-log-density
$\lambda J$; bond-dimension truncation of $J$ as a tensor-train
is analogous to vine-copula truncation at depth $\chi$ rather than a
proof that every vine construction is a tensor-train posterior. This
connects active inference to the rich copula literature, importing
techniques for sparse coupling estimation [@nelsen-2006; @han-2016;
@tran-2015; @fu-smith-panagiotelis-2025].

## Recovery dictionary

The four connections above are concrete only when the relationship
class is explicit.  Reading the table left-to-right turns a broad
recovery claim into a recipe with the relevant exact, parametric, or
out-of-scope boundary attached.

| Prior framework | Structural choice in $(K, J, K_c, \lambda)$ | Relationship class / behavior |
|---|---|---|
| Mean-field active inference (pymdp / SPM) | $\lambda = 0$, any $J, K_c$ | $q_\lambda = \prod_k E_k\,e^{-\gamma G_k} / Z_k$; per-stream FPI |
| KL / path-integral control (single-stream) | $K = 1$, $\lambda = 1$ | $V(x) = -(1/\rho)\log\mathbb{E}_{E}[\exp(-\rho C(\tau))]$; classical log-partition–value duality [@kappen-2005; @todorov-2006; @theodorou-todorov-2012; @rawlik-toussaint-vijayakumar-2013] |
| Options / hierarchical RL | $K = 2$, $J(\pi^1,\pi^2)$ peaked on $\pi^2$ that matches option $\pi^1$ | option-like soft boundaries; intra-option policy from $q_\lambda^2$ (parametric — policy-matching only; option discovery/termination learning supplied separately) [@sutton-1999; @barto-mahadevan-2003; @bacon-harb-precup-2017] |
| Product of Experts | $K_c = 0$, $J = \sum_j \log f_j$ | $\mathcal{E}_\lambda \propto \prod_k E_k \cdot \prod_j f_j^\lambda$ |
| Mixture of Experts (dual) | $m$-mixture rather than $e$-product; not in this construction | additive combination — out-of-scope for the entangled-prior family |
| Copula VI | $E_k$ = marginals; $J$ = log-copula density on $u = F_E(\pi)$ | $\mathcal{E}_\lambda$ as a $\lambda$-deformed copula-density slice after CDF change-of-variables [@nelsen-2006; @tran-2015; @fu-smith-panagiotelis-2025] |
| $\alpha$-Rényi-VI [@li-turner-2016] | divergence-parametrized, not factorization-parametrized | orthogonal axis — not recovered, complementary smooth-deformation precedent |

Empty cells mean *not subsumed in the entangled-prior construction*
(e.g. Mixture-of-Experts requires the $m$-geometry dual).  Every
non-empty row is a worked instance: assigning $(K, J, K_c, \lambda)$
the values shown either reproduces the prior framework's posterior
directly or realizes the relevant parametric policy-matching slice.

---
