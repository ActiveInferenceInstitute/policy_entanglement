# AGENTS.md — `actinf_policy_entanglement_lean`

## Identity & Scope

This project provides a Lean 4 formalization of Policy Entanglement in Active Inference, compatible with Mathlib v4.29.0+. The formalization is structured in phases:

- **Phase 1**: Basic definitions (policy factors, joint distributions) - COMPLETE
- **Phase 2**: Joint and mean-field distributions - COMPLETE
- **Phase 3**: Coupling potentials - COMPLETE
- **Phase 4**: Free energy, KL divergence, entropy - RESTORED with `sorry`
- **Phase 5**: Geometry and exponential families - RESTORED with `sorry`
- **Phase 6**: Spectral properties and heterogeneous inference - RESTORED with `sorry`
- **Phase 7**: Full Mathlib integration - IN PROGRESS

The Lean files were recently restored with `sorry` markers for the unproven theorems. The immediate goal is to prove the foundational theorems in Phase 7.1.

## Repository Constitution (rules you must follow)

1. **Mathlib-free at the Lean boundary.** Do not add `import Mathlib...` to any module under `lean/ActinfPolicyEntanglement/` or `lean/FepSketches/`. The package builds on stock Lean 4 v4.29.0; Mathlib refinement is a Phase 7 task tracked in `lean/ActinfPolicyEntanglement/Phase7Roadmap.md`.
2. **Reserved tokens.** `Π` and `λ` are Lean 4 binder tokens; never use them as ordinary identifiers — use `Pol`, `q_lam`, `lam` etc.
3. **No mocks in tests.** Use real `numpy` arrays; if you need randomness, use `np.random.default_rng(seed=…)` with a fixed seed.
4. **Coverage floor: 90%.** CI runs `pytest tests/ --cov=src --cov-fail-under=90`; today the suite is at 98.37%. Do not regress.
5. **Thin orchestrators only in `scripts/`.** Every numerical computation must come from `src/`; `scripts/` handles I/O, matplotlib, and stdout-path emission.
6. **Print output paths to stdout** in scripts, one per line, so the pipeline manifest can collect them.
7. **Headless matplotlib.** Always set `MPLBACKEND=Agg` before importing `matplotlib.pyplot`; the scripts already do this.
8. **Determinism.** All scripts must run reproducibly (fixed seeds, no time-dependent state).
9. **Disposable `output/`.** Treat the entire `output/` tree as regenerable; never hand-edit it, never commit transient outputs.

## How Agents Should Work

| Want to … | Edit | Then run |
|---|---|---|  
| add a Lean theorem | a file under `lean/ActinfPolicyEntanglement/` | `cd lean && lake build` |
| add an analytical helper | a file under `src/lean/` | `pytest tests/` |
| add a pymdp harness piece | a file under `src/simulation/` | `pytest tests/test_simulation_*.py` |
| add a plotting helper | a file under `src/visualizations/` | `pytest tests/test_visualizations.py` |
| add a test | a file under `tests/` | `pytest tests/<file>` |
| add a figure | `scripts/generate_figures.py` or `scripts/simulate_pymdp.py` | `python scripts/<script>.py` |
| change manuscript prose | a file under `manuscript/` | (PDF rendering is pipeline-level) |
| add architecture / math docs | a file under `docs/` | (none) |

## Cross-track invariants

The Lean and Python tracks are deliberately structured to mirror each other. When you add a concept on one side, prefer to mirror it on the other so the two stay in sync.

| Concept | Lean module | Python module |
|---|---|---|  
| Joint / mean-field PMFs, marginalisation | [`ActinfPolicyEntanglement.JointDist`](lean/ActinfPolicyEntanglement/JointDist.lean) | [`src/lean/joint_dist.py`](src/lean/joint_dist.py) |
| Coupling potentials, λ-entangled prior / posterior | [`Coupling`](lean/ActinfPolicyEntanglement/Coupling.lean) | [`src/lean/coupling.py`](src/lean/coupling.py) |
| Free energies, entropies, total correlation | [`FreeEnergy`](lean/ActinfPolicyEntanglement/FreeEnergy.lean) | [`src/lean/free_energy.py`](src/lean/free_energy.py) |
| e/m-flatness, m-projection, Pythagorean | [`Geometry`](lean/ActinfPolicyEntanglement/Geometry.lean) | [`src/lean/geometry.py`](src/lean/geometry.py) |
| Schmidt rank, archetypes, TT ranks | [`Spectral`](lean/ActinfPolicyEntanglement/Spectral.lean) | [`src/lean/spectral.py`](src/lean/spectral.py) |
| Heterogeneous VFE/EFE, coupling tax (Thm 8.1) | [`Heterogeneous`](lean/ActinfPolicyEntanglement/Heterogeneous.lean) | [`src/lean/heterogeneous.py`](src/lean/heterogeneous.py) |
| K=2 Bernoulli toy | [`BernoulliToy`](lean/ActinfPolicyEntanglement/BernoulliToy.lean) | [`src/lean/bernoulli_toy.py`](src/lean/bernoulli_toy.py) |
| Theorem 4.1 entanglement decomposition | [`Decomposition`](lean/ActinfPolicyEntanglement/Decomposition.lean) | [`src/lean/decomposition.py`](src/lean/decomposition.py) |

## Validation checklist (before commit)

```bash
cd lean && lake build                           # 16/16 green with sorry
cd ..   && uv sync --group sim --group viz       # full env
uv run pytest tests/ --cov=src --cov-fail-under=90  # 340+ passing, ≥90%
uv run python scripts/generate_figures.py       # 21 PNGs in output/figures/
uv run python scripts/simulate_pymdp.py         # pymdp harness artefacts
uv run python scripts/manuscript_variables.py   # JSON in output/data/
uv run python scripts/run_all.py                # full chain + validator
```

## Known limitations / TODO

* A small number of theorems in `lean/ActinfPolicyEntanglement/` carry boundary-form `sorry` placeholders. These are deliberate — the analytic content (KL non-negativity, log identities, SVD rank, Bregman geometry) is scheduled for Phase 7 once Mathlib is wired in. Per-theorem status: [`docs/reference/lean_reference.md`](docs/reference/lean_reference.md); Phase 7 plan: [`docs/reference/phase7_plan.md`](docs/reference/phase7_plan.md).
* The canonical manuscript is the modular set under `manuscript/`; `scripts/generate_figures.py` and `scripts/manuscript_variables.py` feed it numerical content from `src/` via `output/`.
* `docs/` is the technical reference — improvements / clarifications welcome.