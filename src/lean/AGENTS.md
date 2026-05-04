# AGENTS.md — `src/lean/`

Python mirrors of the Lean 4 boundary-fragment modules under
[`lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/).

## Cross-track invariants

| Concept | Lean module | Python module |
|---|---|---|
| Joint / mean-field PMFs, marginalisation | `JointDist` | `joint_dist.py` |
| Coupling potentials, λ-entangled prior / posterior | `Coupling` | `coupling.py` |
| Free energies, entropies, total correlation | `FreeEnergy` | `free_energy.py` |
| e/m-flatness, m-projection, Pythagorean | `Geometry` | `geometry.py` |
| Schmidt rank, archetypes, TT ranks | `Spectral` | `spectral.py` |
| Heterogeneous VFE/EFE, coupling tax (Thm 8.1) | `Heterogeneous` | `heterogeneous.py` |
| K=2 Bernoulli toy | `BernoulliToy` | `bernoulli_toy.py` |
| Theorem 4.1 entanglement decomposition | `Decomposition` | `decomposition.py` |

When you add a concept on one side, mirror it on the other.

## Rules

* No mocks; use real numpy arrays.
* `from joint_dist import …` continues to work because `src/lean/` is on
  `sys.path` (see `pyproject.toml` and `conftest.py`).
* Public APIs require type hints.
* Never depend on `pymdp` or `seaborn` here — those belong to
  `src/simulation/` and `src/visualizations/` respectively.
