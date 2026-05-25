# AGENTS.md — `src/lean/`

Python mirrors of the Lean 4 boundary-fragment modules under
[`lean/ActinfPolicyEntanglement/`](../../lean/ActinfPolicyEntanglement/).

## Cross-track invariants

| Concept | Lean module | Python module |
|---|---|---|
| Joint / mean-field PMFs, marginalization | `JointDist` | `joint_dist.py` |
| Coupling potentials, λ-entangled prior / posterior | `Coupling` | `coupling.py` |
| Free energies, entropies, total correlation | `FreeEnergy` | `free_energy.py` |
| e/m-flatness, m-projection, Pythagorean | `Geometry` | `geometry.py` |
| Schmidt rank, archetypes, TT ranks | `Spectral` | `spectral.py` |
| Heterogeneous VFE/EFE, coupling tax (Thm 9.1) | `Heterogeneous` | `heterogeneous.py` |
| K=2 Bernoulli toy | `BernoulliToy` | `bernoulli_toy.py` |
| Theorem 5.1 entanglement decomposition | `Decomposition` | `decomposition.py` |
| (numerical-witness layer for dashboard / plaintext report) | — | `invariants.py` |
| (Lean build gate — library for `scripts/build_lean.py`) | — | `build_gate.py` |

When you add a concept on one side, mirror it on the other.

`invariants.py` is the only module in this subpackage with no Lean
mirror.  It composes the analytical helpers above into
`reporting.interactive_dashboard.Invariant` records — pass / fail
badges with concrete witnesses — that the dashboard and
`output/reports/dashboard_invariants.txt` consume.  The reporting
module is project-local, so the invariants import in this standalone
checkout without the parent template tree.

## Rules

* No mocks; use real numpy arrays.
* External callers (tests, scripts) import via the namespaced
  subpackage path: `from lean.joint_dist import …`,
  `from lean.coupling import …`, etc.
* Intra-subpackage imports use the relative form
  (`from .joint_dist import …` inside `src/lean/coupling.py`).
* Public APIs require type hints.
* Never depend on `pymdp` or `seaborn` here — those belong to
  `src/simulation/` and `src/visualizations/` respectively.
