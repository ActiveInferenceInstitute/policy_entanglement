# Background and Prior Work: Antecedents in Active Inference, Variational Coupling, Information Geometry, and Tensor Networks

This chapter catalogs the lines of work the framework builds on and points to where each one returns in the body.  Detailed comparisons live in Part V ([[SECREF:connections]], [[SECREF:connections_control_rl]], [[SECREF:connections_multi_agent_geometry]]).  This chapter provides the substantive orientation required for the body of the paper.  The eight subsections below mirror eight axes of structural commitment: a Markov-decision substrate, a variational family, hierarchical / sophisticated extensions, an information-geometric ambient, a low-rank algorithmic backend, a control-theoretic and reinforcement-learning dual, multi-agent / renormalization analogies, and a formal-verification plus reproducible-software scaffold.  Clinical and neural language is treated here as hypothesis-generating context, not as diagnostic evidence.

## Discrete-time POMDP active inference

The discrete-time POMDP formulation of active inference is the home setting throughout.  The standard treatment combines a generative model $(A, B, C, D, E)$ with planning-as-inference under expected free energy [@friston-2010; @friston-2014; @friston-2017; @kaplan-friston-2018; @smith-2022; @sajid-2021; @parr-2022], introducing policies as random variables over which the agent maintains a posterior shaped jointly by past observations and anticipated outcomes.  Recent unification and agency-formalization work further clarifies how multiple expected-free-energy formulations can be derived from shared roots, how EFE-based planning may be recast as variational inference, and how active inference can be used as a model-comparison language for agency [@champion-2024-reframing; @devries-2025; @nuijten-lukashchuk-2025; @dacosta-2024-agency].  That literature is not purely consolidating: Millidge, Tschantz, and Buckley analyze where EFE derivations diverge, so this manuscript treats each per-stream $G_k$ as a specified modeling choice rather than a unique consequence of FEP [@millidge-2021].  Implementations now span several software lineages: `pymdp` targets open-source discrete state-space active inference in Python [@heins-2022], RxInfer.jl supplies reactive variational message passing for real-time Bayesian inference in Julia [@bagaev-2023], ActiveInference.jl provides Julia tooling for POMDP active-inference simulation and parameter estimation [@nehrer-2025], and SPM-DEM remains the continuous-state dynamic-expectation-maximization ancestor [@friston-trujillo-daunizeau-2008].  The present manuscript's empirical harness is built directly against `pymdp` 1.0.1 ([[SECREF:pymdp_harness]]), while the mathematical recap in [[SECREF:setup]] and the Lean recap in [[SECREF:lean_plan]] keep the same generative-model schema explicit.

Within that lineage, expected free energy is the point at which
epistemic and pragmatic control meet: policies are preferred when they
both reduce expected uncertainty and realize prior preferences.
Cognitive-consistency interpretations make the same split visible in
psychological language: epistemic and motivational closure are coupled
but not identical objectives [@friston-2018-cognitive-consistency].
This is why policy coupling is not a cosmetic addition.  If two
policy streams share epistemic opportunities or pragmatic costs,
strict factorization can erase precisely the joint structure through
which the process theory expresses coordinated action; epistemic-value
and navigation examples make that risk concrete in ordinary active
inference before any coupling extension is added
[@parr-friston-2017-uncertainty; @kaplan-friston-2018].  The
action-oriented-model-learning literature makes the same pressure
visible from another angle: agents need models that are parsimonious
because they are oriented toward possible action [@tschantz-2020].
Here the parsimonious object is the coupling potential $J$ and its
scalar strength $\lambda$, rather than an additional hidden-state
factor or hand-designed controller interface.  Factor-graph and
graphical-brain accounts show how generative-model structure induces
message-passing schedules [@devries-friston-2017-factor-graph;
@friston-parr-devries-2017-graphical-brain], and approximation-family
work distinguishes mean-field, Bethe, and marginal message passing as
different commitments about how local beliefs compose
[@parr-markovic-kiebel-friston-2019-message-passing; @yedidia-2005].
The word "free energy" is doing different work across those lineages:
Bethe / Kikuchi free energies govern approximate marginal inference
on factor graphs, while active inference adds policy selection,
preferences, and epistemic terms.  In the present manuscript, an
additional policy factor can implement the
$\lambda$-coupling inside a chosen graph; the exactness belongs to
that chosen graphical model, not to active inference in the abstract.

