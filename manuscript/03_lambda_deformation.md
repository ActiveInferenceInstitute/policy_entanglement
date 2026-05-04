# The lambda-Deformation: Coupling Mean-Field Toward Joint Structure

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
- $\lambda \to \infty$: $q_\lambda$ collapses onto the modes of $J - \gamma K_c$ — *pure archetypal joint policies*.
- Intermediate $\lambda$: the regime of practical interest.

For analytical separation of habit vs. preference coupling, one can carry two parameters $\lambda_E, \lambda_G$ with coupling potentials $J, K_c$ respectively. We use a single $\lambda$ in the body of the paper for clarity, with the two-parameter generalization appearing in [[SECREF:comparative]] for comparative statics.

## The coupling parameter lambda as a precision

A central conceptual point: $\lambda$ is *not* an arbitrary engineering knob. It is formally a **precision parameter** on the coupling structure, dual (in the Legendre sense) to the sufficient statistics $\langle J \rangle$ and $\langle K_c \rangle$ under the joint posterior. This is the same role $\gamma$ plays for EFE in the standard single-stream model. Concretely:

$$\frac{\partial \log Z(\lambda)}{\partial \lambda} = \langle J - \gamma K_c\rangle_{q_\lambda}.$$

Updating $\lambda$ by gradient on free energy ([[SECREF:heterogeneous]]) is therefore a natural higher-order generalization of dopaminergic precision learning [@friston-2014; @schwartenbeck-2015]. We return to this in [[SECREF:heterogeneous.precision]].

## What J and K_c look like in practice

Examples that illustrate the range:

- **Sparse pairwise.** $J(\pi) = \sum_{(i,j) \in \mathcal{C}} J_{ij}(\pi^i, \pi^j)$ with $\mathcal{C}$ a small set of edges. Recovers pairwise Markov-random-field structure and is the natural generalization of factor graphs.
- **Tensor-network low-rank.** $J(\pi) = \log[\text{MPS}(\pi^1,\ldots,\pi^K)]$ with bond dimension $r$. Recovers all the favorable algorithmic structure of matrix product states [@han-2018]; bond dimension is a complexity dial.
- **Block-bidiagonal hierarchical.** $J$ couples only stream $k$ to $k+1$. Recovers hierarchical AIF / deep temporal AIF as a sparse limit ([[SECREF:connections.hierarchical]]).
- **Symbolic-task biased.** $J$ encodes a logical constraint ("if $\pi^1 = $ reach, then $\pi^2 = $ open hand") via large-magnitude penalties on violating configurations.
- **Learned tabular.** $J$ is a free parameter on $\Pi$ (size $\prod_k |\Pi^k|$) and is learned end-to-end. Computationally infeasible for large $K$ but conceptually clean.

The framework is agnostic to the choice of $J, K_c$ — its theorems hold for any bounded-norm potentials. The art of the modeler is in choosing parsimonious, biologically interpretable forms.

---
