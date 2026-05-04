# Spectral and tensor-network structure

Manuscript section:
[`../manuscript/07_spectral_and_tensor_network.md`](../../manuscript/07_spectral_and_tensor_network.md).

## Bipartite (K = 2)

For a K = 2 joint policy posterior, write `q` as a
$|\Pi^1| \times |\Pi^2|$ matrix and compute its singular value
decomposition:

$$
q(\pi^1, \pi^2) \;=\; \sum_{\alpha=1}^{r} s_\alpha\, u_\alpha(\pi^1)\, v_\alpha(\pi^2).
$$

* **Schmidt rank** $r$: the number of non-zero singular values.
* **Archetypes**: each triple $(s_\alpha, u_\alpha, v_\alpha)$ is a
  cross-stream behavioural mode.
* **Entanglement entropy** of the bipartite cut:

  $$
  S_E(q) = -\sum_\alpha p_\alpha \log p_\alpha,\quad p_\alpha = \frac{s_\alpha^2}{\sum_\beta s_\beta^2}.
  $$

### Prop 7.1 — Schmidt rank 1 ⇔ mean-field

A K = 2 joint factorises iff its Schmidt rank is 1.  Direct corollary
of: a rank-1 matrix is the outer product of two vectors.

* Lean: `Bipartite.schmidtRank_one_iff_meanField` (boundary).
* Python: `schmidt_rank_one_iff_mean_field(q)` — tested for both
  outer-product and perfectly-correlated joints.

### Prop 7.2 — Upper-semicontinuity of rank in λ

Schmidt rank is an upper-semicontinuous function of λ — small
perturbations cannot grow the rank, only collapse it.  Important for
*archetype stability*: small policy nudges preserve the dominant
modes.

* Lean: `schmidtRank_upperSemicontinuous_sketch` (TODO).
* Python: deferred to Phase 7 (depends on numerical-rank robustness).

## Multi-stream (K > 2)

For K > 2 we use **tensor-train (matrix-product-state)** ranks:
bond dimensions across each cut $\{1..k\} | \{k+1..K\}$.

* `tensor_train_ranks(q)` returns a list of length `K-1`.
* The *entanglement spectrum* is the same list under a different
  name.

### Theorem 7.3 — Sparsity-rank tradeoff

A coupling potential expressible as a tensor train with bond
dimension $r$ produces a posterior whose tensor-train rank is bounded
by $r$.  Statement only at the Lean boundary; full proof goes via
matrix-product-operator algebra.

## Archetypes

The triple `(weight, u_α, v_α)` from the SVD of a K = 2 joint is the
*archetypal mode* referenced by the manuscript (and DAF in framing
notes).  Practically:

```python
from spectral import schmidt_decomposition
modes = schmidt_decomposition(q)        # descending weight
top  = modes[0]
print(top.weight, top.u, top.v)
```

The unit-norm `u_α` and `v_α` are *behavioural patterns* on each
stream; the weight `s_α` is the relative strength of that
cross-stream mode.

## Why this is more than aesthetics

* **Compression.**  Low Schmidt / TT rank means the joint policy is
  compressible to a few archetypes — important for memory budgets in
  embodied agents.
* **Interpretability.**  Each archetype is a coupled marginal pattern
  that can be inspected, named, and reasoned about.
* **Quantum-inspired analogues.**  Bipartite entanglement entropy in
  policy space has a direct mathematical homologue in many-body
  quantum systems [Han et al. 2018; Glasser et al. 2019].

## Where to look

* Lean: [`Spectral.lean`](../../lean/ActinfPolicyEntanglement/Spectral.lean).
* Python: [`spectral.py`](../../src/lean/spectral.py).
* Tests: [`test_spectral.py`](../../tests/test_spectral.py).
* Figure: [`../output/figures/schmidt_rank.png`](../../output/figures/schmidt_rank.png).
