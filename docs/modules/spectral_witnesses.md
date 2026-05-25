# Module: `SpectralWitnesses`

Boundary witness-form definitions and theorems for the two
spectral / tensor-network claims that were historically outside the
boundary fragment: **Proposition 8.2** (Schmidt rank upper-semicontinuous in
`λ`) and **Theorem 8.3** (sparsity-rank tradeoff for tensor-train
coupling).  Manuscript anchors:
[`../manuscript/2G_spectral.md`](../../manuscript/2G_spectral.md)
§8.1 (`spectral.bipartite` — Proposition 8.2) and §8.3
(`spectral.multistream_tt` — Theorem 8.3).

## Overview

`SpectralWitnesses` packages **two** spectral / tensor-network
analytic obligations as current `witness` status theorems:

* **Proposition 8.2** (`prop_7_2`, *Schmidt rank upper-semicontinuous
  in `λ`*) — the topological statement that the rank curve respects
  every ceiling on a tolerance window of any sample point.
* **Theorem 8.3** (`thm_7_3`, *Sparsity-rank tradeoff*) — the
  cut-by-cut bond-dimension envelope for `K`-stream tensor-train
  coupling potentials.

Both results are stated as **Mathlib-free, witness-consuming boundary
theorems**: the caller (a separate MathlibProofs layer importing
`Mathlib.Topology.Semicontinuous` and
`Mathlib.LinearAlgebra.TensorProduct`) supplies the analytic /
tensor-train evidence as a structural witness, and the boundary
fragment certifies the resulting existence claim by extracting the
witness fields.

The module is `Mathlib`-free, `sorry`-free, and `axiom`-free.  It
follows the *witness-structure idiom* introduced in
[`Heterogeneous.lean`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean)
(`BoundedQuadraticTax`, `SmallLambdaTolerance`) and reused in
[`Convexity.lean`](../../lean/ActinfPolicyEntanglement/Convexity.lean)
and
[`MarkovBlanket.lean`](../../lean/ActinfPolicyEntanglement/MarkovBlanket.lean).

## Definitions provided

| Lean name | Kind | Purpose |
|---|---|---|
| `UpperSemicontinuousRankWitness` | `structure` | Carries (i) the mean-field anchor `rankCurve 0 = 1` and (ii) the universally-quantified upper-semicontinuity inequality: every `λ₀` admits a tolerance window `δ > 0` on which `rankCurve` stays bounded by any ceiling `r₀` that the curve respects at `λ₀`.  Two fields. |
| `SparsityRankEnvelope` | `structure` | Carries (i) the per-cut Schmidt-rank curve `cut_rank : Fin K → Float → Nat`, (ii) the a priori per-cut bond bound `bond_bound : Fin K → Nat`, and (iii) the universally-quantified envelope `cut_rank k λ ≤ bond_bound k` for every cut and every `λ`.  Three fields. |
| `schmidtRank_upperSemicontinuous_witness` | `theorem` | Boundary witness form of Proposition 8.2. |
| `sparsityRank_tradeoff_witness` | `theorem` | Boundary witness form of Theorem 8.3. |
| `sparsityRank_meanField_at_zero` | `theorem` (corollary) | Mean-field corollary at `λ = 0`: every cut rank collapses to `1` provided the caller's envelope respects the rank-`1` anchor.  Discharged via `rw + Nat.le_refl 1`. |

## Key theorems

### `schmidtRank_upperSemicontinuous_witness` (Proposition 8.2 — `prop_7_2`)

```lean
theorem schmidtRank_upperSemicontinuous_witness
    (rankCurve : Float → Nat)
    (witness : UpperSemicontinuousRankWitness rankCurve) :
    rankCurve 0.0 = 1
      ∧ ∀ (lam0 : Float) (r0 : Nat),
          rankCurve lam0 ≤ r0 →
          ∃ delta : Float, 0.0 < delta ∧
            ∀ lam : Float, (lam - lam0).abs < delta → rankCurve lam ≤ r0 :=
  ⟨witness.rank_at_zero, witness.usc⟩
```

The conjunction packages (i) the mean-field anchor (Schmidt rank
collapses to `1` at `λ = 0`) and (ii) the upper-semicontinuity
inequality.  The proof is a single anonymous constructor — exactly
the witness-form pattern.

### `sparsityRank_tradeoff_witness` (Theorem 8.3 — `thm_7_3`)

```lean
theorem sparsityRank_tradeoff_witness (K : Nat)
    (witness : SparsityRankEnvelope K) :
    ∀ (k : Fin K) (lam : Float),
      witness.cut_rank k lam ≤ witness.bond_bound k :=
  witness.envelope
```

The theorem says: every per-cut Schmidt rank respects the bond-bound
envelope at every `λ`.  The proof extracts the witness's `envelope`
field directly — one line, witness-form pattern.

### `sparsityRank_meanField_at_zero` (corollary)

```lean
theorem sparsityRank_meanField_at_zero (K : Nat)
    (witness : SparsityRankEnvelope K)
    (hAnchor : ∀ k : Fin K, witness.cut_rank k 0.0 = 1) :
    ∀ k : Fin K, witness.cut_rank k 0.0 ≤ 1 := by
  intro k
  rw [hAnchor k]
  exact Nat.le_refl 1
```

