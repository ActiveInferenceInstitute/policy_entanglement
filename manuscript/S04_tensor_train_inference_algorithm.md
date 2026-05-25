# Tensor-Train Inference Algorithm: Bond-Dimension Sweep, MPS Contraction, and Sparsity-Rank Tradeoff

For coupling potentials representable as tensor trains (TT) with low
bond rank $r$, the λ-entangled posterior admits efficient inference and
sampling via standard matrix-product-state (MPS) machinery
[@orus-2014; @schollwock-2011]. Throughout
this appendix, $r$ denotes the maximal bond dimension of the TT
contraction; $r$ is the parameter that controls the time / memory
trade-off and corresponds to the Schmidt rank of the bipartite reshape
of $q_\lambda$ across any cut along the train.  Companion code:
[`src/lean/spectral.py`](../src/lean/spectral.py) exposes the rank and
entropy diagnostics used in the current figures; the dense empirical
suite computes the small-$K$ witnesses directly, while the full TT
contraction algorithm below is an engineering extension of that current
rank evidence.

## Tensor-train representation of J

Suppose $J(\pi) = J(\pi^1, \dots, \pi^K)$ admits a TT representation
with bond dimension $r$:

$$
J(\pi^1,\dots,\pi^K) \;=\; \sum_{a_0,\dots,a_K} A^{(1)}_{a_0,\pi^1,a_1}\,A^{(2)}_{a_1,\pi^2,a_2}\cdots A^{(K)}_{a_{K-1},\pi^K,a_K},
$$

with boundary indices $a_0 = a_K = 1$.  Each tensor $A^{(k)}$ has
shape $(r,|\Pi^k|,r)$ except at the boundaries.

## The exponential map

The pointwise exponential of a TT is *not* itself low-rank in
general, but for *additive-form* couplings $J = \sum_e J_e$ over a
local interaction graph $e \in \mathcal{E}$ (the practically
relevant case — pairwise / triplet couplings between adjacent
streams), the factorization

$$
\exp(\lambda J) \;=\; \prod_{e\in\mathcal{E}} \exp(\lambda J_e)
$$

is a product of bond-dimension-bounded operators that contracts
into a TT of bond dimension $r' = O(r^d)$ where $d$ is the maximum
order of an interaction.  For pairwise couplings, $r' = O(r^2)$.

## Inference cost

Per-pass cost of computing $q_\lambda$, its marginals, and its
log-partition is

$$
\mathcal{O}\!\big(K \cdot |\Pi_{\max}|^2 \cdot r'^2\big),
$$

where $|\Pi_{\max}| = \max_k |\Pi^k|$.  Compared to dense inference
(which is $\mathcal{O}\!\big(\prod_k |\Pi^k|\big)$), this is
exponentially cheaper whenever $r' \ll \prod_k |\Pi^k|^{1/2}$.

## Sampling

Standard MPS conditional sampling [@orus-2014; @han-2018]: draw $\pi^1$
from its marginal, condition the remaining streams, draw $\pi^2$, and
so on.  Each conditional draw is an $\mathcal{O}(|\Pi_{\max}|\,r'^2)$
operation; total $\mathcal{O}(K\,|\Pi_{\max}|\,r'^2)$ per sample.

## Marginal extraction

Marginals $q_\lambda^k$ are extracted by tracing out all other
streams from the TT, an $\mathcal{O}(K\,|\Pi_{\max}|\,r'^2)$ operation.
The Python companion implements this end-to-end for the dense (small
$K$) case in `src/lean/joint_dist.py`; a sparse TT contraction version
would extend the same interface rather than change the theorem statement.

## Bond-dimension recursion

The bond dimensions of the contracted TT for $q_\lambda$ obey a
*compositional recursion* over the interaction graph.  Order the
streams $1, 2, \dots, K$ along the train and define the *partial
bond rank* $r_k(\lambda)$ as the Schmidt rank of the bipartite
factorization $\{1,\ldots,k\} \mid \{k+1,\ldots,K\}$ of $q_\lambda$.
Then:

* **Lower bound (rank-additivity at the boundary).**  $r_k(0) = 1$
  for every $k$ (mean-field has rank one across every cut).
* **Upper bound (sparsity ⟹ low rank).**  If $J$ has TT rank
  $\leq r$ across the cut at $k$, then $r_k(\lambda) \leq r^2$ for
  every $\lambda$ — pairwise interactions saturate at this bound; a
  $d$-clique of streams pushes it to $r_k \leq r^d$.
* **Monotone growth.**  $r_k(\lambda)$ is non-decreasing in $\lambda$
  on every cut where $J$ is non-trivial — the symmetry-breaking
  transitions of [[SECREF:spectral.births]] are the discrete jumps in
  $r_k(\lambda)$.

The recursion is exploited algorithmically in the *DMRG-style sweep*:
fix all bonds except one, solve a local generalized-eigenvalue
problem to update that bond, advance.  Each sweep is
$\mathcal{O}(K\,|\Pi_{\max}|^2\,r_{\max}^3)$; convergence in
$\mathcal{O}(\log(1/\varepsilon))$ sweeps for KL accuracy
$\varepsilon$ is standard for log-concave coupling potentials
[@verstraete-2008; @orus-2014; @han-2018].  The numerical companion records the
empirical $r_k$ profile across stream counts $K \in \{2,3,4,5\}$ —
see the `tt_ranks_K2`–`tt_ranks_K5` variables in
[`output/data/manuscript_variables.json`](../output/data/manuscript_variables.json),
exposed in prose at [[SECREF:spectral.multistream_tt]].

## Approximate compression

When the exact TT rank of $\exp(\lambda J)$ exceeds a budget $r_{\max}$,
truncated SVD across each bond gives a rank-$r_{\max}$ approximation
with controlled KL error.  This is the standard
*matrix-product-operator* / *MPO-MPS* contraction trick.

## Connection to the sparsity–rank tradeoff

[[THMREF:thm_7_3]] (sparsity-rank tradeoff): a TT coupling potential of
bond dim $r$ produces a posterior with TT rank bounded by $r'$ as
above.  This is the formal counterpart of the practical observation
that *low-rank couplings give cheap posteriors*.
