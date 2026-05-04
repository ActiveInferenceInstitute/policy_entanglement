# Connections to Existing Frameworks

This section maps the entanglement framework onto major existing
constructions in active inference, control theory, machine learning,
and theoretical neuroscience. The framework either subsumes,
generalizes, or sharply localizes each.

## Mean-field active inference (`pymdp`, SPM, ActiveInference.jl)

The standard factorized treatment of multi-modality, multi-factor
active inference [@heins-2022; @smith-2022] is the $\lambda = 0$ slice
of our framework. Our addition: extend the variational family along the
e-geodesic in any chosen direction (see [[EQREF:e_geodesic]]).
Concretely, in `pymdp` notation, the multi-stream policy posterior
$q(\pi) = \prod_f q_f(\pi_f)$ becomes $q_\lambda(\pi)$ with $\lambda$
as an additional learnable hyperparameter.

This is operationalised by the project's pymdp 1.0.1 simulation
harness ([`src/simulation/`](../src/simulation/),
[`docs/simulation/pomdp_simulation.md`](../docs/simulation/pomdp_simulation.md)):
each stream is built as a separate `pymdp.agent.Agent` whose
$q_\pi^k = \mathrm{softmax}(-\gamma G_k)$ plays the role of a
mean-field marginal, and the analytical layer of [[SECREF:lambda_deformation.entangled_posterior]] adds the
λ-coupling on top.  At $\lambda = 0$, the joint is *exactly* the outer
product of the per-stream pymdp posteriors; for $\lambda > 0$ the
total correlation grows smoothly toward $\log K$.

[[FIG:pymdp_total_correlation_curve]]

[[FIG:pymdp_coupled_rollout]]

## Hierarchical / Deep Active Inference

Hierarchical AIF [@friston-2017; @pezzulo-2018] decomposes the agent
into a hierarchy of slow (high-level) and fast (low-level) generative
models with explicit message passing.

**[[THMREF:thm_11_1]].** Hierarchical AIF with hierarchical depth $L$ is the
limit of policy entanglement with **block-bidiagonal** $J$ (level
$\ell$ couples only to level $\ell+1$), $K_c = 0$, and
$\lambda \to \infty$ on the off-diagonal blocks.

**Proof sketch.** Block-bidiagonal $J$ with $\lambda \to \infty$
enforces hard determinism between adjacent levels, recovering the
explicit-message-passing structure. Finite $\lambda$ relaxes this to
soft probabilistic coupling — which is, in fact, more biologically
plausible. Hierarchical AIF is the *infinite-precision* limit of
policy entanglement with hierarchical sparsity. ∎

This shows the framework strictly generalizes hierarchical AIF, with
the additional benefit of *tunable* hierarchy strength.

## Sophisticated Inference (recursive EFE)

Sophisticated inference [@friston-2021] introduces beliefs about
beliefs — the agent reasons about counterfactual consequences of its
actions for its own beliefs. Recursive EFE has the form

$$G_{\mathrm{soph}}(\pi) = \mathbb{E}_{q(o\mid\pi)}\!\left[G(\pi') + \log q(\pi'\mid o)\right].$$

This is structurally the same as our framework with one stream $\pi$
(the current policy) coupled to another stream $\pi'$ (the next-step
policy posterior conditional on observations), and a specific choice
of $J$ that encodes the recursive belief-about-beliefs structure.

**[[THMREF:prop_11_2]].** Sophisticated inference with recursion depth $d$
embeds in policy entanglement with $K = d+1$ streams (current and $d$
counterfactual future policies), specific $J$ encoding the
recursive-belief structure, and $K_c$ set by EFE-of-EFE.

This gives sophisticated inference a clean generalization to
multi-modal, multi-timescale settings, where the recursive structure
can hold *across modalities* not just in time.

## Branching-Time Active Inference

Branching-time AIF [@champion-2022] addresses the exponential
complexity of policy enumeration via Monte Carlo tree search over a
branching policy tree.

The connection: branching-time AIF samples the policy tree, while our
framework parameterizes its compressed representation. Concretely, a
tensor-train decomposition of $q_\lambda$ over a temporally-extended
policy is equivalent to a *compact representation of the policy tree*
with bond dimension controlling representational capacity. This gives
a principled compression of MCTS trees via tensor-network techniques
[@han-2018].

## KL / Path-Integral Stochastic Optimal Control

Path-integral and KL control [@theodorou-todorov-2012; @kappen-2005]
solve stochastic optimal control via free-energy duality:

$$V(x) = -\frac{1}{\rho}\log \mathbb{E}_{p_{\mathrm{free}}}[\exp(-\rho J(\tau))]$$

