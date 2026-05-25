# Lambda Deformation: Definition and Properties

In symbols: $q_\lambda(\pi) \propto q_{\mathrm{MF}}(\pi)\,e^{\lambda(J(\pi) - \gamma K_c(\pi))}$, with $q_{\mathrm{MF}}$ the mean-field baseline introduced in [[SECREF:setup.mf_baseline]] and the entangled-prior / entangled-posterior expansion derived below.

The symbols introduced below — $J$, $K_c$, $\lambda$, $\gamma$,
$\mathcal{E}_\lambda$, $q_\lambda$ — are cataloged in the unified
notation glossary ([[SECREF:notation]]) with their LaTeX, Python,
and Lean counterparts.

## Coupling potentials

Introduce two real-valued coupling potentials on the joint policy space:

- $J: \Pi \to \mathbb{R}$ — *habit coupling* (prior-side): structural cross-stream tendencies that the agent has built up and considers a-priori plausible.
- $K_c: \Pi \to \mathbb{R}$ — *preference coupling* (EFE-side): cross-stream costs/preferences that show up in expected free energy beyond the per-stream EFEs.

These need not be informed by anything outside the agent: they are parameters of the agent's generative model, learned from experience.

## Definition: lambda-entangled policy posterior

Define the **$\lambda$-entangled prior** and **$\lambda$-entangled posterior** as

$$\boxed{\;\mathcal{E}_\lambda(\pi) \;=\; \frac{1}{Z_E(\lambda)} \prod_{k=1}^K E_k(\pi^k)\,\exp\!\big(\lambda\, J(\pi)\big)\;}$$

$$\boxed{\;G_\lambda(\pi) \;=\; \sum_{k=1}^K G_k(\pi^k) \;+\; \lambda\, K_c(\pi)\;}$$

$$\boxed{\;q_\lambda(\pi) \;\propto\; \mathcal{E}_\lambda(\pi)\,\exp\!\big(-\gamma\, G_\lambda(\pi)\big) \;=\; \frac{1}{Z(\lambda)}\!\left[\textstyle\prod_k E_k(\pi^k)\!\right]\!\exp\!\big(\lambda(J(\pi) - \gamma K_c(\pi)) - \gamma\textstyle\sum_k G_k(\pi^k)\big)\;}$$

**Boundary cases.**
- $\lambda = 0$: $\mathcal{E}_0 = E_{\mathrm{MF}}$, $G_0 = G_{\mathrm{MF}}$, $q_0 = q_{\mathrm{MF}}$.
- $\lambda \to \infty$: $q_\lambda$ collapses onto the modes of $J - \gamma K_c$ — *pure archetypal joint policies*. (Here "modes" means elements of the argmax set $\operatorname*{argmax}_\pi (J(\pi) - \gamma K_c(\pi))$. As $\lambda \to \infty$, $q_\lambda$ concentrates on this argmax set, with mass restricted to and re-normalized over those policies weighted by the bare-posterior measure $E_{\mathrm{MF}}(\pi)\,e^{-\gamma G_{\mathrm{MF}}(\pi)}$; in particular, when $E_{\mathrm{MF}}$ and $G_{\mathrm{MF}}$ are constant on the argmax set, $q_\lambda$ concentrates uniformly on the set.)
- Intermediate $\lambda$: the regime of practical interest.

For analytical separation of habit vs. preference coupling, one can carry two parameters $\lambda_E, \lambda_G$ with coupling potentials $J, K_c$ respectively. We use a single $\lambda$ in the body of the paper for clarity, with the two-parameter generalization appearing in [[SECREF:comparative]] for comparative statics.

## The coupling parameter lambda as a precision-like coupling weight

A central conceptual point: $\lambda$ is *not* merely an arbitrary engineering knob. In the exponential-family representation it behaves as a **precision-like inverse-temperature** on the coupling structure, dual (in the Legendre sense) to the sufficient statistics $\langle J \rangle$ and $\langle K_c \rangle$ under the joint posterior. This is mathematically analogous to the role $\gamma$ plays for EFE in the standard single-stream model, while remaining a distinct model parameter rather than a claim about any specific neural precision signal. Concretely:

$$\frac{\partial \log Z(\lambda)}{\partial \lambda} = \langle J - \gamma K_c\rangle_{q_\lambda}.$$

Updating $\lambda$ by gradient on free energy ([[SECREF:heterogeneous]]) is therefore a formal analog of precision learning [@friston-2014; @schwartenbeck-2015; @limanowski-2024]. We return to this in [[SECREF:heterogeneous.precision]].  Two consequences are worth flagging now.  First, $\lambda$ can be learned from the same free-energy objective the agent already minimizes — there is no auxiliary regularizer, no separate meta-learner in the model.  Second, under the model, coupling strength can vary with task context or learning history.  Any biological, arousal, fatigue, or developmental reading is hypothesis-level until an empirical protocol estimates $\lambda$ from joint-action data; tonic over-coupling and under-coupling are therefore framed as hypotheses about joint-statistical signatures, not as diagnostic claims ([[SECREF:phase]]).

## What J and K_c look like in practice

Five archetypal forms span the modeling range, each tuned to a different *kind* of cross-stream dependency.  The choice of $J$ is therefore the substantive modeling decision — once $J$ is fixed, the deformation in [[EQREF:tc_decomp]] is determined, and the framework's theorems hold for any bounded-norm choice.  The five archetypes:

- **Sparse pairwise.** $J(\pi) = \sum_{(i,j) \in \mathcal{C}} J_{ij}(\pi^i, \pi^j)$ with $\mathcal{C}$ a small set of edges. Recovers pairwise Markov-random-field structure and is the natural generalization of factor graphs; appropriate when only a few stream pairs (e.g. left/right-hand pairs in motor coordination) carry meaningful joint dependence.
- **Tensor-network low-rank.** $J(\pi) = \log[\text{MPS}(\pi^1,\ldots,\pi^K)]$ with bond dimension $r$. Recovers all the favorable algorithmic structure of matrix product states [@han-2018]; bond dimension is a complexity dial that interpolates between mean-field ($r = 1$) and arbitrary joint structure (full $r$).
- **Block-bidiagonal hierarchical.** $J$ couples only stream $k$ to $k+1$. This is the structural analog used by the hierarchical / deep AIF witness-form mapping ([[SECREF:connections.hierarchical]]): it captures cross-level coordination in the joint policy posterior, while temporal-scale separation and directed top-down / bottom-up message passing remain part of the source generative model.
- **Symbolic-task biased.** $J$ encodes a logical constraint ("if policy 1 is reach, then policy 2 is open hand") via large-magnitude penalties on violating configurations.  Appropriate when domain knowledge dictates discrete co-occurrences.
- **Learned tabular.** $J$ is a free parameter on $\Pi$ (size $\prod_k |\Pi^k|$) and is learned end-to-end. Computationally infeasible for large $K$ but conceptually clean and useful as the universal upper bound against which structured choices are benchmarked.

The framework is agnostic to the choice of $J, K_c$ — its theorems hold for any bounded-norm potentials. The art of the modeler is in choosing parsimonious, mechanistically interpretable forms.

---
