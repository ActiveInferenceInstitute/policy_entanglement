# Motivation and Position: Why Multi-Stream Active Inference Needs Parametric Policy Entanglement

## The problem in plain language

Active inference furnishes a normative theory of a perceiving-and-acting unit by minimizing variational free energy across perception, action, and learning [@friston-2006; @friston-2010; @buckley-2017; @friston-2017; @dacosta-2020; @parr-2022].  In the discrete-time POMDP formulation, a unit is specified by an observation likelihood $A: p(o\mid s)$, a transition tensor $B: p(s'\mid s,a)$, prior preferences over outcomes $C$, a prior over hidden states $D$, and a habit / prior over policies $E(\pi)$, where policies $\pi$ live on a space of action-affordances replicated across a (possibly flexible) time horizon [@smith-2022; @heins-2022].  Expected free energy then gives each policy posterior both an epistemic term (seek observations that resolve uncertainty) and a pragmatic term (seek preferred outcomes), so action selection is not bolted onto perception but derived from the same variational calculus [@friston-2017; @sajid-2021; @parr-friston-2019; @friston-2018-cognitive-consistency].  The formalism is mathematically compact, biologically motivated, and increasingly used across perception, decision-making, robotics, and computational psychiatry [@adams-2013; @schwartenbeck-friston-2016; @lanillos-2021], while its direct empirical status remains an active comparative-modeling question [@hodson-2024].

An agent of any non-trivial complexity, however, is not best described by *a single* policy variable.  A real agent juggles **many concurrent policies**: motor and attentional, fast and slow, modality-specific, with some streams treating the next move as a one-shot gradient descent on variational free energy (VFE) and others engaging in deep counterfactual planning under expected free energy (EFE).  The standard discrete POMDP treatment in `pymdp` [@heins-2022] and the continuous-state SPM-DEM lineage [@friston-trujillo-daunizeau-2008] split inference across independent *factors* and policies — that is, they rely on strict mean-field factorizations across hidden-state factors, observation modalities, and, in the multi-stream construction studied here, policy variables [@dacosta-2020; @smith-2022].

The mean-field separation is computationally cheap and biologically suggestive — it mirrors functional segregation, sparse cortical connectivity, and the modular character of much of the cortex — but it discards a structure that is visible in natural behavior and engineered agents: actions taken on one stream are routinely contingent on, anticipatory of, and instrumentally coupled to actions on others.  A drummer's left hand does not freely sample its policy distribution while the right hand plans the next fill; an autonomous vehicle's lateral and longitudinal controllers share predictive structure with the symbolic route planner [@lanillos-2021]; a human reaching for a cup while reading does not factor reach-policy and saccade-policy independently.  Natural-task eye-tracking studies find that gaze typically arrives at the next task object before manipulation begins [@land-hayhoe-2001], and object-manipulation studies show hand shaping and grip forces coupled to visual sampling of the object [@johansson-2001].  Contemporary world-model RL agents such as DreamerV3 [@hafner-2023] give an adjacent machine-learning example: cross-modal predictive state is useful, but the architecture does not expose a scalar coupling parameter that the modeler can tune, infer, or validate.

This document develops a tunable, analytically tractable, machine-checkable formalism for the *parametric entanglement* of concurrent policies in a single agent.  The key move is structural rather than architectural: we do not commit to translation layers between symbolic planners and motor controllers (which would make the modeler responsible for the entire bridge), nor to fully joint enumeration of cross-modal policies (which combinatorially explodes), nor to hand-designed attention-gating that re-introduces the mean-field assumption at a higher level.  We instead introduce a *single tunable coupling parameter* that interpolates between strict factorization and arbitrary joint structure, with a closed-form decomposition of free energy that exposes precisely what the entanglement buys.  In FEP language, $\lambda$ does not replace precision, preferences, or expected-free-energy minimization; it makes the strength of cross-stream policy dependence an explicit object that can be proved about, simulated, visualized, and validated.

The phrase *policy-posterior coupling* is used narrowly.  Standard
active-inference notation already distinguishes posteriors over hidden
states, policies, and parameters [@friston-2017; @smith-2022].  This
manuscript changes only the variational family for the policy
posterior: the policy prior factors $E_k$, the expected-free-energy
weights $\gamma_k G_k$, and the agent's generative-model tensors remain
visible, while $\lambda J$ adds an explicit cross-stream factor on
joint policy space.  Thus $\lambda$ is not neural precision, not a new
preference distribution, and not a biological measurement by itself; it
is the scalar strength of a specified coupling potential inside the
finite policy posterior.

## Current coping strategies and their limits

The active-inference and probabilistic-modeling literatures have developed several strategies for handling cross-stream dependence on top of a mean-field backbone.  Each is genuinely useful in its regime; each leaves a structural gap that the parametric construction below is designed to close.

* **Architectural translation layers.**  A common engineering pattern is to factor the agent into independent per-stream modules and hand-design a translation layer between them — for example, a symbolic-planner outputs a goal that a motor-controller consumes as a target.  This decouples the modules at design time but moves the entire alignment problem into the translation layer, which is typically non-differentiable, non-Bayesian, and the implicit source of brittleness when the modules' assumptions drift apart.
* **Hierarchical / deep active inference.**  Hierarchical AIF [@friston-2017; @pezzulo-2018] organizes the agent into a stack of generative models with explicit message passing across levels.  Within each level the mean-field assumption is re-imposed; cross-stream dependence is captured only through the bottleneck of the inter-level messages.  When two streams at the *same* level depend on each other directly (left hand and right hand; saccade and reach), hierarchical AIF cannot express the dependence without inflating the level structure to a degree that loses biological plausibility.
* **Sophisticated inference.**  Sophisticated inference [@friston-2021] introduces beliefs about beliefs through recursive expected free energy, capturing how an agent's plan depends on what it will *come to believe* once an action is taken.  This is a powerful generalization along the temporal axis but it does not address concurrent cross-stream coupling at a single decision point; the recursion is over future selves, not over peer streams.
* **Branching-time active inference.**  Branching-time AIF [@champion-2022] expands the policy tree and prunes it with Monte Carlo tree search, allowing a much richer enumeration of joint futures.  The price is computational: the policy space scales exponentially in horizon and arity, and the agent must spend search budget the framework does not give it any principled way to allocate.
* **Attention-gating and precision modulation.**  Dopaminergic precision learning [@friston-2014; @schwartenbeck-2015], the broader precision-in-action literature [@limanowski-2024], and structured attention mechanisms [@hoffman-blei-2015] gate which streams influence the posterior at a given moment.  This is well-suited to coarse on / off coupling but provides no continuous parameter for how *strongly* coupled the streams should be, nor any analytical decomposition of the cost paid for coupling.
* **Copula variational inference.**  Copula VI [@tran-2015; @han-2016] retains mean-field marginals and adds a parametric copula on top to model dependence.  The construction is elegant in static settings but does not natively integrate with the EFE / planning side of active inference, and the choice of copula family is a non-trivial modeling commitment that does not interpolate smoothly to or from the mean-field baseline.
* **Tensor-network parameterized variational families.**  Tensor networks — matrix product states, tree-tensor networks, hierarchical Tucker decompositions [@han-2018; @glasser-2019; @verstraete-2008; @eisert-2010] — give compact structured joint distributions with controlled bond dimensions.  We are not aware of a prior active-inference treatment that uses this exact tensor-network family as the policy posterior; one contribution of this manuscript is to show that the parametric coupling below *is* a tensor-network family in disguise, recovering MPS-style algorithmic structure as a side effect.

Across these strategies, the diagnostic pattern is consistent: each one solves a piece of the cross-stream-coupling problem and leaves the remaining pieces to the modeler.  A unified framework needs a single parameter that interpolates between strict mean-field and arbitrary joint structure, a closed-form bookkeeping for the cost of leaving the mean-field manifold, and a *principled* way to classify each neighboring strategy as an exact slice, a parametric modeling route, or a structural analogy.

This placement also clarifies what the manuscript is *not* claiming.
The framework is not a new general account of the Free Energy
Principle, nor a replacement for the process theory of active
inference.  It is a focused extension of the variational family used
for policy inference: the usual mean-field policy posterior remains
the $\lambda=0$ anchor, while finite $\lambda$ represents a controlled
departure from that anchor.  The Markov-blanket and particular-physics
literatures motivate why boundaries and conditional independences
matter for self-organizing systems [@kirchhoff-2018; @ramstead-2018],
and critical reviews warn that those ideas do not automatically
license unrestricted biological or cognitive scope claims
[@aguilera-2021; @raja-2021].  The claim tested here is narrower:
within a finite-POMDP agent whose modeling boundary is already fixed,
cross-stream policy dependence can be made a transparent mathematical
and computational degree of freedom.

## Significance

Six load-bearing properties of the framework:

**(i) Theoretical economy.**  The current AIF literature handles cross-stream coordination through a proliferation of architectural devices: branching-time tree search [@champion-2022], hierarchical / deep AIF with explicit message passing [@pezzulo-2018; @friston-2017; @friston-2017-deep-temporal], sophisticated inference with recursive EFE [@friston-2021], and factor-graph forward-backward over multi-modal generative models [@devries-friston-2017-factor-graph; @friston-parr-devries-2017-graphical-brain; @parr-markovic-kiebel-friston-2019-message-passing; @vandelaar-devries-2017].  Part V classifies these relationships instead of flattening them into one claim: mean-field AIF is the exact $\lambda = 0$ anchor; factor-graph message passing is a parametric implementation route whose inserted policy factor has exact semantics only inside the chosen graph; hierarchical, sophisticated, and branching-time AIF remain structural analogies unless their extra temporal or recursive machinery is explicitly built into $J$ and the generative model.

**(ii) A clean decomposition theorem.**  [[SECREF:decomposition]] below gives a free-energy decomposition ([[THMREF:thm_4_1]]) into (a) per-stream marginal free energies, (b) a coupling / partition-function bundle ($\gamma\lambda\langle K_c\rangle$, $\log Z_E(\lambda)$, and $-\lambda\langle J\rangle$), and (c) the multi-information (total-correlation) term $I(q_\lambda)\geq 0$ — see [[EQREF:tc_decomp]].  The trade-off between coupling and correlation makes precise *when* "joint structure pays for itself" relative to mean-field baselines, where comparable accounts in the structured-VI literature [@saul-jordan-1995; @wainwright-jordan-2008; @hoffman-blei-2015] state the trade-off only implicitly.  Three corollaries follow immediately: [[THMREF:cor_4_2]] (coupling-pays-for-itself verdict), [[THMREF:cor_4_3]] (mean-field reduction at $\lambda = 0$), and [[THMREF:cor_4_4]] (strict gain when $q$ is non-mean-field).

**(iii) Information geometry.**  The family $\{q_\lambda\}$ is an *exponential geodesic* (e-geodesic) departing the mean-field submanifold, which is itself e-flat.  This places the framework on the well-developed scaffolding of dually-flat statistical manifolds [@amari-nagaoka-2000; @amari-2016; @nielsen-2020], and connects revertibility (collapse to mean-field) to the canonical *m-projection* (taking marginals).  Non-extensive analogs via escort / $\phi$-deformed exponential families [@naudts-2011] generalize the construction to systems with non-extensive statistics.

**(iv) Spectral interpretation.**  For bipartite ($K=2$) couplings, the joint posterior $q_\lambda(\pi^1,\pi^2)$ has a Schmidt decomposition; for $K > 2$, a Tucker or tensor-train decomposition.  The leading singular vectors / Tucker factors are **archetypal eigenvectors** — the small number of dominant cross-stream behavioral modes that recur across instances of a habit.  This is a direct probabilistic-graphical-model homologue of bipartite entanglement entropy in quantum many-body systems [@verstraete-2008; @eisert-2010; @han-2018], and inherits all the favorable algorithmic structure of low-rank tensor decomposition.

**(v) Heterogeneous VFE/EFE ensembles.**  Many real agents are mixed: some streams are reflexive (one-step VFE descent) and others plan (EFE counterfactuals).  [[SECREF:heterogeneous]] derives an $O(\lambda^2)$ suboptimality bound ([[THMREF:thm_8_1]]) for VFE-only streams operating inside coupled ensembles.  This formalizes a long-standing intuition: coupled reflexive controllers can ride along with planners *up to a bounded coupling-norm tax* ([[THMREF:cor_8_2]]), providing a quantitative answer to "how reflexive can my low-level controllers be while still benefiting from higher-level planning?"

**(vi) Lean formalizability.**  The framework is built from objects (finite probability distributions, KL divergence, Shannon entropy, Bregman divergences) that are natural targets for Lean's Mathlib [@mathlib-2020].  A prior line of work shipped a 50-topic Mathlib-checked FEP catalog and companion monograph [@friedman-2026-fep-lean]; here, [[SECREF:lean_plan]] documents this manuscript's two-package Lean architecture — a Mathlib4-backed `MathlibProofs/` library that machine-checks the central decomposition ([[THMREF:thm_4_1]]) in $\mathbb{R}$ with foundational-only `#print axioms`, and a stock-Lean [[VAR:lean_toolchain_version]] `ActinfPolicyEntanglement` boundary fragment that ships the [[VAR:theorem_registry_count]]-row theorem surface as a typed API — reusing the same toolchain pin [@demoura-ullrich-2021] and re-export layout as that codebase. The boundary fragment is `sorry` / axiom / Mathlib-free and source-extracted into the manuscript prose; the per-row content table ([[SECREF:lean_plan]]) and the running audit at `docs/reference/veridical_status.md` document what each row certifies at the boundary versus what the Mathlib4 discharge layer establishes.

## Position relative to alternatives

We make a deliberate choice not to take the *embodiment-as-architecture* route of solving the multi-policy problem by partitioning into hardware / software modules with explicit translation layers between symbolic reasoning and low-level control.  That route has well-known costs: the translation layer becomes the entire alignment problem in microcosm, and it is non-differentiable.  Instead, we take the *parametric entanglement* route: tunably couple the policy distributions themselves, leaving the structural distinction between modalities / timescales intact at the level of marginals while permitting arbitrary joint structure to emerge through a learned coupling potential.

This is closest in spirit to: copula variational inference [@tran-2015; @han-2016], structured VI [@saul-jordan-1995; @wainwright-jordan-2008; @hoffman-blei-2015], product-of-experts compositions [@hinton-2002], and tensor-network parameterized variational families [@han-2018; @glasser-2019] — but specialized to the policy-inference setting of active inference with explicit habit ($J$), expected-free-energy ($G$), and sophistication ($\gamma$).  It also connects to KL / path-integral control [@kappen-2005; @theodorou-todorov-2012], options frameworks [@sutton-1999], multi-agent active inference [@maisto-2024], and renormalization-group AIF [@friston-2024].  Part V assigns each connection an exact, parametric, or analogical relationship class, so "connection" never has to mean "full recovery."

## How the framework is developed: four parallel tracks

The manuscript is unusual in that the same mathematical object is developed simultaneously on **four parallel tracks** (prose, equations, Python, Lean), each with its own primary literature, its own quality criteria, and its own role in the overall argument.  The tracks are cross-referenced via a registry of injection tokens; a reader can enter on any track and land on any other in a single hop, and a CI validator fails the build on dangling tokens, hardcoded grid counts, seeds, or rollout horizons.

* **Prose ([[SECREF:setup]] onward).**  The natural-language presentation: definitions, theorem statements, proof sketches, worked examples, interpretive commentary.  Every chapter in Part II opens with the objects under discussion and closes with a three-bullet *Takeaways* box that surfaces the load-bearing claims.  Section numbering is owned by [`manuscript/refs/labels.yaml`](refs/labels.yaml) so that renumbering propagates everywhere automatically.

* **Formalism in equations ([[SECREF:lambda_deformation]], [[SECREF:decomposition]], [[SECREF:geometry]], [[SECREF:spectral]], [[SECREF:heterogeneous]]).**  Every load-bearing identity is a registered equation in the same labels file, auto-numbered as `S.K` and resolved through registry tokens so the manuscript's mathematical structure can be traversed without ever encountering a hand-written equation number.  The four foundational identities — the entanglement decomposition ([[EQREF:tc_decomp]]), the e-geodesic identity ([[EQREF:e_geodesic]]), the Pythagorean decomposition ([[EQREF:pythagorean]]), and the $O(\lambda^2)$ coupling-tax bound ([[EQREF:coupling_tax_bound]]) — anchor the rest.

* **Simulations on real `pymdp` agents ([[SECREF:pymdp_harness]], [[SECREF:pymdp_free_energy]]).**  The empirical layer is *not* a re-implementation of pymdp's mathematics; it instantiates real `pymdp.agent.Agent` objects [@heins-2022] with the JAX backend [@bradbury-2018], runs deterministic fixed-point-iteration inference, and reads off the resulting policy posteriors, expected free energies, and free-energy bundles for every $\lambda$ on the coupling sweep.  The analytical $\lambda$-coupling layer takes those pymdp outputs and adds the cross-stream term — so the simulation tracks exactly the deformation the theorems describe, not a stylized stand-in.  At $\lambda = 0$ the coupled joint is *exactly* the outer product of the pymdp per-stream posteriors; at finite $\lambda$ the joint concentrates on cross-stream archetypes that the bare pymdp run never sees.

* **Lean 4 companions in a real `lake build` environment ([[SECREF:lean_plan]], [[SECREF:app.lean_skeleton]]).**  The formal track is a Lean 4 boundary fragment under [`../lean/`](../lean/) that compiles against stock Lean [[VAR:lean_toolchain_version]] [@demoura-ullrich-2021] with **no Mathlib dependency**, zero strict `sorry`s, zero axioms beyond stock Lean, and no `unsafe` / `partial` / `noncomputable` declarations.  Every theorem in the body that admits a witness-form statement (including [[THMREF:thm_4_1]]) has a Lean companion that *actually compiles* in the project's `lake build`; its source is auto-extracted in the theorem sections and appendix via registry Lean tokens.  The witness-form discipline makes the analytic-content boundary explicit: Mathlib4 is used in the manuscript as the named library context for those analytic obligations, while the current source blocks remain exactly the code that builds today.

The four-track contract is not aspirational; it is CI-gated.  The cross-reference and hyperlink test suites under [`../tests/test_token_resolution.py`](../tests/test_token_resolution.py) and [`../tests/test_project_wide_hyperlinks.py`](../tests/test_project_wide_hyperlinks.py) fail the build if any `[[SECREF:]]`, `[[THMREF:]]`, `[[LEAN:]]`, `[[VAR:]]`, `[[FIG:]]`, or markdown link does not resolve, so a reader who finds a dangling reference has discovered a bug rather than an omission.

## Reading guide

The manuscript has three logical layers; readers can profitably enter at any of the three depending on background.  Choose the *conceptual* path if the question driving you is "why does multi-stream coupling matter and what does it look like when an agent does it well?"; choose the *analytical* path if you want to verify the load-bearing mathematical claims and follow the proofs; choose the *empirical* path if you want to reproduce every numerical result against the pymdp-grounded harness and inspect the JSONL run log.

* **Conceptual / qualitative path.**  This section ([[SECREF:motivation]])
  → [[SECREF:setup]] (POMDP recap) → [[SECREF:lambda_deformation]]
  (the parametric deformation) → [[SECREF:examples]] (worked toys) →
  [[SECREF:phase]] (phase regimes) → [[SECREF:discussion]]
  (worldview).  No proofs required; the closed-form K=2 Bernoulli
  derivation is the fastest entry point to the mathematics.
* **Analytical / theorem path.**  [[SECREF:decomposition]]
  ([[THMREF:thm_4_1]], the load-bearing identity) → [[SECREF:geometry]]
  (e/m-flatness, e-geodesic, Pythagorean) → [[SECREF:spectral]]
  (Schmidt rank, archetypes, tensor-train) →
  [[SECREF:heterogeneous]] (the $O(\lambda^2)$ coupling-tax bound,
  [[THMREF:thm_8_1]]) → [[SECREF:comparative]] (comparative statics).
* **Empirical / reproducibility path.**  [[SECREF:empirical]]
  (closed-form Bernoulli + heterogeneous tax + phase + spectral)
  → [[SECREF:pymdp_harness]] ([[VAR:pymdp_distribution_version]] architecture) →
  [[SECREF:pymdp_free_energy]] (the free-energy bundle and
  derived summary statistics) → [[SECREF:pymdp_validation]]
  (validation gates + JSONL run log + reproducibility contract).

The Lean formalization plan ([[SECREF:lean_plan]], [[SECREF:app.lean_skeleton]]) is orthogonal to all three paths and can be read at any point; every registered theorem in this manuscript names its Lean companion so a reader can navigate prose → theorem-statement → Lean-source in one hop.  A single notation glossary ([[SECREF:notation]]) consolidates every symbol — including manuscript / LaTeX / Python / Lean counterparts — so prose that introduces new symbols can always be cross-referenced without ambiguity.

## Section dependencies (forward signposts)

| Builds on | Used by |
|---|---|
| [[SECREF:setup]] | every later section |
| [[SECREF:lambda_deformation]] | [[SECREF:decomposition]], [[SECREF:examples]], [[SECREF:geometry]], [[SECREF:spectral]] |
| [[SECREF:decomposition]] ([[THMREF:thm_4_1]]) | [[SECREF:examples]], [[SECREF:comparative]], [[SECREF:phase]] |
| [[SECREF:geometry]] ([[THMREF:thm_6_4]], [[THMREF:prop_6_5]]) | [[SECREF:spectral]], [[SECREF:heterogeneous]], [[SECREF:connections]] |
| [[SECREF:spectral]] ([[THMREF:prop_7_1]]) | [[SECREF:phase]], [[SECREF:connections_multi_agent_geometry]] |
| [[SECREF:heterogeneous]] ([[THMREF:thm_8_1]]) | [[SECREF:comparative]], [[SECREF:empirical]] |
| [[SECREF:empirical]] | [[SECREF:pymdp_harness]], [[SECREF:pymdp_free_energy]], [[SECREF:pymdp_validation]] |
| [[SECREF:pymdp_harness]] | [[SECREF:pymdp_free_energy]], [[SECREF:pymdp_validation]] |

---