The standard discrete-POMDP treatment commits to *one* policy random variable per agent, or to a factorized family of per-factor policy posteriors when the model is decomposed.  That design is tractable, but multi-stream coordination is then carried by the modeling factorization rather than by an explicit coupling object [@dacosta-2020; @smith-2022].  This commitment is the entry point for the parametric coupling introduced in [[SECREF:lambda_deformation]].

## Mean-field variational families and their limits

Mean-field factorization is the workhorse approximation of variational inference and its active-inference instantiation: factorize the joint posterior across hidden-state factors, observation modalities, and policy variables to make the per-factor updates tractable [@wainwright-jordan-2008; @blei-kucukelbir-mcauliffe-2017; @dacosta-2020; @smith-2022].  The cost is well known and well-studied: Hoffman and Blei note that the independence approximation "limits the fidelity" of the approximation [@hoffman-blei-2015], while Blei, Kucukelbir, and McAuliffe present mean-field and structured variational families as choices in an optimization problem rather than as exact posterior semantics [@blei-kucukelbir-mcauliffe-2017].  In the present setting, any genuine cross-factor dependence is discarded, and the magnitude of the resulting bias is measured by the multi-information between factors — the same quantity that appears as the surcharge in [[THMREF:thm_4_1]].  The point is not that mean-field is wrong; it is that mean-field lacks an internal observable for the dependence it has projected away.

Three lines of prior work attempt to relax mean-field while preserving tractability:

* **Structured VI** preserves selected dependency substructures while approximating the remaining interactions [@saul-jordan-1995; @wainwright-jordan-2008; @blei-kucukelbir-mcauliffe-2017], and structured stochastic VI [@hoffman-blei-2015] introduces dependence between subsets of variables via amortized sub-models with shared parameters, capturing coarse-grained dependencies at the cost of additional architectural commitment.
* **Copula variational inference** [@tran-2015; @han-2016] inserts a parametric copula on top of the mean-field marginals, preserving the per-stream factor structure and confining dependence to the copula density in the classical copula sense [@nelsen-2006].
* **Tensor-network parameterized variational families** [@biamonte-2017; @cichocki-2016; @han-2018; @glasser-2019] use matrix-product-state and tree-tensor-network factorizations as compact joint distributions, importing algorithmic infrastructure from tensor-network physics and numerical multilinear algebra [@verstraete-2008; @eisert-2010; @orus-2014].

The framework here is a parametric interpolation across all three:
$\lambda = 0$ recovers strict mean-field; finite $\lambda$ with
appropriate $J$ realizes products of experts exactly, copula VI
parametrically, and tensor-network variational structure as the
algorithmic backend for low-rank coupling ([[SECREF:connections_control_rl]]).
Crucially, these are structural correspondences, not benchmark
claims: at each exact or parametric specialization the entanglement
decomposition of [[THMREF:thm_4_1]] reduces by substitution to the
relevant variational-free-energy expression.  Where the relationship
is only analogical, such as renormalization-group AIF, the recovery
dictionary marks it as analogical rather than exact.

## Hierarchical, deep, and sophisticated active inference

Hierarchical / deep active inference [@friston-2017; @friston-2017-deep-temporal; @pezzulo-2018] decomposes the agent into a hierarchy of generative models with explicit message passing across levels — a treatment that captures temporally-extended structure and cortically-plausible scale separation [@friston-2024], but that retains the mean-field assumption *within* each level.  Sophisticated inference [@friston-2021] introduces beliefs about beliefs through recursive expected free energy, modeling how an agent's plan depends on the beliefs it anticipates having after taking an action.  Branching-time AIF [@champion-2022] addresses the exponential cost of policy enumeration via Monte Carlo tree search applied to the EFE tree.

