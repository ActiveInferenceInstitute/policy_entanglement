# Spectral Structure: Schmidt Rank, Archetypal Decomposition, and Tensor-Train Bond Profiles

## Bipartite Schmidt decomposition

For $K = 2$, view $q_\lambda$ as a matrix $M \in \mathbb{R}^{|\Pi^1| \times |\Pi^2|}$ with $M_{ij} = q_\lambda(\pi^1 = i, \pi^2 = j)$. Singular value decomposition:

$$M = U \Sigma V^\top = \sum_\alpha s_\alpha\, u_\alpha v_\alpha^\top,$$

where $s_\alpha \geq 0$, $u_\alpha, v_\alpha$ orthonormal. Define:

- **Schmidt rank** $r(q_\lambda) = \#\{s_\alpha > 0\}$.
- **Policy entanglement entropy** $S_E(q_\lambda) = -\sum_\alpha p_\alpha \log p_\alpha$ where $p_\alpha = s_\alpha^2 / \sum_\beta s_\beta^2$.

**[[THMREF:prop_7_1]].** $r(q_\lambda) = 1 \iff q_\lambda \in \mathcal{M}_{\mathrm{MF}}$ (the joint distribution is a product). Equivalently, $S_E = 0 \iff$ mean-field.

The Lean companion is a live boundary statement for the rank-one /
mean-field interface:

[[LEAN:prop_7_1]]

**[[THMREF:prop_7_2]] (witness-form).** $r(q_\lambda)$ is upper-semicontinuous in $\lambda$. As $\lambda \uparrow \infty$, $r(q_\lambda)$ collapses toward the number of distinct *modes* of $J - \gamma K_c$. As $\lambda \downarrow 0$, $r(q_\lambda) = 1$.

The Lean companion `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness`
is now live in the boundary fragment in *witness-consuming* form: the
caller supplies a Schmidt-rank curve `rankCurve : Float → Nat` together
with the mean-field anchor `rankCurve 0 = 1` and the universally
quantified upper-semicontinuity inequality as a structural witness,
and the boundary fragment certifies the resulting existence claim by
extracting the witness fields.  The Mathlib4 discharge target is the
semicontinuity / matrix-rank argument; the current claim is the typed
witness contract plus the numerical rank sweep.  The numerical realization lives
in [`src/lean/spectral.py`](../src/lean/spectral.py) and is exercised by
[`tests/test_witness_theorems.py`](../tests/test_witness_theorems.py):

[[LEAN:prop_7_2]]

The discontinuous-rank prediction of [[THMREF:prop_7_1]] is empirically observed
as a step from $r = [[VAR:ising_schmidt_rank_at_lam_0]]$ at $\lambda = 0$
to $r = [[VAR:ising_schmidt_rank_at_lam_1]]$ for any $\lambda > 0$
in the K=2 Ising toy.  **Caveat (non-trivial coupling required).** The
rank jump from $1$ to $2$ at $\lambda = 0^+$ requires that $J$ is
non-trivial across the cut $\{1\}\mid\{2\}$, i.e.\ $J$ cannot be
written as $f(\pi^1) + g(\pi^2)$ for any per-stream functions $f, g$.
In particular, if $J$ depends only on one stream — say $J(\pi) = f(\pi^1)$ —
the coupling is degenerate across this cut, $q_\lambda$ remains a
product across the cut for every $\lambda \geq 0$, and rank remains $1$. The Schmidt rank is computed by
[`src/lean/spectral.py::schmidt_decomposition`](../src/lean/spectral.py)
and gated against the analytical predictions in
[`tests/test_spectral.py`](../tests/test_spectral.py):

[[FIG:schmidt_rank]]

The smooth analog, the *entanglement entropy* $S_E(q_\lambda)$, takes
the boundary values $S_E(0) = [[VAR:ising_S_E_at_lam_0:.4f]]$,
$S_E(1) = [[VAR:ising_S_E_at_lam_1:.4f]]$,
$S_E(3) = [[VAR:ising_S_E_at_lam_3:.4f]]$ and is shown across
$(\lambda, \mathrm{utility})$ as a heatmap below.

[[FIG:schmidt_entropy_surface]]

## The leading singular vectors as archetypal eigenvectors

This is the formal content of the *archetypal eigenvector* reading of low-rank entangled posteriors.

**Definition (Archetypal modes).** The *archetypal joint policies* of an entangled ensemble are the leading singular vector pairs $\{(u_\alpha, v_\alpha) : s_\alpha \text{ large}\}$. Each mode $\alpha$ specifies a coupled pattern: a marginal $u_\alpha$ on $\pi^1$ and a co-occurring marginal $v_\alpha$ on $\pi^2$, with weight $s_\alpha$.

These are *not* policies the agent ever literally executes — they are eigenmodes of the joint posterior. But they are interpretable as the *behavioral templates* the coupling structure encodes. A drummer's "groove" is the leading $(u_\alpha, v_\alpha)$ pair on (left-hand-pattern, right-hand-pattern); a navigator's "circumnavigation" pattern is a leading mode on (locomotion, gaze).

