# AGENTS.md — `ActinfPolicyEntanglement/`

## Identity & Scope

This package provides the Lean 4 formalization of Policy Entanglement in Active Inference. It is structured in phases:

- **Phase 1**: Basic definitions (policy factors, joint distributions) - COMPLETE
- **Phase 2**: Joint and mean-field distributions - COMPLETE
- **Phase 3**: Coupling potentials - COMPLETE
- **Phase 4**: Free energy, KL divergence, entropy - RESTORED with `sorry`
- **Phase 5**: Geometry and exponential families - RESTORED with `sorry`
- **Phase 6**: Spectral properties and heterogeneous inference - RESTORED with `sorry`
- **Phase 7**: Full Mathlib integration - IN PROGRESS

The files were recently restored with `sorry` markers for the unproven theorems. The immediate goal is to prove the foundational theorems in Phase 7.1.

### Key Changes from Phase 6

1. **Mathlib Integration**: Imports from Mathlib provide the infrastructure for analytic content.
2. **Real Numbers**: `Float` replaced with `Real` (ℝ) throughout.
3. **Sorry Markers**: `sorry` markers present pending formal proofs.
4. **Updated Validation**: The build now requires Mathlib; `lake build` should succeed with `sorry` markers.

### Repository Constitution

1. **Mathlib at the Boundary**: This module now imports from Mathlib for analytic content. The package builds on Mathlib v4.29.0+ (via Lake).
2. **Reserved Tokens**: `Π` and `λ` remain reserved binder tokens; use `Pol`, `q_lam`, `lam` as substitutes.
3. **Coverage Floor**: 90% minimum coverage on `src/` still applies.
4. **Thin Orchestrators**: Scripts remain thin coordinators; business logic in `src/`.

### Validation Checklist

```bash
cd lean && lake build                           # Compiles with sorry
cd ..   && uv sync --group sim --group viz       # full env
uv run pytest tests/ --cov=src --cov-fail-under=90  # 340+ passing, ≥90%
uv run python scripts/generate_figures.py       # 21 PNGs in output/figures/
uv run python scripts/simulate_pymdp.py         # pymdp harness artefacts
uv run python scripts/manuscript_variables.py   # JSON in output/data/
uv run python scripts/run_all.py                # full chain + validator
```

### Known Limitations

* The Lean formalization depends on Mathlib for analytic content.
* Many proofs contain `sorry` markers pending formal verification.
* The Python companion remains the numerical oracle for testing.

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

## Cross-Track Invariants

The Lean and Python tracks remain mirrored. When you add a concept on one side, prefer to mirror it on the other so the two stay in sync.

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

## Validation Checklist (with Mathlib)

```bash
cd lean && lake build                           # Compiles with sorry
cd ..   && uv sync --group sim --group viz       # full env
uv run pytest tests/ --cov=src --cov-fail-under=90  # 340+ passing, ≥90%
uv run python scripts/generate_figures.py       # 21 PNGs in output/figures/
uv run python scripts/simulate_pymdp.py         # pymdp harness artefacts
uv run python scripts/manuscript_variables.py   # JSON in output/data/
uv run python scripts/run_all.py                # full chain + validator
```

## Known Limitations

* The Lean formalization depends on Mathlib for analytic content.
* Many proofs contain `sorry` markers pending formal verification.
* The Python companion remains the numerical oracle for testing.

## Adding to the Formalization

When adding new theorems, use Mathlib's infrastructure. Import from Mathlib as needed, but keep the module self-contained.

## Sorry Hygiene

`sorry` markers are temporary placeholders for proofs that are part of Phase 7. They will be removed as proofs are completed.