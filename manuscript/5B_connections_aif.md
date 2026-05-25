# Framework Connections I: pymdp/SPM Baseline, Hierarchical/Deep AIF, Sophisticated Inference, and Branching-Time AIF

This section maps the entanglement framework onto major existing
constructions in active inference, control theory, machine learning,
and theoretical neuroscience.  The framework gives exact recoveries
for some rows, parametric embeddings for others, and explicitly
labeled structural analogies where the prior framework carries
additional process-theoretic content.

The mapping is split into three thematic groups:

* **Classical active-inference frameworks** (this file) — mean-field
  AIF (`pymdp` / SPM), hierarchical / deep AIF, sophisticated
  inference, branching-time AIF.
* **Control and reinforcement-learning frameworks**
  ([[SECREF:connections_control_rl]]) — KL / path-integral control,
  options framework, products + mixtures of experts, copula VI.
* **Multi-agent, geometry, and worldview connections**
  ([[SECREF:connections_multi_agent_geometry]]) — interactive /
  multi-agent inference, renormalization-group AIF, Markov
  blankets / Bayesian mechanics, CEREBRUM and case grammar.

## Relationship calculus for AIF variants

The common template used throughout Part V is the finite joint-policy
posterior

$$
q_\lambda(\pi^{1:K}) \propto
\prod_{k=1}^K E_k(\pi^k)
\,
\exp\!\left(
  -\sum_{k=1}^K \gamma_k G_k(\pi^k)
  + \lambda J(\pi^{1:K})
  - \gamma\lambda K_c(\pi^{1:K})
\right).
$$

Every comparison below asks which part of this template a prior
framework changes: the generative model, the policy-posterior
factorization, the EFE recursion, the message-passing schedule, the
agent-coupling graph, or temporal depth.  The recovery labels are
therefore strict.  `Exact` means literal specialization of this
posterior or its single-stream log-partition dual after all variables
and factors have been specified.  `Parametric` means the cited
framework can realize the form after the modeler adds explicit policy
nodes, coupling factors, priors, or change-of-variables.  `Analogical`
means the cited framework shares a structural motif, but additional
process-theoretic content remains in the generative model, recursive
EFE definition, or message-passing schedule rather than in
$\lambda J$ itself.  Exactness therefore attaches to a fully specified
posterior or graphical model, not to active inference as a whole.

The notation bridge to standard active inference is deliberately
literal.  The generative-model law $P(\cdot)$ remains represented by
the usual likelihood, transition, preference, state-prior, and
policy-prior ingredients; the variational beliefs $Q(\cdot)$ become
the normalized policy posteriors denoted by $q$ in this manuscript.
The per-stream factors $E_k$, $G_k$, and $\gamma_k$ are the ordinary
habit/prior, expected-free-energy, and policy-precision ingredients of
single-stream discrete active inference.  The new objects are only
$J$, $K_c$, and $\lambda$: a pair of joint-policy potentials and the
scalar that weights them.  Thus $\lambda$ is not a substitute for
policy precision, neural precision, preferences, desire, or a
generative-model parameter.  It is a coupling strength inside the
finite policy-posterior family, and every comparison below must say
whether the external framework supplies the same posterior, supplies a
parameterized route to it, or merely shares a structural pattern.

This convention matters because active inference is broader than any
one posterior factorization.  Factor-graph treatments show how
generative-model specification and message passing can automate deep
temporal active inference [@devries-friston-2017-factor-graph], while
graphical-brain and neuronal-message-passing accounts distinguish
Forney-style belief propagation, mean-field, Bethe, and marginal
approximations as alternative implementation commitments
[@friston-parr-devries-2017-graphical-brain; @parr-markovic-kiebel-friston-2019-message-passing; @yedidia-2005].
Reactive message-passing toolkits such as RxInfer support flexible
factor insertion [@bagaev-2023].  Adding
$\exp(\lambda J-\gamma\lambda K_c)$ as a policy factor is then an
exact implementation pattern for that chosen graphical model; it is
not a claim that every factor-graph or RxInfer active-inference model
already contains this coupling factor.

## Relation to recent unification efforts