Each motivates a different structural choice, but none should be read
as a full exact recovery in the current artifact.  Hierarchical AIF
corresponds to block-bidiagonal $J$ as a cross-level concentration
witness ([[THMREF:thm_11_1]]), while temporal-scale separation and
directed top-down / bottom-up message passing remain part of the
source process theory.  Sophisticated inference embeds with
recursion-depth-many streams and a belief-about-belief $J$
([[THMREF:prop_11_2]]), while the recursive observation-conditioning
is a constraint on how that $J$ is supplied.  Branching-time AIF
suggests tensor-train or prefix-tree compression of $q_\lambda$, but
the present manuscript does not run a head-to-head BTAI algorithmic
comparison.  The detailed mappings are tabulated in [[SECREF:connections]]
and the appendix recovery ledger.

## Information geometry

Dually-flat statistical manifolds, $e$- and $m$-coordinates, $\alpha$-projections, and Bregman divergences are the natural language for parametric extensions of variational families [@amari-nagaoka-2000; @amari-2016; @nielsen-2020; @ay-jost-le-schwachhofer-2017].  The $\lambda$-deformation lives on this scaffolding: $\{q_\lambda\}$ is an $e$-geodesic ([[THMREF:thm_6_4]]), the mean-field submanifold is $e$-flat ([[THMREF:prop_6_1]]), and revertibility (collapse to mean-field marginals) is the canonical $m$-projection ([[THMREF:prop_6_2]]).  The Pythagorean decomposition ([[THMREF:prop_6_5]]) provides an exact split of the KL from the entangled posterior to any reference distribution into a multi-information term and a marginal-to-reference KL.

Non-extensive generalizations via Tsallis / Rényi entropies and escort distributions [@naudts-2011] yield $\phi$-deformed exponential families on which the same construction goes through with quantitatively different geometry; we flag the $q$-deformed analog as a natural extension ([[SECREF:geometry.escort]]) without developing it here.  Information geometry also supplies vocabulary used in integrated-information studies of consciousness [@tononi-2008], but the present framework makes only a policy-space analogy: total correlation and low-rank structure quantify dependence among policy streams after the modeling boundary is fixed.  It does not claim to solve consciousness, define phenomenology, or validate an integrated-information theory.

## Tensor networks and entanglement entropy

Schmidt decomposition, matrix-product states, and the area law of entanglement entropy [@verstraete-2008; @eisert-2010] supply both the algorithmic backend and the conceptual vocabulary for the spectral structure of entangled posteriors.  General tensor-network surveys and machine-learning treatments supply the computational bridge from that physics vocabulary to low-rank tensor representations of high-dimensional arrays [@biamonte-2017; @cichocki-2016; @orus-2014].  In the bipartite ($K=2$) case the joint $q_\lambda(\pi^1, \pi^2)$ admits a Schmidt decomposition whose leading singular vectors are the *archetypal eigenvectors* — the few dominant cross-stream behavioral modes ([[SECREF:spectral]]).  For $K > 2$ a tensor-train factorization with bond-dimension profile $(r_1, \ldots, r_{K-1})$ controls representational capacity ([[THMREF:prop_7_1]], [[SECREF:app.tt_inference]]).

The tensor-network perspective also gives the framework its sharpest computational claim: low-rank coupling potentials produce low-rank posteriors ([[THMREF:thm_7_3]], the *sparsity-rank tradeoff*), making structured-coupling inference scalable in the bond dimension rather than in the raw policy-space size.  The tensor-network literature has independently developed efficient inference algorithms — DMRG, TEBD, MERA [@han-2018; @glasser-2019; @schollwock-2011] — that become available once a coupling potential is represented in a tensor-network form; the present artifact demonstrates the rank/bond-profile side of that claim through the multi-$K$ sweep and tensor-train figures, while full tensor-network inference is left as an algorithmic extension. Categorical-systems-theory formulations of structured active inference [@smithe-2024-structured] further suggest that the same compositional vocabulary admits formal-verification-amenable presentations of structured policies.  All tensor-network language in the manuscript is therefore a probability-tensor and linear-algebra analogy.  It is not a claim that policy streams are quantum subsystems, or that quantum entanglement semantics are being imported into active inference.

