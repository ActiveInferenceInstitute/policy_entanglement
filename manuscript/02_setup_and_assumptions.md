# Setup, Notation, Standing Assumptions

We work throughout with finite, discrete state and action spaces — adequate for the analytical results, computationally tractable, and aligned with the discrete-time POMDP formulation that dominates AIF practice (`pymdp`, `RxInfer`, `ActiveInference.jl`, SPM-DEM). Continuous extensions are sketched in [[SECREF:discussion]].

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

VFE-only streams are obtained by treating $G$ as a one-step variational objective (no recursive lookahead), where action selection is the gradient step on $F$ at the current belief; the policy distribution effectively collapses to a delta on the next-action argmin. In planning-as-inference with $\gamma$ moderate, $q(\pi)$ remains a proper distribution over the policy space.

## The multi-stream extension

We posit $K$ concurrent policy variables

$$\pi = (\pi^1, \pi^2, \ldots, \pi^K), \qquad \pi^k \in \Pi^k, \qquad \Pi = \prod_{k=1}^K \Pi^k.$$

**Generic streams.** The $K$ streams are generic in three independent senses, all of which the framework handles uniformly:

- **Modality.** Each stream may correspond to a distinct observation modality (visual, auditory, proprioceptive) and/or distinct hidden-state factor (location, identity, intent).
- **Time horizon.** Streams may differ in planning horizon $T_k$ — a fast attentional policy with $T_a = 1$ and a slow navigational policy with $T_n = 10$ are simultaneously representable.
- **Inference mode.** Each stream may use VFE-only, EFE-planning, or sophisticated inference (recursive EFE; [@friston-2021]).

Let $\mathcal{V} \subseteq \{1,\ldots,K\}$ index VFE-only streams and $\mathcal{P} = \{1,\ldots,K\} \setminus \mathcal{V}$ index planning streams.

## The mean-field baseline

Strict mean-field across streams:

$$E_{\mathrm{MF}}(\pi) = \prod_{k=1}^K E_k(\pi^k), \qquad G_{\mathrm{MF}}(\pi) = \sum_{k=1}^K G_k(\pi^k), \qquad q_{\mathrm{MF}}(\pi) = \prod_{k=1}^K q_k(\pi^k),$$

with each $q_k(\pi^k) \propto E_k(\pi^k)\exp(-\gamma_k G_k(\pi^k))$ a single-stream posterior. This is the regime exemplified by `pymdp`'s factorized-A, factorized-B, factorized-policy treatment of multi-factor models [@heins-2022].

**Standing notation.**
- $H(\cdot)$: Shannon entropy.
- $D_{\mathrm{KL}}(p\|q)$: Kullback-Leibler divergence.
- $I(p) = \sum_k H(p^k) - H(p)$: total correlation (multi-information) of joint $p$ with respect to its $K$ marginals $p^k$.
- $\mathcal{M}$: manifold of joint distributions on $\Pi$.
- $\mathcal{M}_{\mathrm{MF}} \subset \mathcal{M}$: mean-field submanifold (product distributions).

---
