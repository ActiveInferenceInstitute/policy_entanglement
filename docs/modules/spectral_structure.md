# Spectral and tensor-network structure

Manuscript section:
[`../manuscript/2G_spectral.md`](../../manuscript/2G_spectral.md).

## Bipartite (K = 2)

For a K = 2 joint policy posterior, write `q` as a
$|\Pi^1| \times |\Pi^2|$ matrix and compute its singular value
decomposition:

$$
q(\pi^1, \pi^2) \;=\; \sum_{\alpha=1}^{r} s_\alpha\, u_\alpha(\pi^1)\, v_\alpha(\pi^2).
$$

* **Schmidt rank** $r$: the number of non-zero singular values.
* **Archetypes**: each triple $(s_\alpha, u_\alpha, v_\alpha)$ is a
  cross-stream behavioral mode.
* **Entanglement entropy** of the bipartite cut:

  $$
  S_E(q) = -\sum_\alpha p_\alpha \log p_\alpha,\quad p_\alpha = \frac{s_\alpha^2}{\sum_\beta s_\beta^2}.
  $$

### Prop 7.1 — Bipartite mean-field factorization

A K = 2 joint is mean-field iff it factors as `u(π¹) · v(π²)`. This is
the boundary form of the Schmidt-rank-1 ⇔ mean-field characterization
(the full Schmidt-rank version requires Mathlib's
`Matrix.rank_one_outer_product`).

* Lean: `Bipartite.isBipartiteMeanField_iff_factors` (the primary
  boundary biconditional, `Iff.rfl`; this is the form imported by
  `SpectralWitnesses` when anchoring Schmidt-rank-1).  The split
  forwarders `Bipartite.isBipartiteMeanField_factors` (forward
  direction) and `Bipartite.factors_isBipartiteMeanField` (converse)
  are `.mp`/`.mpr` projections of the iff.
* Python: `schmidt_rank_one_iff_mean_field(q)` — tested for both
  outer-product and perfectly-correlated joints.

### Prop 8.1 — Schmidt-rank-1 ⇔ mean-field (boundary form)

The §8.1 block of [`Spectral.lean`](../../lean/ActinfPolicyEntanglement/Spectral.lean)
exposes the Schmidt-rank-1 predicate and proves it equivalent to
bipartite mean-field in stock Lean (the full matrix-SVD-based Schmidt
rank is supplied by the Mathlib extension):

* Lean: `Bipartite.HasSchmidtRankOne` — the rank-1 predicate, defined
  as the existence of an outer-product factorization `∃ u v, ∀ π1 π2,
  q π1 π2 = u π1 * v π2`.
* Lean: `Bipartite.schmidtRankOne_iff_isBipartiteMeanField` — the
  biconditional `HasSchmidtRankOne q ↔ IsBipartiteMeanField q`, proved
  by `Iff.rfl` (both predicates unfold to the same outer-product
  existence).
* Lean: `Bipartite.isBipartiteMeanField_imp_schmidtRankOne` —
  constructive corollary: any mean-field bipartite joint has Schmidt
  rank 1 (`.mpr` of the iff).
* Lean: `Bipartite.schmidtRankOne_imp_isBipartiteMeanField` —
  constructive corollary: any Schmidt-rank-1 bipartite joint is
  mean-field (`.mp` of the iff).  Together with the previous, this
  discharges the bipartite K=2 case of Prop 8.1 fully on the boundary
  fragment.

### Prop 8.2 — Upper-semicontinuity of rank in λ (round-3 witness)

Schmidt rank is an upper-semicontinuous function of λ — small
perturbations cannot grow the rank, only collapse it. Important for
*archetype stability*: small policy nudges preserve the dominant
modes.