This is structurally **analogous** to bipartite quantum entanglement entropy [@eisert-2010] and to the spectral theory of probabilistic graphical models [@han-2018]. In the quantum case the Schmidt coefficients $\{c_\alpha\}$ are amplitudes of a normalized state vector with $\sum_\alpha |c_\alpha|^2 = 1$; in the classical-probability case here the Schmidt coefficients are singular values $\{s_\alpha\}$ of the K=2 reshape of $q_\lambda$, *normalized by their sum-of-squares* to define the spectral distribution $p_\alpha = s_\alpha^2/\sum_\beta s_\beta^2$. The analogy is mapped in tensor-network tutorials and reviews [@eisert-2010; @orus-2014] and does not promote the policy joint to a quantum state — there is no superposition, no phase, no Hilbert space; the structural similarity is at the level of the SVD-derived entropy of a bipartite array.

[[FIG:archetype_dendrogram]]

## Multi-stream tensor decomposition

For $K > 2$, $q_\lambda$ is a $K$-tensor of size $\prod_k |\Pi^k|$. Use:

- **CP (CANDECOMP/PARAFAC):** $q_\lambda \approx \sum_\alpha \lambda_\alpha\, u^1_\alpha \otimes u^2_\alpha \otimes \cdots \otimes u^K_\alpha$.
- **Tucker:** $q_\lambda \approx \mathcal{G} \times_1 U^1 \times_2 U^2 \cdots \times_K U^K$.
- **Tensor train (matrix product state, MPS):** $q_\lambda(\pi^1,\ldots,\pi^K) \approx \mathrm{Tr}\!\left[\prod_k A^k(\pi^k)\right]$ with bond dimension $r$.

Tensor-train is computationally favored: storage $O(K \cdot |\Pi_{\max}|^2 \cdot r^2)$ vs $\prod_k |\Pi^k|$ for the full joint, with rich expressive power for sparse/sequential coupling structure [@orus-2014; @glasser-2019; @han-2018].

**Definition (Multi-stream entanglement entropy).** For tensor-train representation with bond dimensions $\{r_k\}$, the *maximum bond entropy* across each cut $\{1,\ldots,k\} \mid \{k+1,\ldots,K\}$ is $S_k^{\max} = \log r_k$. The *actual* bond entropy is $S_k(q_\lambda) = -\sum_\alpha p_\alpha^{(k)}\,\log p_\alpha^{(k)}$ where $\{p_\alpha^{(k)} = s_\alpha^{(k),2}/\sum_\beta s_\beta^{(k),2}\}$ is the spectral distribution of the bipartite reshape of $q_\lambda$ across the $k$-th cut; by Jensen, $S_k(q_\lambda) \leq \log r_k$ with equality iff the bond singular values are uniform. The full *entanglement spectrum* is the tuple $(r_1, \ldots, r_{K-1})$ together with the per-cut singular-value distributions.

**[[THMREF:thm_7_3]] (Sparsity-rank tradeoff).** If the coupling potential $J$ is representable as a tensor-train with bond dimensions $\{r_k\}$ and interaction order $d$ (the maximum order of any individual clique in the additive decomposition $J = \sum_e J_e$), then the resulting $q_\lambda$ has tensor-train rank at most $\{r_k^d\}$ on each cut (pairwise interactions give the $\{r_k^2\}$ saturation; see [[SECREF:app.tt_inference]] for the exact bound and the contraction $\exp(\lambda J) = \prod_e \exp(\lambda J_e)$ that produces it). Hence sparse hierarchical coupling structures (small $r_k$, small $d$) yield computationally efficient posteriors, and the bond dimensions $\{r_k^d\}$ are the rank of cross-cut entanglement.

The Lean companion `SpectralWitnesses.sparsityRank_tradeoff_witness`
is now live in the boundary fragment in *witness-consuming* form: the
caller supplies a per-cut Schmidt-rank function and an a-priori bond-
dimension envelope, together with the universally quantified rank-
bound envelope, as a `SparsityRankEnvelope K` witness; the boundary
fragment certifies that the entangled posterior respects the envelope
on every cut and every $\lambda$.  The Mathlib4 discharge target is the
tensor-product / matrix-rank proof of that envelope; the rendered Lean
block below is the current source that actually builds.

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

## Takeaways

> **1. Rank is the operational definition of "non-mean-field".**
> The joint posterior is mean-field iff its Schmidt rank is 1
> ([[THMREF:prop_7_1]]); any coupling that is non-trivial across the
> cut $\{1\}\mid\{2\}$ (i.e.\ not of the additive form $f(\pi^1) + g(\pi^2)$)
> jumps rank to $\ge 2$ at $\lambda > 0$.
> (The boundary Lean companion checks the definitional rank-one /
> mean-field unfolding; the full rank equivalence is the Mathlib-layer
> discharge target — `prop_7_1` is `status: proved`,
> `faithfulness: statement-restricted`.)
>
> **2. A few archetypes carry most of the behavioral mass.**
> Leading singular vectors of $q_\lambda$ are the dominant
> cross-stream behavioral modes — the few archetypes the agent's
> hyperprior repeatedly sculpts.
>
> **3. Low-rank couplings give low-rank posteriors.**
> The sparsity-rank tradeoff ([[THMREF:thm_7_3]]) bounds the bond
> dimensions of the posterior by those of the coupling — sparse
> hierarchical couplings yield computationally cheap inference.

---