At `λ = 0` every cut rank collapses to `1` — the multi-cut analog
of `rank_at_zero` for `UpperSemicontinuousRankWitness`.  Discharged
constructively without analytic content.

## Wiring

| Track | Resolves to |
|---|---|
| Manuscript section (Prop 8.2) | [`§8.1 Bipartite Schmidt decomposition`](../../manuscript/2G_spectral.md) (`spectral.bipartite`). |
| Manuscript section (Thm 8.3) | [`§8.3 Multi-stream tensor decomposition`](../../manuscript/2G_spectral.md) (`spectral.multistream_tt`). |
| Lean module | [`SpectralWitnesses.lean`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) (2 structures, 3 theorems, zero `sorry`, zero `axiom`). |
| Registry labels | `prop_7_2` (Prop 8.2) and `thm_7_3` (Thm 8.3) in [`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml); both are current `status: witness` rows. |
| Python sanity rail | [`src/lean/spectral`](../../src/lean/spectral.py) — `schmidt_rank(q, atol=1e-9)` and `tensor_train_ranks(q, atol=1e-9)` produce the numerical witnesses on K-stream Ising joints. |
| Multi-K experiments | [`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py) sweeps the K-stream Ising ensemble at $K \in \{3, 4\}$ and writes `output/data/multi_k_summary.json` plus three figures (`multi_k_total_correlation`, `multi_k_aligned_mass`, `multi_k_tt_rank_profile`) that empirically envelope the boundary witnesses on the multi-stream sparsity grid. |
| Tests | [`tests/test_spectral.py`](../../tests/test_spectral.py) and [`tests/test_witness_theorems.py`](../../tests/test_witness_theorems.py) — the latter exercises both witnesses against floating tolerance on the canonical Ising ensemble. |

## Examples / use-cases (witness construction)

A Mathlib-side caller that wishes to certify Proposition 8.2 on a
concrete rank curve constructs a `UpperSemicontinuousRankWitness` by
supplying the analytic content as explicit proof terms:

```lean
def myUSCWitness
    (rankAtZero : mySchmidtRankCurve 0.0 = 1)
    (uscProof :
      ∀ (lam0 : Float) (r0 : Nat),
        mySchmidtRankCurve lam0 ≤ r0 →
        ∃ delta : Float, 0.0 < delta ∧
          ∀ lam : Float,
            (lam - lam0).abs < delta → mySchmidtRankCurve lam ≤ r0) :
    UpperSemicontinuousRankWitness mySchmidtRankCurve where
  rank_at_zero := rankAtZero
  usc := uscProof
```

and then invokes

```lean
example : ... := schmidtRank_upperSemicontinuous_witness
                   mySchmidtRankCurve
                   (myUSCWitness rankAtZero uscProof)
```

to discharge the existence claim.  Analogously, a `SparsityRankEnvelope`
witness for a K-stream tensor-train coupling supplies the per-cut
ranks and bonds:

```lean
def myEnvelope (K : Nat)
    (cutRank : Fin K → Float → Nat)
    (bonds : Fin K → Nat)
    (rankEnvelope :
      ∀ (k : Fin K) (lam : Float), cutRank k lam ≤ bonds k) :
    SparsityRankEnvelope K where
  cut_rank   := cutRank
  bond_bound := bonds
  envelope   := rankEnvelope
```

On the **numerical** side, the parameter sweep at $K = 2$
(`schmidt_rank` on `lean.coupling.entangled_posterior`) plus the
multi-K sweep at $K \in \{3, 4\}$
([`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py))
exhibit both witnesses on the empirical Ising ensemble across the
canonical sweep grid (`PARAMETER_SWEEP_LAMBDAS` and
`MULTI_K_SWEEP_LAMBDAS`).  The companion figures
[`multi_k_tt_rank_profile`](../../output/figures/multi_k_tt_rank_profile.png)
and [`tensor_train_rank_surface`](../../output/figures/tensor_train_rank_surface.png)
plot the bond-rank envelope at $K \in \{2, 3, 4, 5\}$.

## Cross-references

* [`spectral_structure.md`](spectral_structure.md) — the boundary
  fragment that provides `Bipartite.IsBipartiteMeanField` and the
  forward / converse Schmidt-rank-1 factorization lemmas (Prop 8.1).
* [`free_energy.md`](free_energy.md) — `totalCorrelation` is the
  scalar quantity whose growth (Fig.
  [`multi_k_total_correlation`](../../output/figures/multi_k_total_correlation.png))
  is the empirical envelope of the multi-stream rank growth.
* [`connections_witnesses.md`](connections_witnesses.md) — the
  companion round-3 module covering Theorem 17.1 + Proposition 17.2
  (the §17 witness graduations).
* [`convexity.md`](convexity.md) — round-2 witness module
  (`Convexity.lean`); the same witness-structure idiom is reused
  here.
* [`heterogeneous_ensembles.md`](heterogeneous_ensembles.md) — the
  original witness-structure idiom (`BoundedQuadraticTax`,
  `SmallLambdaTolerance`).
* [`../reference/lean_reference.md`](../reference/lean_reference.md) —
  per-theorem status table.  Round 3 added the
  `SpectralWitnesses.lean` rows.
* [`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md) — the
  Mathlib payload-discharge roadmap; `schmidtRank_upperSemicontinuous_witness`
  and `sparsityRank_tradeoff_witness` are the two new entries in
  that roadmap.