Recent work has independently proposed unification narratives for
active inference. Da Costa, Tenka, Zhao, and Sajid treat active
inference as a normative model of agency and a comparison language for
different agency models [@dacosta-2024-agency]. de Vries, Nuijten,
van de Laar et al.
[@devries-2025] recast EFE-based planning as variational inference on
an augmented generative model with preference and epistemic priors;
Nuijten and Lukashchuk [@nuijten-lukashchuk-2025] formally argue that
active inference is a subtype of variational inference; Champion,
Bowman, Marković, and Grześ [@champion-2024-reframing] derive four
EFE formulations from unified root definitions. Millidge, Tschantz,
and Buckley [@millidge-2021] provide the complementary caution:
expected free energy has multiple derivational routes whose
assumptions matter. These constructions unify over the *form of EFE*
or over the *EFE/VFE equivalence*; the present framework unifies over
the *factorization structure of the joint policy posterior* via a
scalar deformation parameter $\lambda$. The two unifying strategies
are orthogonal — our framework operates on top of a generative model
that the de Vries / Nuijten lineage works to construct, and Champion
et al.'s EFE-reframing applies to the per-stream $G_k$ that enters our
$\lambda$-deformed prior.
This distinction keeps the claim strength clear: the present
manuscript does not solve the EFE unification problem, but it is
compatible with those formulations because it acts on the posterior
factorization once the per-stream EFE terms have been specified.

## Mean-field active inference (`pymdp`, SPM, ActiveInference.jl)

The standard factorized treatment of multi-modality, multi-factor
active inference [@heins-2022; @smith-2022] is the $\lambda = 0$ slice
of our framework. Our addition: extend the variational family along the
e-geodesic in any chosen direction (see [[EQREF:e_geodesic]]).
Concretely, in `pymdp` notation, the multi-stream policy posterior
$q(\pi) = \prod_f q_f(\pi_f)$ becomes $q_\lambda(\pi)$ with $\lambda$
as an additional learnable hyperparameter.

This is operationalized by the project's [[VAR:pymdp_distribution_version]] simulation
harness ([[SECREF:pymdp_harness]],
[`src/simulation/`](../src/simulation/),
[`docs/simulation/pomdp_simulation.md`](../docs/simulation/pomdp_simulation.md)):
each stream is built as a separate `pymdp.agent.Agent` whose
$q_\pi^k = \mathrm{softmax}(-\gamma G_k)$ plays the role of a
mean-field marginal, and the analytical layer of [[SECREF:lambda_deformation.entangled_posterior]] adds the
λ-coupling on top.  This is an adapter construction, not a claim about
the native pymdp API: pymdp supplies per-stream inference, while this
repository constructs and validates the structured joint posterior
after those per-stream posteriors exist.  At $\lambda = 0$, the joint is *exactly* the outer
product of the per-stream pymdp posteriors; for $\lambda > 0$ the
total correlation grows smoothly toward the task-specific coordination
ceiling.  In the binary all-aligned/all-anti-aligned Ising slice used
by the pymdp harness, that ceiling is $(K-1)\log 2$; for the default
$K = [[VAR:pymdp_ensemble_K]]$ case this reduces to $\log 2$.

[[FIG:pymdp_total_correlation_curve]]

[[FIG:pymdp_coupled_rollout]]

## Hierarchical / Deep Active Inference

Hierarchical AIF [@friston-2017; @pezzulo-2018] decomposes the agent
into a hierarchy of slow (high-level) and fast (low-level) generative
models with explicit message passing.

**[[THMREF:thm_11_1]] Structural analog of hierarchical AIF
(witness-form).** With block-bidiagonal $J$ coupling adjacent levels
of an $L$-level ensemble and $\lambda \to \infty$, the entangled
posterior concentrates on the cross-level coordination shadow of
hierarchical AIF: each adjacent pair $(\pi^\ell, \pi^{\ell+1})$
becomes deterministically linked.  The Lean companion
`ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness` is now
live in the boundary fragment in *witness-consuming* form: the caller
supplies the entangled family $\lambda \mapsto q_\lambda$, the
hierarchical fixed point $q_\infty$, and the universally quantified
$(\varepsilon, \lambda_0)$ concentration inequality as a
`HierarchicalConcentrationWitness` structure; the boundary fragment
certifies the resulting existence claim by extracting the witness
fields.  We do not claim that this recovers hierarchical AIF in full
— the *temporal scale separation* and *directed top-down/bottom-up
message passing* that characterize standard hierarchical AIF
[@friston-2017; @pezzulo-2018] are additional structures not encoded
by symmetric $J$ alone. The construction here recovers the
*coupling-structural* component machine-checked at the witness level.
A generative-model-side embedding (with explicit per-level $B^\ell$
dynamics) would be required to upgrade the analogy to a recovery, and
that stronger construction is outside the present artifact.

