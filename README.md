# Policy Entanglement in Active Inference

> **Citation metadata:** DOI [`10.5281/zenodo.20419431`](https://doi.org/10.5281/zenodo.20419431) · source repository
> [`https://github.com/ActiveInferenceInstitute/policy_entanglement`](https://github.com/ActiveInferenceInstitute/policy_entanglement)
> · cite via [`CITATION.cff`](CITATION.cff)

A research project that develops a **tunable mean-field deformation
framework** for multi-stream policy ensembles in active inference. A
single scalar coupling parameter `λ ∈ [0, ∞)` interpolates between
strict mean-field factorization (`λ = 0`) and arbitrary structured
joint policy distributions (`λ → ∞`), with a closed-form *entanglement
decomposition* of variational free energy and an
information-geometric / spectral / formal-verification treatment.

The scope is deliberately narrower than the Free Energy Principle as a
whole: FEP supplies the variational framing, active inference supplies
the process-theory context, and this repository studies the
factorization structure of finite policy posteriors.

This project is one of the active projects under the
[`docxology/template`](https://github.com/docxology/template) two-layer
architecture. It keeps the same mathematics synchronized across the
formal, numerical, empirical, rendering, and documentation surfaces
below:

| Track | Path | Purpose |
|---|---|---|
| **Lean 4** boundary fragment | [`lean/`](lean/) | Machine-checked **typed API skeleton**: every manuscript theorem row has a Lean companion (witness-form, proved, boundary, forwarder, or roadmap); ~15 genuine algebraic proofs over the in-house `CommScalar` typeclass (decomposition four-term re-grouping, coupling-log-weight affineness, bipartite Schmidt-rank-1 ↔ mean-field, …), plus 11 typed-API contracts re-publishing caller-supplied analytic witnesses. Mathlib4 is documented as the separate analytic-discharge layer, not as a hidden dependency of the current build. **Mathlib-free, strict-`sorry`-free, axiom-free**; builds on stock Lean 4 v4.29.0 (17 submodules, 22/22 lake jobs). See "Lean content honesty" section below. |
| **Python analytical companion** | [`src/lean/`](src/lean/) | Numerical realization of every Lean module, dense PMF arithmetic on finite policy spaces |
| **pymdp POMDP harness** | [`src/simulation/`](src/simulation/) | Real `pymdp.agent.Agent` runs from `inferactively-pymdp==1.0.1` (JAX-backed, deterministic FPI), λ-coupling layer on top, plus `FreeEnergyBundle` (VFE / EFE / entropy / coupling-term / TC / action-distribution), multi-K + long-horizon + revertibility + robustness / ablation experiments, and `hyperparameters.py` source-of-truth |
| **Visualizations** | [`src/visualizations/`](src/visualizations/) | Reusable plotting helpers (heatmaps, joint plots, spectral, trajectory, graph, log-weight flow, free-energy dashboards, multi-K plots) |
| **Manuscript registry** | [`src/manuscript/`](src/manuscript/) | Token renderer + auto-numbering pipeline + Lean source extractor + bibliography helper |
| Manuscript prose | [`manuscript/`](manuscript/) | Modular markdown sections rendered to PDF by the template pipeline; every numeric value flows from JSON via `[[VAR:...]]` |
| Figures + sims | [`scripts/`](scripts/) | Thin orchestrators in canonical order via [`run_all.py`](scripts/run_all.py), ending with the regression gate; the live count is derived from `scripts.run_all.SCRIPTS` |
| Documentation | [`docs/`](docs/) | Architecture, math reference, statistics reference, styleguide, Lean / Python API, build / run guides, POMDP simulation guide, changelog, FAQ, reading order |

## Current Snapshot

This table is the current onboarding snapshot.  Volatile release facts
come from generated reports rather than hand-maintained prose:
`output/reports/release_readiness.json`, `output/reports/test_results.json`,
`output/MANIFEST.md`, and the generated theorem map.  Historical round
deltas live in [`docs/CHANGELOG.md`](docs/CHANGELOG.md) and
[`docs/reference/veridical_status.md`](docs/reference/veridical_status.md).

| Layer | Count |
|---|---|
| Lean submodules under [`lean/ActinfPolicyEntanglement/`](lean/ActinfPolicyEntanglement/) | **17** (Basic, Scalar, JointDist, Coupling, FreeEnergy, Geometry, Spectral, Heterogeneous, BernoulliToy, Decomposition, Constructive, Monotonicity, Convexity, MarkovBlanket, SpectralWitnesses, ConnectionsWitnesses, FloatRealResidualWitness) |
| Lake jobs green | **22 / 22** |
| Lean toolchain | stock `leanprover/lean4:v4.29.0` (no Mathlib) |
| Hygiene budget | **0** `sorry`, **0** `axiom`, **0** `unsafe`/`partial`/`noncomputable`, **0** `Mathlib` imports |
| Manuscript theorem rows | **21** total (20 Lean-companion rows + 1 roadmap row). The Lean-companion rows comprise 11 witness-form typed-API contracts + 5 registry-`proved` + 3 boundary rows + 1 forwarder. **Of the 5 `proved`, only 2 are substantive proofs of the named proposition; 3 are statement-restricted** (`prop_6_1`/`prop_6_2`/`prop_7_1` prove a weaker statement than their name). The 3 `boundary` rows mix typed/witness-threaded boundary contracts with definitional boundary facts; use the per-row `faithfulness:` audit in [`docs/reference/veridical_status.md`](docs/reference/veridical_status.md), not the status word alone, to assess proof strength. |
| Lean `theorem` / `lemma` declarations (total) | **76** |
| Structures (witness types) | **11** |
| `def` declarations | **39** |
| Total Lean declarations | **126** |
| Pipeline scripts in [`scripts/run_all.py`](scripts/run_all.py) | Live count from `scripts.run_all.SCRIPTS` / `output/data/manuscript_variables.json` |
| Python tests | Live full-suite count and pass/skip split from `output/reports/test_results.json` (`uv run pytest tests/ --cov=src --cov-fail-under=95`) — see `tests/AGENTS.md` |
| Coverage on `src/` | ≥ 95 % gate; live percentage comes from `output/reports/test_results.json` |
| Lint / type-check | **0** ruff errors, **0** mypy errors |
| PNG figures | Live count from `output/reports/release_readiness.json` / `output/figures/` |
| Rendered manuscript files under `output/manuscript/` | Live count from `output/reports/release_readiness.json` / `output/manuscript/` |
| YAML citation entries | Source-derived from [`manuscript/refs/citations.yaml`](manuscript/refs/citations.yaml); rendered bibliography counts are regenerated by the manuscript pipeline |
| Dashboard invariants | **47 / 47** pass |
| Combined PDF | `output/pdf/actinf_policy_entanglement_lean_combined.pdf`; live page and size values come from `pdfinfo` / `output/reports/release_readiness.json` |

### Lean content honesty: substantive proofs vs typed-API contracts

The "76 theorems / lemmas" total above counts every `theorem`/`lemma` keyword
that `lake build` checks. **Reader: do not conflate** that count with
"76 machine-checked proofs of substantive results." The honest split:

| Category | Count | What it means |
|---|---:|---|
| **Substantive algebraic proofs** (`Scalar`, `Coupling`, `Decomposition.entanglement_decomposition_four_terms_*`, `couplingVerdict_correct`, `Spectral.schmidtRankOne_iff_isBipartiteMeanField`, plus their forwarders) | ~15 | Genuine algebraic identities discharged via `CommScalar` typeclass + tactic chains. These would not type-check if false. |
| **Definitional unfoldings via `rfl`** (`mfImage_isMeanField`, `totalCorrelation_def`, `BernoulliToy.*_total`, the two `Bipartite` corollaries) | ~10 | True by construction; locks definitions to their unfolded shapes. Cheap content but useful for downstream callers. |
| **Witness extractors** (11 witness-form theorems: `entanglement_decomposition`, `freeEnergy_convex_in_lam_witness`, `dualFlat_pythagorean_witness`, `couplingTax_quadratic_bound`, `couplingTax_small_lambda_tolerance`, `freeEnergy_localConcavity_at_zero_witness`, `schmidtRank_upperSemicontinuous_witness`, `sparsityRank_tradeoff_witness`, `hierarchicalAIF_lambda_limit_witness`, `sophisticatedInference_embedding_witness`, `markovBlanket_separation_identity_witness`) | 11 | Typed-API contracts. The analytic identity is supplied by the caller as a `structure` field; the boundary fragment extracts and re-publishes it. **These are not stand-alone proofs of the underlying mathematical claims.** They commit any caller, including a separate Mathlib4 discharge layer, to a specific decomposition shape and parameter-threading discipline; the underlying claims are verified *numerically* by the Python companion in `src/lean/` and at 47 dashboard invariants. |
| **Filler / `Monotonicity` re-exports of Lean core** | ~21 | Re-named wrappers around `Nat.le_refl`, `Nat.zero_le`, etc.  Useful for naming consistency; not framework content. |

In short: ~15 of the 76 Lean theorems are *substantive proofs of
framework algebraic identities*; ~11 are *typed-API contracts* that
re-publish a caller-supplied analytic witness; the remainder are
definitional unfoldings or core-library re-exports.

> **Count provenance (to prevent drift):** the `76` / `39` / `11` / `126`
> figures are the generator's comment-stripped declaration scan, emitted
> live to `output/data/manuscript_variables.json`
> (`lean_theorem_count` / `lean_def_count` / `lean_structure_count` /
> `lean_total_declarations`) and mirrored in
> [`docs/reference/veridical_status.md`](docs/reference/veridical_status.md)
> and [`docs/reference/lean_reference.md`](docs/reference/lean_reference.md).
> When the Lean source changes, re-read those generated values rather than
> hand-editing here. (This README is not token-substituted; keep it in sync
> with the JSON.)

**Why this matters.** The framework's mathematical correctness is
established by (a) the prose proofs in the manuscript body and
appendix S01, (b) the Python numerical witnesses in `src/lean/` and
`src/simulation/`, and (c) the 47 dashboard invariants whose worst-
case residual is recorded in the generated invariant dashboard for the
entanglement-decomposition row. The Lean fragment
contributes (d) a typed-API skeleton that constrains separate additive
Mathlib4-based analytic discharges to a specific shape and (e) genuine algebraic
identities (commutative-ring decompositions, affine-in-λ identities,
the bipartite Schmidt-rank-1 iff).

**The FULL S01 free-energy identity IS now machine-checked — in ℝ, in
a separate Mathlib package.** `MathlibProofs.free_energy_decomposition_full`
proves the literal manuscript S01 boxed identity
`F[q_λ]=Σ_k F[q^k_λ]+γλ⟨K_c⟩+log Z_E(λ)−λ⟨J⟩+I(q_λ)` for the genuine
entangled posterior (`log Z_E` the definitional log-normalizer, not an
assumed scalar; positivity/unit-mass proved; `I(q)` discharged through
the axiom-clean general-`K` kernel `entanglement_decomposition_generalK`),
`#print axioms` → foundational only, `0 sorry/axiom`, two independent
negative controls. (Its first delivery was a `sorryAx`-laundered fake
caught by the axiom gate + a coherence audit and reverted — see
CHANGELOG; only the independently re-verified third state was
accepted.) **The single honest residual, stated here not buried:** it
is an **ℝ** proof while this pipeline's numbers are **Float** — a
*verified* error-bounded Float↔ℝ bridge is genuine, precisely-scoped
**unbuilt** research work (Lean `Float` is opaque `@[extern]`; the two
sound routes are a Flocq-style IEEE model or an interval
re-implementation). **Enforcement, stated precisely (no over-claim):**
this project is local-only/not-git-tracked so no CI runs it; the
`#print axioms` foundational-only audit
(`scripts/build_mathlib_proofs.py`) runs on the automatic pytest path
via `tests/test_mathlib_axiom_audit.py` **when the Lean toolchain is
available** (and *honestly xfails — never silently passes —* when it is
not), and additionally on the opt-in `--with-mathlib` path; the fast
`tests/test_mathlib_proofs_integrity.py` is a grep tripwire that
does **not** by itself catch transitive `sorryAx`. The roadmap is
[`lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md);
the normative tier ledger is
[`docs/reference/methods_and_assumptions.md`](docs/reference/methods_and_assumptions.md).

See [`docs/reference/veridical_status.md`](docs/reference/veridical_status.md)
for the live ground-truth tally; this section and the abstract are
kept in agreement by `tests/test_h1_headline_invariant.py`.

### Mathlib4 integration readiness

Mathlib4 integration is an additive proof-discharge layer, not a
dependency smuggled into the current boundary package. The current
boundary fragment remains stock Lean, defines the theorem names and
witness structures, and keeps `lake build` fast. The separate
`lean/MathlibProofs/` package now contains the headline
`free_energy_decomposition_full` discharge, the general-$K$ finite-KL
kernel (`entanglement_decomposition_generalK`), supporting KL /
cross-term lemmas, and matrix-rank readiness plumbing. That is enough
to support the manuscript's real-valued headline decomposition claim;
remaining witness-form rows still require row-specific compiled
Mathlib source and registry updates before promotion.

| Integration slice | First targets | Why it comes here |
|---|---|---|
| Headline finite `ℝ` PMF + entropy/KL discharge | `thm_4_1` plus the S01 boxed identity | The general-K finite-sum, log, entropy, KL, and marginalization infrastructure now proves the real-valued decomposition under the MathlibProofs gate. |
| Real log-partition and convexity/Taylor layer | `thm_4_2`, `thm_4_3`, `prop_10_1`, `thm_8_1`, `cor_8_2` | Once `F(λ)` is represented over `ℝ`, convexity, local Taylor behavior, and quadratic coupling-tax bounds can be discharged in a single proof family. |
| Matrix/rank layer | `prop_7_1`, `prop_7_2`, `thm_7_3` | Bipartite rank-one facts are nearest to existing finite-dimensional linear algebra; tensor-train ranks require project-local definitions on top. |
| Limit/recursive layer | `thm_11_1`, `prop_11_2` | These require concentration, filter/limit, and recursive-policy infrastructure, so they should follow the finite and convex foundations. |

The generated theorem map now carries a per-theorem readiness table:
[`docs/reference/_theorem_map.md`](docs/reference/_theorem_map.md#mathlib4-discharge-readiness).
The implementation scope note is
[`lean/MathlibProofs/README.md`](lean/MathlibProofs/README.md), and
the boundary-level payload plan is
[`lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).
Exact import paths should be chosen against the Mathlib version pinned
by that separate additive package; the current manuscript cites only
compiled MathlibProofs declarations as validated code.

## What it looks like in 20 lines

The framework is centered on a single function: `entangled_posterior`.
Hand it the per-stream mean-field prior, per-stream EFE, the two
coupling potentials $J$ and $K_c$, the precision $\gamma$, and the
coupling strength $\lambda$ — it returns the joint policy
distribution.  Decoupling at $\lambda = 0$ recovers the mean field
exactly; cranking $\lambda$ up concentrates probability on aligned
joint policies.

```python
import numpy as np
from lean.coupling import entangled_posterior
from lean.free_energy import total_correlation

mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]   # K=2 binary streams
G  = [np.zeros(2), np.zeros(2)]                     # no per-stream EFE
J  = np.array([[1.0, -1.0], [-1.0, 1.0]])           # bilinear Ising habit
Kc = np.zeros((2, 2))                               # no preference coupling

for lam in [0.0, 1.0, 4.0]:
    q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=lam)
    print(f"λ={lam}:  q={q.flatten().round(3)}   I(q)={total_correlation(q):.4f}")

# λ=0.0:  q=[0.25 0.25 0.25 0.25]   I(q)=0.0000   ← mean-field manifold
# λ=1.0:  q=[0.440 0.060 0.060 0.440]  I(q)=0.3278  ← skilled (mixed) regime
# λ=4.0:  q=[0.500 0.000 0.000 0.500]  I(q)=0.6901  ← frozen onto two archetypes
```

The mean-field manifold ($I(q) = 0$) at $\lambda = 0$ and the
archetypal limit ($I(q) \to \log 2$) at large $\lambda$ are the two
poles between which the framework's theorems live.

## Quick start

`uv` manages the environment. The `sim` and `viz` groups bring in
`inferactively-pymdp==1.0.1` (which provides the `pymdp` import/API)
and the visualization stack respectively. The root template
`pyproject.toml` does **not** include pymdp — run `uv sync --group sim`
inside this project (or use the project `.venv`) for the full empirical
suite; [`conftest.py`](conftest.py) bootstraps missing artifacts when
tests run before analysis under `./run.sh --pipeline`.

### Two pipeline paths

| Path | When to use |
|---|---|
| **Template** `./run.sh --project actinf_policy_entanglement_lean --pipeline` | Stage 4 runs only `run_all.py` (via `manuscript/config.yaml` allowlist). Stage 5 (`03_render_pdf.py`) does **not** use this project's injector — PDF is optional here. |
| **Release** `make pipeline-release` or `uv run python scripts/run_all.py --with-pdf --with-mathlib` | Full artifact chain including `build_pdf.py`, `validate_pdf.py`, `readiness_report.py`, and optional MathlibProofs. |

Combined PDF output: `output/pdf/actinf_policy_entanglement_lean_combined.pdf`
(copied to root `output/pdf/actinf_policy_entanglement_lean_combined.pdf` when the template
stage 9 runs after a `--with-pdf` analysis).

```bash
# Default (core + dev + viz):
uv sync

# Add the pymdp simulation harness:
uv sync --group sim --group viz

# Lean build (boundary fragment, no Mathlib needed):
cd lean && lake build                              # 22/22 jobs green

# Lean + sorry/axiom budget gate (returns non-zero on regression):
uv run python scripts/build_lean.py

# Python tests (live full-suite count from output/reports/test_results.json; configured coverage gate in pyproject.toml):
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=95

# Run *everything* end-to-end (canonical order from scripts/run_all.py):
uv run python scripts/run_all.py

# Release/readiness gate, including PDF render validation:
make readiness

# Explicit full release pipeline (PDF + optional MathlibProofs subgate):
uv run python scripts/run_all.py --with-pdf --with-mathlib
```

The canonical pipeline executed by
[`scripts/run_all.py`](scripts/run_all.py) is, in order:

1. `build_lean.py` — lake build + sorry/axiom/unsafe budget gate
2. `generate_figures.py` — analytical PNG figures
3. `dump_archetypes.py` — frozen-archetype CSV
4. `parameter_sweep.py` — configured `PARAMETER_SWEEP_LAMBDAS` sweep
5. `simulate_pymdp.py` — `inferactively-pymdp==1.0.1` / `pymdp` POMDP harness + free-energy bundle
6. `simulate_multi_k.py` — configured `MULTI_K_VALUES` ensemble experiments
7. `simulate_long_horizon.py` — configured `LONG_HORIZON_STEPS` habit-accumulation rollout
8. `simulate_revertibility.py` — m-projection back-to-mean-field witness
9. `simulate_robustness.py` — robustness, ablation, and replicate sidecars
10. `simulate_btai.py` — shipped BTAI baseline worked run
11. `simulate_adversarial.py` — shipped adversarial-perturbation sweep
12. `simulate_gnn.py` — GNN fifth-track round-trip and Lean typed-contract emitter
13. `manuscript_variables.py` — JSON variable mirror from current hyperparameters and sidecars
14. `build_dashboard.py` — invariant dashboard (47 invariants)
15. `generate_index.py` — manuscript index
16. `generate_theorem_map.py` — four-track Lean ↔ Python ↔ test table
17. `inject_manuscript_variables.py` — token + equation + figure rendering
18. `validate_outputs.py` — PNG / CSV / JSON schema gate
19. `validate_manuscript.py` — token + range + four-track-wiring gate
20. `regression_gate.py` — compare test, coverage, invariant, and Lean-budget metrics against `scripts/regression_baseline.json`

The methods contract is therefore inspectable in three places: pipeline
order in [`scripts/run_all.py`](scripts/run_all.py), generated values
in `output/data/manuscript_variables.json`,
and theorem wiring in
[`docs/reference/_theorem_map.md`](docs/reference/_theorem_map.md).
Manuscript source never hand-writes paper-facing display numbers:
numeric results use `[[VAR:...]]`, and section / theorem / figure /
equation references use registry tokens (`[[SECREF:...]]`,
`[[THMREF:...]]`, `[[FIGREF:...]]`, `[[EQREF:...]]`). Rendered PDF
and markdown outputs contain resolved labels and values by design;
the strict gate is on source fields.
For reviewer-facing details on figure metadata, variable injection,
and Mathlib integration checkpoints, see
[`docs/reference/methods_orchestration.md`](docs/reference/methods_orchestration.md)
and the release checklist
[`docs/reference/reproducibility_checklist.md`](docs/reference/reproducibility_checklist.md).
`make readiness` also writes the live reviewer release note to
`output/reports/release_note.md`; that generated file carries the
claim-strength ledger (`proved`, `witness`, `empirical`, `hypothesis`,
`roadmap`) used by the manuscript appendix.

## Output inventory

Every artifact under `output/` is regenerable by
`scripts/run_all.py`; nothing in the directory is hand-edited and
nothing is committed.

| Subdirectory | Contents |
|---|---|
| `output/figures/` | Live PNG count from `output/reports/release_readiness.json`; analytical + pymdp + multi-K + long-horizon + revertibility + robustness/ablation/null-control sidecars, each carrying `project.*` tEXt metadata (script, function, hyperparameter snapshot, git revision, ISO timestamp, schema-v2 plotted-statistics and font metadata) |
| `output/data/` | `manuscript_variables.json`, archetypes, theorem map, invariant dashboard |
| `output/simulations/` | `pymdp_free_energy_bundle.csv`, one `pymdp_K*_sweep.csv` per configured multi-K value, `pymdp_long_horizon.csv`, `pymdp_revertibility.csv`, robustness / ablation / replicate sidecars, plus per-script run summaries |
| `output/manuscript/` | Live rendered Markdown count from `output/reports/release_readiness.json` (currently the preamble plus 37 manuscript section files), all tokens / citations / equations / figures resolved |
| `output/pdf/` | `actinf_policy_entanglement_lean_combined.pdf` — combined PDF, validated by `scripts/validate_pdf.py`; page and size values are generated status fields |

## Imports

Every test, script, and intra-package reference uses the canonical
namespaced subpackage path:

```python
from lean.coupling import entangled_posterior
from lean.free_energy import total_correlation
from simulation.specs import CoupledEnsembleSpec
from manuscript.registry import load_registry
from visualizations.heatmaps import plot_lambda_utility_heatmap
```

`pyproject.toml` puts `src/` on `pythonpath`; intra-subpackage
imports use relative form (`from .coupling import …`).

## Key links

- Manuscript index: [`manuscript/INDEX.md`](manuscript/INDEX.md)
- Documentation hub: [`docs/README.md`](docs/README.md)
- Lean + pymdp methods audit: [`docs/reference/methods_audit.md`](docs/reference/methods_audit.md)
- Reading order by reader persona: [`docs/READING_ORDER.md`](docs/READING_ORDER.md)
- FAQ: [`docs/FAQ.md`](docs/FAQ.md)
- Per-round revision history: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Lean tree: [`lean/ActinfPolicyEntanglement/`](lean/ActinfPolicyEntanglement/) and the
  witness-payload-discharge plan [`lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
- Pipeline orchestrator: [`scripts/run_all.py`](scripts/run_all.py)
- Reproducibility checklist: [`docs/reference/reproducibility_checklist.md`](docs/reference/reproducibility_checklist.md)
- Agent / contributor cheat-sheet: [`AGENTS.md`](AGENTS.md)
- Styleguide (manuscript ↔ code contract): [`docs/guides/styleguide.md`](docs/guides/styleguide.md)
- Live audit page: [`docs/reference/veridical_status.md`](docs/reference/veridical_status.md)

## Reading order

Different readers have different optimal entry points. Pick one of
the curated paths in [`docs/READING_ORDER.md`](docs/READING_ORDER.md):

- **Mathematician** — go from theorem statements through proofs.
- **Software engineer** — go from the pipeline into the modules.
- **Active inference researcher** — go from the empirical suite up to
  the deformation framework.
- **Lean / formal-methods reader** — go from the Lean boundary
  fragment outward to the registry-anchored four-track contract.

## License

The manuscript is released under **CC-BY-4.0**.  Code follows the
MIT-style license inherited from the parent
[`docxology/template`](https://github.com/docxology/template)
repository.

## Citation

Friedman, D. A. (2026). *Policy Entanglement in Active Inference: A
Tunable Mean-Field Deformation Framework for Multi-Stream Policy
Ensembles, with Information-Geometric, Spectral, and
Lean-Formalization Treatments.* Active Inference Institute (working
manuscript).

> **Note.** [`manuscript/config.yaml`](manuscript/config.yaml) carries DOI
> [`10.5281/zenodo.20419431`](https://doi.org/10.5281/zenodo.20419431). Source code and
> reproducibility artifacts live at
> [`https://github.com/ActiveInferenceInstitute/policy_entanglement`](https://github.com/ActiveInferenceInstitute/policy_entanglement).