## KL / path-integral control and reinforcement learning

KL / path-integral control duality [@kappen-2005; @todorov-2006; @theodorou-todorov-2012; @rawlik-toussaint-vijayakumar-2013] formalizes the equivalence between stochastic optimal control and free-energy minimization: the value function under a controlled stochastic system is the log-partition of an unnormalized path measure weighted by exponentiated cost.  The options framework / hierarchical RL [@sutton-1999; @barto-mahadevan-2003; @bacon-harb-precup-2017; @doll-2015] decomposes long-horizon RL into reusable temporally-extended sub-policies with explicit initiation / termination structure.  Both fit cleanly into the parametric construction when the required factors are supplied: KL control corresponds to the special-purpose choice in which $\lambda J$ is the negative control-effort cost (single-stream limit); options correspond to an option-like two-stream factorization with $J$ encoding option-membership structure ([[SECREF:connections_control_rl]]).

A subtler connection is to **products of experts** [@hinton-2002]: the $\lambda$-entangled prior $\mathcal{E}_\lambda(\pi) = \prod_k E_k(\pi^k)\,e^{\lambda J(\pi)}$ is literally a product of experts on joint policy space, with the coupling potential acting as one additional expert that *only* fires on configurations where the cross-stream relationship holds.

## Multi-agent inference, Markov blankets, and renormalization

Interactive / multi-agent active inference [@maisto-2024] models multi-agent cooperation as joint inference under shared generative models, while collective active-inference models show how group-level coordination can arise from surprise minimization under coupled generative models [@heins-2024-collective].  Renormalization-group AIF [@friston-2024] derives hierarchical generative models via repeated application of a coarse-graining operator that preserves dynamics-form.  Bayesian-mechanics treatments of Markov blankets [@friston-2019; @dacosta-friston-heins-pavliotis-2021] identify a system with a partition of states into internal / external / blanket, while Markov-blanket accounts of autonomy emphasize that a system boundary is an inferential and conditional-independence structure rather than just a physical envelope [@kirchhoff-2018; @ramstead-2018].  The critical literature is important here: both technical and philosophical reviews argue that Markov blankets require careful modeling assumptions and do not, by themselves, settle the scope of FEP, active inference, or cognitive boundaries [@aguilera-2021; @raja-2021; @menary-gillett-2022].

All three relate to $NK$-stream entanglement only after the modeling
boundary and coupling graph are specified.  Multi-agent inference is a
parametric joint-policy prior when within-agent and across-agent
blocks of $J$ are added to a shared or linked generative model.
Renormalization-group AIF is an analogy between coarse-graining and
low-rank policy-posterior projection.  Markov-blanket separation is a
policy-space analog quantified by normalized multi-information
([[SECREF:connections_multi_agent_geometry]]), not a recovery of the
state-space blanket construction.  The manuscript therefore does not
infer new biological boundaries from $J$; it supplies a way to measure
and manipulate policy dependence once a modeling boundary has already
been chosen.

## Computational psychiatry and neural implementation

Computational-psychiatry programs use AIF to model dysregulation of perception, action, and learning [@adams-2013; @schwartenbeck-friston-2016], often associating symptom dimensions with failure modes of the free-energy-minimization machinery (sensory precision dysregulation, prior over-weighting, habit rigidity).  Dopaminergic / policy-precision accounts [@friston-2014; @schwartenbeck-2015; @parr-friston-2017-working-memory] and recent precision-in-action reviews [@limanowski-2024], together with empirical precision-weighting evidence in psychosis [@haarsma-2021], motivate the precision vocabulary, but the present framework borrows only the *formal* precision analogy for $\lambda$ ([[SECREF:heterogeneous.precision]]).  It does not identify $\lambda$ with dopamine, synaptic gain, or any specific neural variable.