## Sophisticated Inference (recursive EFE)

Sophisticated inference [@friston-2021] introduces beliefs about
beliefs — the agent reasons about counterfactual consequences of its
actions for its own beliefs. Recursive EFE has the form

$$G_{\mathrm{soph}}(\pi) = \mathbb{E}_{q(o\mid\pi)}\!\left[G(\pi') + \log q(\pi'\mid o)\right].$$

This can be represented within our template by treating one stream
$\pi$ as the current policy and another stream $\pi'$ as the next-step
policy posterior conditional on observations, with a specific
source-supplied choice of $J$ that encodes the recursive
belief-about-beliefs structure.

**[[THMREF:prop_11_2]] Sophisticated inference as a tree-structured
coupling (witness-form).** With $K = d+1$ streams indexed by lookahead
depth and a $J$ that scores joint trajectories by their sophisticated
EFE, the entangled posterior $q_\lambda$ tracks coordinated lookahead
policies.  The Lean companion
`ConnectionsWitnesses.sophisticatedInference_embedding_witness` is now
live in the boundary fragment as a *witness-consuming* form: the
caller supplies an opaque sophisticated-inference source type, an
embedding map into the entangled-posterior family, and the
VFE-preservation identity as a `SophisticatedInferenceEmbedding`
structure; the boundary fragment certifies that the embedding lifts
into the boundary-fragment `variationalFreeEnergy` primitive without
`sorry`.  We emphasize that the substantive content of sophisticated
inference [@friston-2021] — recursive conditioning of next-step EFE on
*anticipated* observations $o_\tau$ — requires an explicit form for
$J$ that integrates over $q(o_\tau, s_\tau \mid \pi_\tau)$. Spelling
out this $J$ is straightforward but voluminous; we treat it here as a
*structural analogy* with the recursive content discharged into the
construction of $J$. The connection is machine-checked at the level
of VFE-preservation through a witness-form Lean embedding; the
observation-conditioning recursion is a constraint on $J$, not a
consequence of the $\lambda$-deformation.

## Branching-Time Active Inference

Branching-time AIF [@champion-2022] addresses the exponential
complexity of policy enumeration via Bayesian filtering over a
branching policy tree (with optional MCTS-style sampling for
tractability, in the lineage of [@fountas-2020]).

The scoped connection is representational: branching-time AIF performs
Bayesian filtering / sampling on the policy tree, while our framework
parameterizes compact probability tensors that can be read as compressed
views of temporally-extended policy posteriors. Concretely, a
tensor-train decomposition of $q_\lambda$ over a temporally-extended
policy offers a compact policy-tree summary with bond dimension
controlling representational capacity. This is an analogy and an
engineering route for compression, not an algorithmic equivalence to
Champion's Bayesian-filtering formulation. It is complementary to the
Monte-Carlo lineage [@fountas-2020] and to tensor-network techniques
[@orus-2014; @han-2018; @oseledets-2011].

## Synthesis: How Every Connection Lands on Lambda, J, or Kc

The thirteen frameworks discussed across this section and its two
companions ([[SECREF:connections_control_rl]],
[[SECREF:connections_multi_agent_geometry]]) all reduce to a specific
choice of three core objects: the coupling strength $\lambda$, the
coupling potential $J$, and the off-diagonal cost $K_c$.  The table
below summarizes the embedding for each, so a reader can locate any
one connection at a glance.

Two patterns are worth flagging before reading the table.  First, the
$\lambda$ axis orders the frameworks by *coupling strength*: mean-field
AIF lives at the $\lambda = 0$ pole; classical hierarchical AIF and
option-like policy-matching embeddings live near $\lambda \to \infty$
with sparse $J$; the entire continuum between them is what the
parametric framework covers.  Second, the $J$ structure orders the
frameworks by *kind of
coordination*: block-bidiagonal $J$ produces hierarchical structure,
tensor-train $J$ produces renormalization-group-style bond-dimension
flow, symmetric Ising-style $J$ produces interactive multi-agent
behavior, case-graded $J$ produces CEREBRUM-style asymmetric coupling.
The *Recovery type* column distinguishes *exact* (literal
specialization of the posterior or its single-stream log-partition
dual), *parametric* (realized after an explicit parameter,
change-of-variables, or factor-graph modeling choice), and
*analogical* (the prior framework's coupling-structural skeleton is
mirrored, but additional dynamical, temporal, or message-passing
content lies outside the $\lambda$-deformation and must be discharged
into $J$, the EFE recursion, or the generative model).

