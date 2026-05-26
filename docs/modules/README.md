# `docs/modules/` — Per-concept deep dives

One Markdown file per major mathematical object — read the section of
the manuscript that introduces it, then come here for the unfolded
proof, numerical realization, and Lean status.

| File | Manuscript section | Lean module | Python module |
|---|---|---|---|
| [`basic.md`](basic.md) | §3 setup | [`Basic`](../../lean/ActinfPolicyEntanglement/Basic.lean) | (no separate mirror) |
| [`scalar_typeclass.md`](scalar_typeclass.md) | (Lean infrastructure) | [`Scalar`](../../lean/ActinfPolicyEntanglement/Scalar.lean) | (typeclass; not directly Python-mirrored) |
| [`joint_dist.md`](joint_dist.md) | §3 (setup, joint / mean-field PMFs) | [`JointDist`](../../lean/ActinfPolicyEntanglement/JointDist.lean) | [`lean/joint_dist`](../../src/lean/joint_dist.py) |
| [`coupling.md`](coupling.md) | §4 (λ-deformation) | [`Coupling`](../../lean/ActinfPolicyEntanglement/Coupling.lean) | [`lean/coupling`](../../src/lean/coupling.py) |
| [`decomposition_theorem.md`](decomposition_theorem.md) | §5 (decomposition theorem) | [`Decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | [`lean/decomposition`](../../src/lean/decomposition.py) |
| [`free_energy.md`](free_energy.md) | §5 / §7 (total-correlation primitives) | [`FreeEnergy`](../../lean/ActinfPolicyEntanglement/FreeEnergy.lean) | [`lean/free_energy`](../../src/lean/free_energy.py) |
| [`convexity.md`](convexity.md) | §5.4 / §11.3 (convexity and local-concavity witnesses) | [`Convexity`](../../lean/ActinfPolicyEntanglement/Convexity.lean) | (realized in [`lean/free_energy`](../../src/lean/free_energy.py) and [`lean/coupling`](../../src/lean/coupling.py)) |
| [`information_geometry.md`](information_geometry.md) | §7 (information geometry) | [`Geometry`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | [`lean/geometry`](../../src/lean/geometry.py) |
| [`markov_blanket.md`](markov_blanket.md) | §19.3 (Markov-blanket separation) | [`MarkovBlanket`](../../lean/ActinfPolicyEntanglement/MarkovBlanket.lean) | (realized in [`lean/free_energy`](../../src/lean/free_energy.py)) |
| [`spectral_structure.md`](spectral_structure.md) | §8 (spectral / TT structure; factorization forward/converse) | [`Spectral`](../../lean/ActinfPolicyEntanglement/Spectral.lean) | [`lean/spectral`](../../src/lean/spectral.py) |
| [`spectral_witnesses.md`](spectral_witnesses.md) | §8.1 / §8.3 (rank-continuity and sparsity-rank witness rows) | [`SpectralWitnesses`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) | (realized in [`lean/spectral`](../../src/lean/spectral.py); multi-K experiments in [`scripts/simulate_multi_k.py`](../../scripts/simulate_multi_k.py)) |
| [`connections_witnesses.md`](connections_witnesses.md) | §17 (hierarchical AIF and sophisticated-inference witness rows) | [`ConnectionsWitnesses`](../../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) | (realized in [`lean/decomposition`](../../src/lean/decomposition.py); long-horizon experiment in [`scripts/simulate_long_horizon.py`](../../scripts/simulate_long_horizon.py)) |
| [`heterogeneous_ensembles.md`](heterogeneous_ensembles.md) | §9 (coupling-tax witnesses) | [`Heterogeneous`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean) | [`lean/heterogeneous`](../../src/lean/heterogeneous.py) |
| [`bernoulli_toy.md`](bernoulli_toy.md) | §6 (examples), App. C | [`BernoulliToy`](../../lean/ActinfPolicyEntanglement/BernoulliToy.lean) | [`lean/bernoulli_toy`](../../src/lean/bernoulli_toy.py) |
| [`monotonicity.md`](monotonicity.md) | (constructive helper) | [`Monotonicity`](../../lean/ActinfPolicyEntanglement/Monotonicity.lean) | (no Python mirror) |
| [`constructive.md`](constructive.md) | §4 (λ-deformation) / §5 baseline (λ = 0) | [`Constructive`](../../lean/ActinfPolicyEntanglement/Constructive.lean) | (realized in [`lean/decomposition`](../../src/lean/decomposition.py)) |
| GNN fifth track (S08) | [`S08_gnn_generalized_notation_extension.md`](../../manuscript/S08_gnn_generalized_notation_extension.md) | (empirical; no Lean proof row) | [`src/gnn/AGENTS.md`](../../src/gnn/AGENTS.md) · [`reference/python_api_gnn.md`](../reference/python_api_gnn.md) |
