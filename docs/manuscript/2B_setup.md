# Setup and Assumptions: Finite-Horizon Discrete POMDPs, Multi-Stream Policy Factorization, and the Mean-Field Baseline

We work throughout with finite, discrete state and action spaces — adequate for the analytical results, computationally tractable, and aligned with the discrete-time POMDP formulation that dominates AIF practice (`pymdp`, `RxInfer`, `ActiveInference.jl`, SPM-DEM) [@heins-2022; @bagaev-2023; @nehrer-2025; @friston-trujillo-daunizeau-2008]. Continuous extensions are sketched in [[SECREF:discussion]].  Every symbol introduced here also appears in the unified notation glossary ([[SECREF:notation]]) with its LaTeX, Python, and Lean counterparts.

## Single-stream POMDP active inference

A standard discrete POMDP active inference unit:

| Symbol | Meaning |
|---|---|
| $s \in \mathcal{S}$ | hidden state (finite) |
| $o \in \mathcal{O}$ | observation (finite) |
| $a \in \mathcal{A}$ | action (finite) |
| $\pi \in \Pi$ | policy: sequence/map of actions over horizon $T$ |
| $A_{ij} = p(o = i \mid s = j)$ | likelihood matrix |
| $B^a_{ij} = p(s' = i \mid s = j, a)$ | transition tensor |
| $C(o) = \log \tilde p(o)$ | log-prior preferences |
| $D(s) = p(s_0)$ | initial state prior |
| $E(\pi)$ | habit / policy prior on $\Pi$ |
| $\gamma$ | policy precision |

Under planning-as-inference with expected free energy [@friston-2014; @dacosta-2020]:

$$q(\pi) \propto E(\pi) \exp\!\big(-\gamma\, G(\pi)\big), \qquad G(\pi) = \mathrm{Risk}(\pi) + \mathrm{Ambiguity}(\pi)$$

with the standard EFE decomposition into pragmatic and epistemic components

$$G(\pi) = \underbrace{\mathbb{E}_{q(o,s\mid\pi)}\big[\log q(s\mid \pi) - \log p(s\mid o,\pi)\big]}_{\text{epistemic value, negated}} + \underbrace{\mathbb{E}_{q(o\mid\pi)}\!\big[D_{\mathrm{KL}}(q(o\mid\pi)\,\|\,\tilde p(o))\big]}_{\text{pragmatic value, negated}}.$$

(Sign conventions for $F$, $G$, $K_c$ are cataloged in [[SECREF:notation.sign_conventions]]; the "negated" annotations above match the standard EFE convention there.)

VFE-only streams are obtained by treating $G$ as an immediate variational objective (no recursive lookahead), where action selection is the gradient step on $F$ at the current belief; the policy distribution effectively collapses to a delta on the next-action argmin. In planning-as-inference with $\gamma$ moderate, $q(\pi)$ remains a proper distribution over the policy space.

Having fixed the single-stream POMDP baseline, we now generalize to the
multi-stream setting that is the substantive subject of this manuscript.

## The multi-stream extension

We posit $K$ concurrent policy variables

$$\pi = (\pi^1, \pi^2, \ldots, \pi^K), \qquad \pi^k \in \Pi^k, \qquad \Pi = \prod_{k=1}^K \Pi^k.$$

**Generic streams.** The $K$ streams are generic in three independent senses, all of which the framework handles uniformly:

- **Modality.** Each stream may correspond to a distinct observation modality (visual, auditory, proprioceptive) and/or distinct hidden-state factor (location, identity, intent).
- **Time horizon.** Streams may differ in planning horizon $T_k$ — a fast attentional policy and a slow navigational policy are simultaneously representable without forcing them onto a shared clock.
- **Inference mode.** Each stream may use VFE-only, EFE-planning, or sophisticated inference (recursive EFE; [@friston-2021]).

Concretely: a drummer's left-hand timing stream (motor modality, short horizon, reflexive VFE) co-exists with a right-hand fill-planning stream (motor modality, longer horizon, EFE planning); an autonomous vehicle couples a very short-horizon steering controller (proprioceptive, VFE) with a much longer-horizon route planner (symbolic, EFE) and an intermediate-horizon attention allocator (visual, EFE); a reading-while-reaching agent factors immediate saccade policy (visual, VFE) from short-horizon reach policy (proprioceptive, EFE).  In each example the streams differ along at least two of the three axes above, and the *coordination* between them is precisely what the entanglement framework formalizes.

Let $\mathcal{V} \subseteq \{1,\ldots,K\}$ index VFE-only streams and $\mathcal{P} = \{1,\ldots,K\} \setminus \mathcal{V}$ index planning streams.  The heterogeneous-ensemble pay-off when these two stream classes are coupled is developed in [[SECREF:heterogeneous]].

## The mean-field baseline

Strict mean-field across streams:

$$E_{\mathrm{MF}}(\pi) = \prod_{k=1}^K E_k(\pi^k), \qquad G_{\mathrm{MF}}(\pi) = \sum_{k=1}^K G_k(\pi^k), \qquad q_{\mathrm{MF}}(\pi) = \prod_{k=1}^K q_k(\pi^k),$$

with each $q_k(\pi^k) \propto E_k(\pi^k)\exp(-\gamma_k G_k(\pi^k))$ a single-stream posterior. This is the regime exemplified by `pymdp`'s factorized-A, factorized-B, factorized-policy treatment of multi-factor models [@heins-2022].

**Standing assumptions.**
- Every per-stream policy alphabet $\Pi^k$ is finite; the joint $\Pi = \prod_k \Pi^k$ is therefore finite. Continuous-policy extensions are conjectured in [[SECREF:open_questions]] (Q4) but are out of scope for the analytical core of this manuscript.
- The per-stream priors $E_k$ are strictly positive on $\Pi^k$ (no exact zeros), so KL divergences and log-likelihoods are everywhere finite.
- The per-stream EFE $G_k$ and coupling potentials $J$, $K_c$ are real-valued and bounded on $\Pi$, so $\mathbb{E}_{q_\lambda}[\,\cdot\,]$ exists for every observable used below and the Gibbs partition function $Z(\lambda)$ is real-analytic in $\lambda$ on $[0,\infty)$.

**Standing notation.**
- $H(\cdot)$: Shannon entropy.
- $D_{\mathrm{KL}}(p\|q)$: Kullback-Leibler divergence.
- $I(p) = \sum_k H(p^k) - H(p)$: total correlation (multi-information [@mcgill-1954; @watanabe-1960]) of joint $p$ with respect to its $K$ marginals $p^k$ (see [[EQREF:total_correlation]]).
- $\mathcal{M}$: manifold of joint distributions on $\Pi$.
- $\mathcal{M}_{\mathrm{MF}} \subset \mathcal{M}$: mean-field submanifold (product distributions); its e-flatness is recorded in [[THMREF:prop_6_1]] and developed in [[SECREF:geometry]].

---