| Framework | $J$ structure | $\lambda$ regime | Recovery type |
|---|---|---|---|
| Mean-field AIF (`pymdp`, SPM) | any | $\lambda = 0$ | exact |
| Factor-graph / RxInfer-style message passing | additional policy factor $\exp(\lambda J-\gamma\lambda K_c)$ | any finite $\lambda$ once the factor is added | parametric |
| Product of Experts | $J = \sum_j \log f_j$, $K_c = 0$ | any $\lambda$ | exact |
| Copula VI | $J$ = log-copula density on $\Pi$ (CDF reparametrization) | any $\lambda$ | parametric (after CDF change-of-variables) |
| Hierarchical / Deep AIF | block-bidiagonal $J$, $K_c = 0$ | $\lambda \to \infty$ on off-diagonal blocks | analogical (structural shadow; lacks temporal-scale separation and directed message passing) |
| Sophisticated inference | $J$ that integrates over $q(o_\tau, s_\tau \mid \pi_\tau)$ | $K = d{+}1$ streams, finite $\lambda$ | analogical (with $J$-construction discharge of recursive observation-conditioning) |
| Branching-time AIF | tensor-train $J$ across time-extended policies | bond-dimension truncation | analogical (with tensor-train algorithmic side) |
| KL / path-integral control (single-stream) | single-stream cost $C(\tau)$ | $K = 1$, $\lambda = 1$ | exact (classical log-partition–value duality) |
| Options framework / Hierarchical RL | $J(\pi^1,\pi^2)$ peaked on option-matching configs | $K = 2$, any $\lambda$ | parametric (soft option boundaries; policy-matching only) |
| RG-AIF (RGM) | tensor-train compression of $q_\lambda$ | bond-dimension flow | analogical (MERA-style scale invariance lies outside the present construction) |
| Mixture of Experts | $m$-mixture (not $e$-product) | n/a | out-of-scope ($m$-geometry dual) |
| Interactive / multi-agent AIF | $NK$-stream $J$ with within- and across-agent blocks | any $\lambda$ | parametric (per-stream coupling extends to per-agent) |
| Markov blankets / Bayesian mechanics (policy-space) | $J$ controls cross-stream coupling | $\lambda = 0$ → $\eta = 0$ | analogical policy-space leakage measure (distinct from state-space blankets) |
| CEREBRUM / case-grammar | directional asymmetry in $J$ | any $\lambda$ | parametric (case = edge-weight asymmetry) |

Three takeaways from the table:

1. **The exact recoveries are mean-field AIF, product-of-experts, and
   single-stream KL control.** Factor-graph / RxInfer-style
   implementations are parametric until the modeler inserts and
   validates the policy-coupling factor in a chosen graph; Copula VI is
   recovered parametrically after a CDF change-of-variables. The remaining rows are *structural
   analogies*: the coupling skeleton of the prior framework is
   mirrored, but additional content (temporal-scale separation in
   hierarchical AIF; recursive observation-conditioning in
   sophisticated inference; Bayesian filtering over the expanded
   policy tree in branching-time AIF; MERA-style scale invariance in
   RG-AIF; state-space construction in Markov blankets) lies outside
   the $\lambda$-deformation.
2. **The $\lambda$ axis is the natural "comparison axis."** Mean-field
   AIF lives at the $\lambda = 0$ pole; sparse-$J$ frameworks live
   near $\lambda \to \infty$; the continuum between them is what our
   framework parametrizes.
3. **The $J$ structure is the natural "kind axis."** Block-bidiagonal $J$
   is hierarchical coupling; tensor-train $J$ is RG-style compression;
   symmetric Ising-style $J$ is interactive multi-agent; case-graded
   $J$ is CEREBRUM. Every row above is a statement about which $J$
   topology the prior art is implicitly assuming.

In this sense the lattice of existing constructions is mapped onto
a low-dimensional set of slices through the $(\lambda, J, K_c)$
parameter space, with the connecting tissue between them
parameterized rather than ad-hoc — though several of these mappings
remain structural analogies rather than full recoveries, in the
senses listed above.

---