The phase-structure analysis in [[SECREF:phase]] flags a *coupling-drift* failure mode (under- or over-coupling of behavioral streams) that is qualitatively distinct from per-stream prior corruption.  We treat the clinical language as a model-generated hypothesis, not a diagnostic claim: if the coupling account is right, controlled tasks would be expected to reveal cross-stream covariance signatures (joint-action repertoire, between-trial mode statistics, coupling-spectrum effective rank) that are not visible in per-stream marginal measures alone.  This is consistent with the habit-vs-deliberation balance literature [@doll-2015] while adding an explicit coupling parameter that a follow-up empirical protocol could estimate.

## Lean 4, Mathlib, and formal verification of probabilistic systems

Lean 4 [@demoura-ullrich-2021; @lean-fro-2026] and the Mathlib library [@mathlib-2020; @lean-fro-mathlib-2026] are the formal-verification backbone of the present work.  Lean 4 is a dependently-typed proof assistant with a minimal trusted kernel and a tactic framework expressive enough to mechanize contemporary mathematics; Mathlib provides — among many other things — the measure theory, linear algebra, and analysis targeted by the separate additive discharge of the framework's witness-form theorems.

A prior line of work shipped a 50-topic Mathlib-checked FEP catalog and companion monograph [@friedman-2026-fep-lean]; the present manuscript's `ActinfPolicyEntanglement` boundary fragment ([[SECREF:lean_plan]], [[SECREF:app.lean_skeleton]]) reuses the same toolchain pin and re-export layout, with witness-form theorems isolating the analytic content for a separate Mathlib4 discharge layer.  Every numbered theorem in this manuscript — including the spectral semicontinuity and tensor-train rank claims of [[SECREF:spectral]] ([[THMREF:prop_7_2]], [[THMREF:thm_7_3]]) and the hierarchical / sophisticated-inference embeddings of [[SECREF:connections]] ([[THMREF:thm_11_1]], [[THMREF:prop_11_2]]) — now carries a live Lean companion in that fragment.  The choice to keep the present fragment **Mathlib-free** is deliberate: it forces every theorem statement to be expressible in the in-house `CommScalar α` typeclass, exposes the analytic content as explicit witness arguments, and makes the boundary's hygiene budget (zero strict `sorry`, zero axioms, zero `unsafe` / `partial` / `noncomputable`) easy to verify against stock Lean [[VAR:lean_toolchain_version]].

The verified-numerics boundary remains separate from this proof story.
Numerical analysis supplies the right vocabulary for round-off,
conditioning, and stability [@higham-2002], while IEEE 754 fixes the
floating-point arithmetic standard a formal bridge would have to model
[@ieee-754-2019], and proof-assistant floating-point libraries such as
Flocq show what such a bridge requires [@boldo-melquiond-2011].  The present artifact
machine-checks the exact $\mathbb{R}$ mathematics and tests the Float
pipeline to strict tolerances; it does not claim a formal
Float$\leftrightarrow\mathbb{R}$ theorem.

## Reproducible scientific software

The empirical layer is built on NumPy [@harris-2020], SciPy [@virtanen-2020], JAX [@bradbury-2018] (which underpins `pymdp` 1.0.1), and Matplotlib [@hunter-2007].  Every numeric value in the manuscript flows from a real run via the `[[VAR:<key>]]` token system ([[SECREF:pymdp_validation]]); every figure carries reproducibility tEXt metadata (source script, function, hyperparameter snapshot, git revision, ISO timestamp, and compact plotted-data summaries); every cross-reference resolves through the same registry that the renderer consumes.  This positions the manuscript inside the broader open-science / reproducible-research practice and — concretely — makes the manuscript an executable artifact: running `scripts/run_all.py` regenerates every numeric, every figure, and every theorem-table row from a single deterministic pipeline.

---
