# Framework Connections III: Multi-Agent Inference, RG-AIF Coarse-Graining, Markov Blankets, and CEREBRUM Case Grammar

This sub-section closes [[SECREF:connections]] by mapping the
entanglement framework onto multi-agent active inference,
renormalization-group treatments, the Markov-blanket / Bayesian-mechanics
worldview, and CEREBRUM-style case-grammar architectures.

## Interactive Inference / Multi-Agent Active Inference

Interactive inference [@maisto-2024] models multi-agent cooperation as
joint inference under shared generative models. Collective
active-inference models add a complementary population-scale result:
coordinated behavior can emerge from surprise minimization without
treating the group result as a proof of any particular finite-policy
coupling theorem [@heins-2024-collective].

The multi-agent active inference literature has expanded substantially
since 2022. Federated inference and belief sharing
[@friston-2024-federated] models belief broadcasting across agents;
Shared Protentions [@albarracin-2024] formalizes coordinated
anticipation; collective surprise-minimization models
[@heins-2024-collective] show how coordination can emerge at population
scale; *As One and Many* [@waade-2025] relates individual to
emergent group-level generative models; Factorized Active Inference
for Strategic Multi-Agent Interactions [@ruiz-serra-2025] explicitly
notes the current default mean-field-across-agents assumption — which
our $\lambda$-deformation relaxes. The framework here provides the
scalar deformation parameter for the policy-coupling part of these
lines, not a full multi-agent process theory by itself.

**Connection.** A multi-agent setting with $N$ agents each with $K$
policy streams maps onto a single $NK$-stream entanglement only after
the modeler fixes agent boundaries, shared or separate generative
models, and the within-agent / across-agent blocks of $J$. Under that
explicit parameterization, the framework gives a joint-policy prior
for single-agent multi-stream coordination and multi-agent joint
action under the same scalar coupling parameter. Without that
generative-model choice, the connection is structural rather than an
identity with any particular federated-inference paper.

This is conceptually clean at the level of the variational family:
from the perspective of policy entanglement, *interpersonal*
coordination and *intrapersonal* coordination can use the same
cross-stream coupling machinery once the modeler has chosen the
agent boundaries, observation model, and shared or separate
generative models. The claim class is therefore `parametric`, not
`proved` or `exact` for the multi-agent literature as a whole.

## Renormalization-group active inference (structural analogy)

Scale-free active inference, formalized as Renormalizing Generative
Models (RGMs) [@friston-2024], coarse-grains across temporal/spatial
scales preserving the form of the generative model. Our framework's
tensor-train compression of $q_\lambda$ (bond-dimension truncation)
provides a *coarse-graining analog at the policy-posterior level*:
low-rank truncation projects out high-spectral-rank correlations,
akin to integrating out fast modes. We emphasize this is an
*analogy*, not a recovery: a full RG-AIF correspondence would require
a MERA-style scale-invariant ansatz (not standard tensor-train),
which we do not develop here. The proper RG-AIF reference is RGM
[@friston-2024] and we cite it as the canonical scale-free AIF
construction.

## Markov Blankets and Bayesian Mechanics

The Markov blanket / Bayesian-mechanics formulation of FEP
[@friston-2019; @dacosta-friston-heins-pavliotis-2021;
@kirchhoff-2018; @aguilera-2021; @raja-2021;
@menary-gillett-2022]
identifies a system with a partition of states into
internal/external/blanket. In our framework, *streams* are candidate
partitions of the agent's policy space chosen by the modeler, and the
factorization structure of $q_\lambda$ across streams induces a
policy-space analog of the blanket idea.

**[[THMREF:prop_11_3]] Policy-space Markov blankets.** We extend the
Markov-blanket idea from state-space [@friston-2019;
@dacosta-friston-heins-pavliotis-2021; @kirchhoff-2018;
@aguilera-2021; @raja-2021; @menary-gillett-2022]
to policy-space: define the *policy-blanket leakage* of a joint $q$
on $\Pi^1 \times \cdots \times \Pi^K$ as the normalized
multi-information

$$\eta(q) = I(q) / H(q) \in [0, 1].$$

At $\lambda = 0$ we have $\eta(q_0) = 0$ (perfect factorization
across streams; policy posteriors are conditionally independent given
marginals); at $\lambda > 0$, $\eta(q_\lambda) > 0$ measures the
leakage of cross-stream information that would be lost under a
mean-field projection. We emphasize this is a policy-space analog,
not a recovery of the state-space Markov-blanket construction; the
two are formally distinct.

## CEREBRUM and case-grammar approaches

CEREBRUM (Case-Enabled Reasoning Engine with Bayesian
Representations for Unified Modeling) [@friedman-2025-cerebrum] explores
grammatical case as a structuring principle for cognitive architectures.  The connection to
policy entanglement: cases encode *role-relations* across cognitive
operations, which are precisely cross-stream coupling structures.  A
nominative-accusative case relation between two streams corresponds to
a directional asymmetry in $J$.  The framework therefore provides a
parametric probabilistic backend for case-grammar cognitive
architectures once the case roles have been encoded as edge-weight
asymmetries in $J$.

A *compositional* reading of these case-grammar architectures sharpens
the connection. Following the category-theoretic account of
[@friedman-2026-compositional-case], let $\mathcal{K}$ be a
compact-closed case category whose objects are case roles, whose
morphisms are role-composing sentence and discourse circuits (in the
DisCoCat / DisCoCirc sense), and whose hom-objects are enriched over
$[0,1]$ as magnitudes; an *alignment pattern* is then a functor
$\alpha : \mathcal{K} \to \mathbf{Coup}_K$ into a category of
directional couplings on the $K$-stream policy space, and — when
this substrate is supplied — the habit potential of
[[SECREF:lambda_deformation]] can be written as the pullback
$J = \alpha^{\ast}\Phi$ of a weighting $\Phi$ on $\mathcal{K}$. Two cognitive-architecture decisions
then sit on distinct objects: a *choice of case system* (nominative–
accusative, ergative–absolutive, fluid-$S$, split-ergative) is a choice
of $\mathcal{K}$ and its alignment functor $\alpha$, while the
*coupling strength* of the present framework is the scalar $\lambda$
that scales the pulled-back potential $\lambda J$ inside
$\mathcal{E}_\lambda$. Topos-theoretic Morita equivalence between alignment frames in the
sense of [@friedman-2026-compositional-case] then predicts when two
surface-different case-graded couplings induce the *same* entangled
posterior — a non-identifiability condition on $J$ that is invisible
at the level of the coupling graph alone. The recovery
class is unchanged: the categorical layer supplies the substrate on
which case roles license edge-weight asymmetries in $J$, but choosing
$\mathcal{K}$ and $\alpha$ remains an explicit modeling commitment, so
the mapping stays `parametric` rather than `exact`.

The interaction graph of $J$ across multiple streams is itself a
useful diagnostic — symmetric all-to-all coupling (as in the K=4 Ising
ensemble below) appears as an evenly-weighted clique, while
asymmetric / hierarchical / case-graded couplings would manifest as
edge-weight heterogeneity:

[[FIG:coupling_graph]]

---