* Lean: **witness form, round-3 graduation** — `SpectralWitnesses.schmidtRank_upperSemicontinuous_witness` packaged with the `UpperSemicontinuousRankWitness {rank_at_zero, usc}` structure. See [`spectral_witnesses.md`](spectral_witnesses.md) for the witness pattern; the Mathlib refinement still has to discharge the analytic payload (`Mathlib.Topology.Semicontinuous` + lower-semicontinuity of matrix rank).
* Python: numerical detector via `lean.spectral.schmidt_rank(q, atol=1e-9)`; the configured multi-K sweep in [`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py) exhibits the upper-semicontinuous behavior across `MULTI_K_VALUES`.

## Multi-stream (K > 2)

For K > 2 we use **tensor-train (matrix-product-state)** ranks:
bond dimensions across each cut $\{1..k\} | \{k+1..K\}$.

* `tensor_train_ranks(q)` returns a list of length `K-1`.
* The *entanglement spectrum* is the same list under a different
  name.

### Theorem 8.3 — Sparsity-rank tradeoff (round-3 witness)

A coupling potential expressible as a tensor train with bond
dimension $r$ produces a posterior whose tensor-train rank is bounded
by $r$.

* Lean: **witness form, round-3 graduation** — `SpectralWitnesses.sparsityRank_tradeoff_witness` packaged with the `SparsityRankEnvelope {cut_rank, bond_bound, envelope}` structure (per-cut bond-dimension envelope for K-stream tensor-train coupling). See [`spectral_witnesses.md`](spectral_witnesses.md). The Mathlib refinement payload requires `Mathlib.LinearAlgebra.TensorProduct` + matrix-rank bounds.
* Python: `tensor_train_ranks(q, atol=1e-9)` exercised by [`test_spectral.py`](../../tests/test_spectral.py) and the round-3 multi-K experiment in [`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py).

## Archetypes

The triple `(weight, u_α, v_α)` from the SVD of a K = 2 joint is the
*archetypal mode* referenced by the manuscript (and DAF in framing
notes). Practically:

```python
from lean.spectral import schmidt_decomposition
modes = schmidt_decomposition(q)        # descending weight
top  = modes[0]
print(top.weight, top.u, top.v)
```

The unit-norm `u_α` and `v_α` are *behavioral patterns* on each
stream; the weight `s_α` is the relative strength of that
cross-stream mode.

## Why this is more than aesthetics

* **Compression.**  Low Schmidt / TT rank means the joint policy is
  compressible to a few archetypes — important for memory budgets in
  embodied agents.
* **Interpretability.**  Each archetype is a coupled marginal pattern
  that can be inspected, named, and reasoned about.
* **Quantum-inspired analogs.**  Bipartite entanglement entropy in
  policy space has a direct mathematical homologue in many-body
  quantum systems [Han et al. 2018; Glasser et al. 2019].

## Where to look

* Lean: [`Spectral.lean`](../../lean/ActinfPolicyEntanglement/Spectral.lean) — Prop 7.1 (`isBipartiteMeanField_iff_factors` + forwarders) and the §8.1 Schmidt-rank-1 block (`HasSchmidtRankOne`, `schmidtRankOne_iff_isBipartiteMeanField`, and the two constructive corollaries).
* Lean (round-3): [`SpectralWitnesses.lean`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) — Prop 8.2 (upper-semicontinuity) + Thm 8.3 (sparsity-rank tradeoff), witness form; see the companion docs page [`spectral_witnesses.md`](spectral_witnesses.md).
* Python: [`spectral.py`](../../src/lean/spectral.py).
* Tests: [`test_spectral.py`](../../tests/test_spectral.py), [`test_multi_k_experiments.py`](../../tests/test_multi_k_experiments.py) (round-3 K>2 numerics), [`test_witness_theorems.py`](../../tests/test_witness_theorems.py).
* Figures: [`schmidt_rank.png`](../../output/figures/schmidt_rank.png), [`tensor_train_rank_surface.png`](../../output/figures/tensor_train_rank_surface.png), and the round-3 [`multi_k_tt_rank_profile.png`](../../output/figures/multi_k_tt_rank_profile.png).
