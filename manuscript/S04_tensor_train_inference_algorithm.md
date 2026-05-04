# Tensor-Train Inference Algorithm Sketch

For coupling potentials representable as tensor trains, the
λ-entangled posterior admits efficient inference and sampling via
standard matrix-product-state (MPS) machinery.  Companion code:
[`src/lean/spectral.py`](../src/lean/spectral.py) (currently exposes the
*ranks* of a posterior; the inference algorithm itself is a Phase 7 /
Empirical-suite item — see [[SECREF:empirical]]).

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
streams), the factorisation

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

Standard MPS conditional sampling [@han-2018]: draw $\pi^1$
from its marginal, condition the remaining streams, draw $\pi^2$, and
so on.  Each conditional draw is an $\mathcal{O}(|\Pi_{\max}|\,r'^2)$
operation; total $\mathcal{O}(K\,|\Pi_{\max}|\,r'^2)$ per sample.

## Marginal extraction

Marginals $q_\lambda^k$ are extracted by tracing out all other
streams from the TT, an $\mathcal{O}(K\,|\Pi_{\max}|\,r'^2)$ operation.
The Python companion implements this end-to-end for the dense (small
$K$) case in `src/lean/joint_dist.py`; the TT version is a planned
extension under [[SECREF:empirical]] of the manuscript.

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

