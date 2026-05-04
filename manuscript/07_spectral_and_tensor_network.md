# Spectral and Tensor-Network Structure

## Bipartite Schmidt decomposition

For $K = 2$, view $q_\lambda$ as a matrix $M \in \mathbb{R}^{|\Pi^1| \times |\Pi^2|}$ with $M_{ij} = q_\lambda(\pi^1 = i, \pi^2 = j)$. Singular value decomposition:

$$M = U \Sigma V^\top = \sum_\alpha s_\alpha\, u_\alpha v_\alpha^\top,$$

where $s_\alpha \geq 0$, $u_\alpha, v_\alpha$ orthonormal. Define:

- **Schmidt rank** $r(q_\lambda) = \#\{s_\alpha > 0\}$.
- **Policy entanglement entropy** $S_E(q_\lambda) = -\sum_\alpha p_\alpha \log p_\alpha$ where $p_\alpha = s_\alpha^2 / \sum_\beta s_\beta^2$.

**[[THMREF:prop_7_1]].** $r(q_\lambda) = 1 \iff q_\lambda \in \mathcal{M}_{\mathrm{MF}}$ (the joint distribution is a product). Equivalently, $S_E = 0 \iff$ mean-field.

The Lean companion (boundary statement, Mathlib-deferred):

[[LEAN:prop_7_1]]

**[[THMREF:prop_7_2]].** $r(q_\lambda)$ is upper-semicontinuous in $\lambda$. As $\lambda \uparrow \infty$, $r(q_\lambda)$ collapses toward the number of distinct *modes* of $J - \gamma K_c$. As $\lambda \downarrow 0$, $r(q_\lambda) = 1$.

The Lean companion (sketch placeholder; needs measure-theoretic
upper-semicontinuity machinery from Mathlib):

[[LEAN:prop_7_2]]

The discontinuous-rank prediction of [[THMREF:prop_7_1]] is empirically observed
as a step from $r = [[VAR:ising_schmidt_rank_at_lam_0]]$ at $\lambda = 0$
to $r = [[VAR:ising_schmidt_rank_at_lam_1]]$ for any $\lambda > 0$
in the K=2 Ising toy:

[[FIG:schmidt_rank]]

The smooth analogue, the *entanglement entropy* $S_E(q_\lambda)$, takes
the boundary values $S_E(0) = [[VAR:ising_S_E_at_lam_0:.4f]]$,
$S_E(1) = [[VAR:ising_S_E_at_lam_1:.4f]]$,
$S_E(3) = [[VAR:ising_S_E_at_lam_3:.4f]]$ and is shown across
$(\lambda, \mathrm{utility})$ as a heatmap below.

[[FIG:schmidt_entropy_surface]]

## The leading singular vectors as archetypal eigenvectors

This is the formal content of DAF's "archetypal eigenvector" framing.

**Definition (Archetypal modes).** The *archetypal joint policies* of an entangled ensemble are the leading singular vector pairs $\{(u_\alpha, v_\alpha) : s_\alpha \text{ large}\}$. Each mode $\alpha$ specifies a coupled pattern: a marginal $u_\alpha$ on $\pi^1$ and a co-occurring marginal $v_\alpha$ on $\pi^2$, with weight $s_\alpha$.

These are *not* policies the agent ever literally executes — they are eigenmodes of the joint posterior. But they are interpretable as the *behavioral templates* the coupling structure encodes. A drummer's "groove" is the leading $(u_\alpha, v_\alpha)$ pair on (left-hand-pattern, right-hand-pattern); a navigator's "circumnavigation" pattern is a leading mode on (locomotion, gaze).

This is structurally identical to bipartite quantum entanglement entropy [@eisert-2010] and to the spectral theory of probabilistic graphical models [@han-2018].

[[FIG:archetype_dendrogram]]

## Multi-stream tensor decomposition

For $K > 2$, $q_\lambda$ is a $K$-tensor of size $\prod_k |\Pi^k|$. Use:

- **CP (CANDECOMP/PARAFAC):** $q_\lambda \approx \sum_\alpha \lambda_\alpha\, u^1_\alpha \otimes u^2_\alpha \otimes \cdots \otimes u^K_\alpha$.
- **Tucker:** $q_\lambda \approx \mathcal{G} \times_1 U^1 \times_2 U^2 \cdots \times_K U^K$.
- **Tensor train (matrix product state, MPS):** $q_\lambda(\pi^1,\ldots,\pi^K) \approx \mathrm{Tr}\!\left[\prod_k A^k(\pi^k)\right]$ with bond dimension $r$.

Tensor-train is computationally favored: storage $O(K \cdot |\Pi_{\max}|^2 \cdot r^2)$ vs $\prod_k |\Pi^k|$ for the full joint, with rich expressive power for sparse/sequential coupling structure [@glasser-2019; @han-2018].

**Definition (Multi-stream entanglement entropy).** For tensor-train representation with bond dimensions $\{r_k\}$, the *bond entropies* $S_k = \log r_k$ measure the entanglement across each cut $\{1,\ldots,k\} \mid \{k+1,\ldots,K\}$. The full *entanglement spectrum* is $(r_1, \ldots, r_{K-1})$.

**[[THMREF:thm_7_3]] (Sparsity-rank tradeoff).** For coupling potential $J$ representable as a tensor-train with bond dimensions $\{r_k\}$, the resulting $q_\lambda$ has tensor-train rank at most $\{r_k\}$. Hence sparse hierarchical coupling structures (small $r_k$) yield computationally efficient posteriors, and the bond dimensions are precisely the rank of cross-cut entanglement.

The Lean companion (sketch placeholder; closure requires Mathlib's
matrix-product / tensor-network algebra):

[[LEAN:thm_7_3]]

This is the formal version of: *the deeper the coupling structure, the higher the cross-stream rank — but sparse couplings give low rank, hence efficient inference.* It directly mirrors the empirical success of MPS-based generative models [@han-2018] and Friston's renormalization-group treatment of FEP [@friston-2024], in which scale-invariant generative models have an inherent sparse-coupling structure that supports efficient hierarchical inference.

The bond-rank profile is computed numerically across stream counts
$K \in \{2, 3, 4, 5\}$ for the symmetric Ising K-stream coupling
(`src/simulation/builders.py::ising_coupling_tensor`):
$\mathrm{TT}_{K=2} = [[VAR:tt_ranks_K2]]$,
$\mathrm{TT}_{K=3} = [[VAR:tt_ranks_K3]]$,
$\mathrm{TT}_{K=4} = [[VAR:tt_ranks_K4]]$,
$\mathrm{TT}_{K=5} = [[VAR:tt_ranks_K5]]$.

[[FIG:tensor_train_rank_surface]]

## Birth and death of archetypes

As $\lambda$ varies continuously from $0$, the Schmidt rank can jump discontinuously upward (singular value crossings). These are the *symmetry-breaking transitions* of the entanglement structure — points at which a new behavioral archetype becomes available. We develop these as phase transitions in [[SECREF:phase]].

---