where $J(\tau)$ is the trajectory cost and $p_{\mathrm{free}}$ is the
uncontrolled-dynamics prior. The control-effort cost is the KL between
the controlled and uncontrolled measures.

**Connection.** Our $E_k(\pi^k)$ plays the role of the uncontrolled
prior; $-\gamma G_k$ is the trajectory cost (in negative-utility
convention). The coupling potential $\lambda J$ encodes *cross-stream
control coupling* — exactly the sense in which a "joint" KL controller
pays a coupling cost beyond the marginal control efforts. The
framework therefore extends KL control duality to coupled multi-stream
settings, with $\lambda$ as the cross-coupling precision.

## Options framework / Hierarchical RL

The options framework [@sutton-1999] introduces temporally-extended
actions ("options") as semi-MDPs with initiation sets, intra-option
policies, and termination conditions.

**Connection.** An option is a *temporally-coupled policy stream*: a
high-level decision (which option to invoke) and a low-level
intra-option policy. This is exactly $K = 2$ entanglement with $J$
encoding the option-membership structure (high $J$ on configurations
where intra-option policy matches the invoked option, low $J$
otherwise). Termination conditions correspond to *boundary conditions*
on the entangled posterior.

The framework therefore generalizes options to *probabilistic, soft,
learnable option boundaries* via $\lambda$-tunable coupling.

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

Copula VI [@tran-2015] retains mean-field marginals while modeling
dependence via a copula. Our framework's $\lambda$-deformation is
structurally equivalent: $\mathcal{E}_\lambda$ retains mean-field
marginals (modulo normalization) while $J$ encodes joint dependence.
The Schmidt-rank / tensor-train view on $J$ corresponds to vine-copula
and tree-copula decompositions. The framework therefore connects
active inference to the rich copula literature, importing techniques
for sparse coupling estimation [@han-2016; @tran-2015].

## Interactive Inference / Multi-Agent Active Inference

Interactive inference [@maisto-2023] models multi-agent cooperation as
joint inference under shared generative models.

**Connection.** A multi-agent setting with $N$ agents each with $K$
policy streams maps onto a single $NK$-stream entanglement, with $J$
encoding both within-agent and across-agent coupling. The framework
therefore unifies single-agent multi-stream coordination with
multi-agent joint action under a single coupling parameter.

This is conceptually clean: from the perspective of policy
entanglement, *interpersonal* coordination differs from *intrapersonal*
coordination only in which streams are coupled, not in the
mathematical machinery.

## Renormalization-Group Active Inference

Friston et al.'s scale-free / RG treatment of active inference
[@friston-2024] derives hierarchical generative models via repeated
application of an RG operator that coarse-grains state spaces while
preserving dynamics-form.

**Connection.** Policy entanglement's tensor-train / sparse-coupling
limit *is* an RG-flow on the space of generative models. The bond
dimensions of the tensor-train representation play the role of
"effective degrees of freedom at scale $k$"; coarse-graining =
increasing $k$ = decreasing bond dimensions. The framework therefore
embeds RG-AIF: the renormalization flow is the flow on the coupling
structure $J$ as $\lambda$ varies and as we project onto sparser
representations.

## Markov Blankets and Bayesian Mechanics

The Markov blanket formulation of FEP [@friston-2019] identifies a
system with a partition of states into internal/external/blanket. In
our framework, *streams* are themselves potential Markov-blanket
partitions of the agent's policy space.

**[[THMREF:prop_11_3]].** A mean-field policy decomposition ($\lambda = 0$)
corresponds to a perfect Markov-blanket partition of the policy space
across streams. Non-zero $\lambda$ corresponds to *blanket leakage* —
streams with non-trivial conditional dependencies. The framework thus
quantifies the degree of Markov-blanket separation between streams as
$1 - I(q_\lambda)/H(q_\lambda)$, the *normalized* multi-information.

## CEREBRUM and case-grammar approaches

DAF's CEREBRUM (Case-Enabled Reasoning Engine with Bayesian
Representations for Unified Modeling) explores grammatical case as a
structuring principle for cognitive architectures. The connection to
policy entanglement: cases encode *role-relations* across cognitive
operations, which are precisely cross-stream coupling structures. A
nominative-accusative case relation between two streams corresponds to
a directional asymmetry in $J$. The framework therefore provides a
probabilistic backend for case-grammar cognitive architectures.

The interaction graph of $J$ across multiple streams is itself a
useful diagnostic — symmetric all-to-all coupling (as in the K=4 Ising
ensemble below) appears as an evenly-weighted clique, while
asymmetric / hierarchical / case-graded couplings would manifest as
edge-weight heterogeneity:

[[FIG:coupling_graph]]

---
