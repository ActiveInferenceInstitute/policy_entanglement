# AGENTS.md — `actinf_policy_entanglement_lean`

**Citation metadata:** DOI [`10.5281/zenodo.20418904`](https://doi.org/10.5281/zenodo.20418904) · source repository
[`https://github.com/ActiveInferenceInstitute/policy_entanglement`](https://github.com/ActiveInferenceInstitute/policy_entanglement)
· cite via [`CITATION.cff`](CITATION.cff) and [`manuscript/config.yaml`](manuscript/config.yaml).

This is the agent / contributor onboarding guide for the
**Policy Entanglement in Active Inference** project. Read
[`README.md`](README.md) first for the elevator pitch; then read
this file before editing anything. Per-directory cheat-sheets live
alongside the code:

- [`docs/AGENTS.md`](docs/AGENTS.md) — documentation conventions
- [`lean/AGENTS.md`](lean/AGENTS.md) — Lean 4 boundary fragment rules
- [`manuscript/AGENTS.md`](manuscript/AGENTS.md) — prose + registry rules
- [`scripts/AGENTS.md`](scripts/AGENTS.md) — thin-orchestrator pipeline
- [`tests/AGENTS.md`](tests/AGENTS.md) — no-mocks test policy

## Identity & scope

A Lean 4 formalization of **Policy Entanglement in Active Inference**,
paired with a Python analytical companion, an `inferactively-pymdp==1.0.1`
POMDP simulation harness using the `pymdp` import/API, a visualization
stack, and a modular manuscript.

The Lean fragment is currently:

- **Mathlib-free** — builds on stock Lean 4 v4.29.0
- **`sorry`-free** — every algebraic theorem is fully proved on the
  in-house `CommScalar α` typeclass, every existence theorem is
  expressed as a witness-consuming boundary form
- **`axiom`-free** — no global axioms, no IEEE-754 cheats
- **`unsafe` / `partial` / `noncomputable`-free** — every declaration
  is total and constructive

The Mathlib4 analytic payload (KL chain rule, matrix SVD, Bregman
Taylor expansion) sits behind the witness boundary; a separate
`MathlibProofs` library can discharge those payloads without touching
the boundary fragment. The current `lean/MathlibProofs/` tree now
discharges the headline real-valued free-energy decomposition through
`free_energy_decomposition_full` and the general-$K$ finite-KL kernel,
while the remaining witness-form rows still require row-specific
payload proofs before promotion. See
[`lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
for the witness-payload-discharge plan.

## Current Ground-Truth Snapshot

| Layer | Count |
|---|---|
| Lean submodules in [`lean/ActinfPolicyEntanglement/`](lean/ActinfPolicyEntanglement/) | Source-derived by `scripts/manuscript_variables.py`; see `output/data/manuscript_variables.json` |
| Lake jobs green | Live summary from `scripts/build_lean.py` and `output/reports/release_readiness.json` |
| Hygiene budget | Guarded by `scripts/build_lean.py`: zero `sorry`, zero `axiom`, zero `unsafe`/`partial`/`noncomputable`, zero boundary `Mathlib` imports |
| Lean declarations and theorem-row counts | Source-derived from Lean files and `manuscript/refs/labels.yaml`; live roll-up in `output/data/manuscript_variables.json` and `docs/reference/_theorem_map.md` |
| Pipeline scripts (`scripts/run_all.py`) | Canonical default list lives in `scripts/run_all.py`; release runs may add `--with-pdf` and `--with-mathlib` subgates |
| Python tests | Live full-suite count and pass/skip split from `output/reports/test_results.json` |
| Coverage on `src/` | ≥ 95 % gate; live percentage from `output/reports/test_results.json`; critical validator-module floors are enforced by `scripts/regression_gate.py` |
| Lint / type-check | Run `uvx ruff check src/ scripts/ tests/` and `uv run mypy src/ scripts/`; both must be zero-error |
| PNG figures (in `output/figures/`) | Live count from `output/reports/release_readiness.json` / `output/figures/` |
| Rendered manuscript files (in `output/manuscript/`) | Live count from `output/reports/release_readiness.json` |
| YAML citation and bibliography entries | Source-derived from `manuscript/refs/citations.yaml` by `scripts/manuscript_variables.py` and bibliography validation |
| Dashboard invariants | Live count from `output/reports/dashboard_invariants.txt` and the regression gate |
| Combined PDF | Live page count and file size from `scripts/validate_pdf.py` / `pdfinfo` after `scripts/run_all.py --with-pdf` |

The per-round revision history with explanations of *why* counts
moved between rounds lives in [`docs/CHANGELOG.md`](docs/CHANGELOG.md).

**Claim audit matrix:** CSV
[`docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv`](docs/_audit/pymdp_lean_manuscript_matrix_2026-05-21.csv);
regenerate with [`scripts/generate_audit_matrix.py`](scripts/generate_audit_matrix.py)
(`--write` / `--check`); cross-track rows from
[`manuscript/refs/audit_tracks.yaml`](manuscript/refs/audit_tracks.yaml).

## Repository layout

```
.
├── README.md            ← elevator pitch + live counts
├── AGENTS.md            ← (this file)
├── pyproject.toml       ← uv-managed Python packaging + pytest + coverage
├── conftest.py          ← canonical `src/` PYTHONPATH insertion
├── lean/                ← Lean 4 package (boundary fragment + FepSketches re-exports)
│   ├── lakefile.lean    ← Lake build config; Mathlib-free / sorry-free / axiom-free
│   ├── lean-toolchain   ← pinned to leanprover/lean4:v4.29.0
│   ├── ActinfPolicyEntanglement/
│   │   ├── Basic · Scalar · JointDist · Coupling · FreeEnergy · Geometry · Spectral
│   │   ├── Heterogeneous · BernoulliToy · Decomposition · Constructive · Monotonicity
│   │   ├── Convexity · MarkovBlanket · SpectralWitnesses · ConnectionsWitnesses
│   │   └── MathlibRefinementRoadmap.md   ← witness-payload-discharge plan
│   └── FepSketches/     ← fep_lean-compatible `FepSketches.*` re-exports
├── manuscript/          ← Modular markdown sections + config + preamble + INDEX.md
├── docs/                ← Modular technical documentation
│   ├── README.md · CHANGELOG.md · FAQ.md · READING_ORDER.md
│   ├── guides/ · reference/ · modules/ · simulation/
├── src/
│   ├── lean/            ← Analytical mirrors of the Lean modules
│   ├── simulation/      ← pymdp 1.0.1 POMDP harness (specs, builders, agents, …)
│   ├── gnn/             ← Fifth-track GNN round-trip (parse → bridge → sidecar)
│   ├── visualizations/  ← Reusable plotting helpers
│   ├── manuscript/      ← Registry, validators, renderer, lean-snippet extractor
│   ├── reporting/       ← Dashboard HTML/JSON/plaintext emission
│   ├── gates/           ← Parameterised pipeline gate logic (`regression_gate.py`)
│   ├── orchestration/   ← End-to-end pipeline runner (`run_all.py`)
│   └── dashboard_types/ ← Shared panel/control/invariant dataclasses
├── tests/               ← live full-suite collection from output/reports/test_results.json (pure-numpy + pymdp-marked + viz + lean-build gate + hyperparameters + equation auto-numbering + free-energy bundle + statistics + metadata + veridicality + python-api coverage + token-resolution + project-wide hyperlink audit)
├── scripts/             ← thin orchestrators; `run_all.py` runs the canonical default pipeline
└── output/              ← Generated artifacts (figures, data, simulations, manuscript, pdf) — disposable
```

## Authoring rules (you must follow these)

1. **Mathlib-free at the Lean boundary.** Do not add `import Mathlib…`
   to any module under `lean/ActinfPolicyEntanglement/` or
   `lean/FepSketches/`. The package builds on stock Lean 4 v4.29.0;
   any Mathlib refinement lives in a separate `MathlibProofs`
   library inside `lean/`.
2. **Hygiene budget = 0.** No `sorry`, no `axiom`, no `unsafe` /
   `partial` / `noncomputable`. CI runs
   [`scripts/build_lean.py`](scripts/build_lean.py) which enforces
   this; a single regression fails the build.
3. **Reserved Lean tokens.** `Π` and `λ` are Lean 4 binder tokens;
   never use them as ordinary identifiers — use `Pol`, `q_lam`,
   `lam`, etc.
4. **Every numeric value flows through `[[VAR:...]]`.** No hardcoded
   `121-point grid`, `seed = 42`, `T = 10 steps` etc. in `manuscript/`
   prose, headings, figure captions, figure short labels, or rendered
   registry titles. All such values are owned by
   [`src/simulation/hyperparameters.py`](src/simulation/hyperparameters.py),
   mirrored into `output/data/manuscript_variables.json` by
   [`scripts/manuscript_variables.py`](scripts/manuscript_variables.py),
   and substituted by
   [`scripts/inject_manuscript_variables.py`](scripts/inject_manuscript_variables.py).
   Section, theorem, figure, and equation references likewise flow
   through `[[SECREF:...]]`, `[[THMREF:...]]`, `[[FIGREF:...]]`, and
   `[[EQREF:...]]`; do not hand-write `§9.5`, `Theorem 5.1`,
   `Figure 7`, or `Eq. (3)` in paper-facing source fields.
   When code comments, tests, docs, or figure annotations mention a
   display number for reader orientation, check it against
   `manuscript/refs/labels.yaml`; old display numbers belong only in
   explicitly historical revision notes.
   The validator
   [`scripts/validate_manuscript.py`](scripts/validate_manuscript.py)
   calls `manuscript.validation.find_hardcoded_numeric_literals`,
   `find_hardcoded_refs`, and
   `find_hardcoded_rendered_source_literals`; any offense fails CI.
5. **No mocks in tests.** Use real `numpy` arrays; if you need
   randomness, use `np.random.default_rng(seed=…)` with a fixed seed.
   `MagicMock`, `mocker.patch`, `unittest.mock` and similar are
   forbidden anywhere in `tests/`.
6. **Coverage floor: 95 %.** CI runs
   `pytest tests/ --cov=src --cov-fail-under=95`. Keep focused coverage
   additions with any new source behavior.
7. **Namespaced Python imports.** Every test, script, and intra-package
   reference uses `from lean.coupling import …`,
   `from simulation.specs import …`,
   `from manuscript.registry import …`,
   `from visualizations.heatmaps import …`. Never bare imports
   (`from coupling import …`); never relative imports outside the
   same subpackage.
8. **Thin orchestrators only in `scripts/`.** Every numerical
   computation must come from `src/`; `scripts/` handles I/O,
   matplotlib, and stdout-path emission.
9. **Print output paths to stdout** in scripts, one per line, so the
   pipeline manifest can collect them.
10. **Headless matplotlib.** Always set `MPLBACKEND=Agg` before
    importing `matplotlib.pyplot`; the scripts already do this.
11. **Determinism.** All scripts must run reproducibly (fixed seeds,
    no time-dependent state).
12. **Disposable `output/`.** Treat the entire `output/` tree as
    regenerable; never hand-edit it, never commit transient outputs.
13. **American English for prose.** README, AGENTS, docs, manuscript
    sections, captions, and generated prose use American spelling.
    Preserve exact citation titles, external schema fields, and stable
    code identifiers even when they contain historical spellings.

## Historical Revision Note: Round 3

(See [`docs/CHANGELOG.md`](docs/CHANGELOG.md) for the full per-round
revision history.)

- **Two new Lean submodules.**
  [`SpectralWitnesses.lean`](lean/ActinfPolicyEntanglement/SpectralWitnesses.lean)
  with `schmidtRank_upperSemicontinuous_witness` (Prop 8.2) and
  `sparsityRank_tradeoff_witness` (Thm 8.3); and
  [`ConnectionsWitnesses.lean`](lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean)
  with `hierarchicalAIF_lambda_limit_witness` (Thm 17.1) and
  `sophisticatedInference_embedding_witness` (Prop 17.2).
- **Three new orchestrator scripts.**
  [`simulate_multi_k.py`](scripts/simulate_multi_k.py) (configured
  `MULTI_K_VALUES` Ising sweep),
  [`simulate_long_horizon.py`](scripts/simulate_long_horizon.py)
  (`LONG_HORIZON_STEPS` rollout, habit accumulation),
  [`simulate_revertibility.py`](scripts/simulate_revertibility.py)
  (m-projection round-trip witness).
- **Sketch & deferred buckets are empty.**
  The four remaining `deferred` theorems graduated to `witness` status
  via the two new Lean modules and three new empirical scripts; the
  algebraic boundary identity `couplingVerdict_correct` graduated
  Corollary 5.2 from `sketch` to `proved`. Proposition 7.1 was
  audit-graduated from `sketch` to `proved` (the constructive proof
  was already complete; the registry label was stale).
- **Historical checkpoint status distribution: 10 witness · 6 proved · 3
  boundary · 1 forwarder · 0 sketch · 0 deferred.**  (Stale historical
  snapshot — current is 11 witness · 5 proved · 3 boundary · 1
  forwarder.)  Note `status: proved` ≠ "proved as named": per-row
  `faithfulness:` (only 2 substantive; 3 statement-restricted) lives in
  `manuscript/refs/labels.yaml` and `docs/reference/veridical_status.md`.
  The current live distribution is generated from
  `manuscript/refs/labels.yaml` into
  `output/data/manuscript_variables.json` and the theorem map.
- **+6 PNGs**, **+1 dashboard invariant** (`revertibility_kl_equals_multiinformation`,
  bringing the total to 47), **+3 pipeline scripts**, **+35 round-3
  lock-down tests**.
- **New docs files.** [`docs/CHANGELOG.md`](docs/CHANGELOG.md),
  [`docs/FAQ.md`](docs/FAQ.md),
  [`docs/READING_ORDER.md`](docs/READING_ORDER.md), and the per-module
  pages [`docs/modules/spectral_witnesses.md`](docs/modules/spectral_witnesses.md)
  and [`docs/modules/connections_witnesses.md`](docs/modules/connections_witnesses.md).
- **Roadmap relabel.**
  [`MathlibRefinementRoadmap.md`](lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
  replaces the retired phase-style roadmap document; the "deferred
  theorems" framing is retired in favor of a witness-payload-discharge
  plan (every registry row has a live Lean companion; the Mathlib
  payload refines `witness` rows into `proved` rows). The retired
  companion-paper outline page has been folded into
  [`docs/READING_ORDER.md`](docs/READING_ORDER.md) and
  [`docs/FAQ.md`](docs/FAQ.md).

## Worked example — adding a small theorem end-to-end

Suppose you want to register a new identity: *"the entangled posterior
at $\lambda = 0$ is exactly mean-field"*. The four-track contract
shapes the work in a definite order:

1. **Manuscript prose first.**  Add a paragraph (and a registry entry
   in `manuscript/refs/labels.yaml::theorems`) under the appropriate
   section. Use `[[THMREF:my_label]]` for forward references.

2. **Lean statement next.**  Add a `theorem` to the closest
   `lean/ActinfPolicyEntanglement/*.lean` module. Keep it on the
   `CommScalar α` typeclass so it remains Mathlib-free:

   ```lean
   theorem entangledPosterior_at_zero_is_meanField
       (E G : MFDist K Pol) (J Kc : CouplingPotential α K Pol)
       (γ : α) (π : PolicySpace K Pol) :
       entangledPosteriorLogWeight E G J Kc γ 0 π
         = sumLogPrior E π - γ * sumEFE G π := by
     simp [entangledPosteriorLogWeight, couplingLogWeight_at_zero]
   ```

   then `cd lean && lake build` until it compiles.

3. **Python numerical witness.**  Mirror the claim in
   `src/lean/<module>.py` as a Python function, and add a test in
   `tests/test_<module>.py` that calls the real `entangled_posterior`
   at `lam=0.0` and asserts equality with `mean_field_to_joint(mf)`
   to `atol=1e-12` — exactly the pattern of `tests/test_coupling.py`.

4. **Wire the four-track row.**  Add a row to
   `scripts/generate_theorem_map.py::PYTHON_COMPANION` and
   `::TEST_GATE` pointing at the new Python function and test file,
   then run `uv run python scripts/generate_theorem_map.py` to
   regenerate `docs/reference/_theorem_map.md`.

5. **Validate.**  `uv run python scripts/validate_manuscript.py &&
   uv run pytest tests/`. Both should be green before commit.

The whole loop typically takes 20–30 minutes for a non-trivial
algebraic identity. Skipping any track *will* trip CI: the manuscript
validator catches dangling `[[THMREF:]]` tokens, the Lean build
catches type-checking regressions, and the test gate catches
analytical drift.

## How agents should work — quick map

| Want to … | Edit | Then run |
|---|---|---|
| add a Lean theorem | a file under `lean/ActinfPolicyEntanglement/` | `cd lean && lake build` then `uv run python scripts/build_lean.py` |
| add an algebraic lemma reusable across modules | `lean/ActinfPolicyEntanglement/Scalar.lean` | `cd lean && lake build` |
| add an analytical helper | a file under `src/lean/` | `uv run pytest tests/test_<module>.py` |
| add a pymdp harness piece | a file under `src/simulation/` | `uv run pytest tests/test_simulation_*.py` |
| add a plotting helper | a file under `src/visualizations/` | `uv run pytest tests/test_visualizations.py` |
| add a test | a file under `tests/` | `uv run pytest tests/<file>` |
| add a figure | `scripts/generate_figures.py` or `scripts/simulate_*.py` | `uv run python scripts/<script>.py` |
| change a grid / seed / rollout horizon | [`src/simulation/hyperparameters.py`](src/simulation/hyperparameters.py) | full pipeline (JSON mirror + manuscript prose update automatically) |
| add a manuscript variable | extend a `_*_facts` helper in [`scripts/manuscript_variables.py`](scripts/manuscript_variables.py) and reference it via `[[VAR:key]]` | `uv run python scripts/manuscript_variables.py && uv run python scripts/inject_manuscript_variables.py` |
| change manuscript prose | a file under `manuscript/` (no hardcoded numbers — use `[[VAR:…]]`) | `uv run python scripts/inject_manuscript_variables.py && uv run python scripts/validate_manuscript.py` |
| add a registered equation | extend `manuscript/refs/labels.yaml` under `equations:` and place via `[[EQ:label]]` | full pipeline (auto-numbering picks it up at render time) |
| validate the release PDF | `manuscript/`, `output/manuscript/`, local Pandoc/XeLaTeX renderer | `uv run python scripts/build_pdf.py && uv run python scripts/validate_pdf.py` |
| prepare MathlibProofs | `lean/MathlibProofs/` only | `uv run python scripts/build_mathlib_proofs.py` (do not cite as proved until real theorem source builds) |
| add architecture / math / stats docs | a file under `docs/` | (none) |

## Cross-track invariants

The Lean and Python tracks are deliberately structured to mirror each
other. When you add a concept on one side, prefer to mirror it on
the other so the two stay in sync.

| Concept | Lean module | Python module |
|---|---|---|
| Joint / mean-field PMFs, marginalization | [`ActinfPolicyEntanglement.JointDist`](lean/ActinfPolicyEntanglement/JointDist.lean) | [`src/lean/joint_dist.py`](src/lean/joint_dist.py) |
| Abstract scalar / ring laws | [`Scalar`](lean/ActinfPolicyEntanglement/Scalar.lean) | (implicit — Python uses `numpy.float64`) |
| Constructive existence helpers (witnesses) | [`Constructive`](lean/ActinfPolicyEntanglement/Constructive.lean) | (boundary witnesses — no Python counterpart) |
| Monotonicity / order lemmas | [`Monotonicity`](lean/ActinfPolicyEntanglement/Monotonicity.lean) | (used implicitly by `numpy` ordering) |
| Coupling potentials, λ-entangled prior / posterior | [`Coupling`](lean/ActinfPolicyEntanglement/Coupling.lean) | [`src/lean/coupling.py`](src/lean/coupling.py) |
| Free energies, entropies, total correlation | [`FreeEnergy`](lean/ActinfPolicyEntanglement/FreeEnergy.lean) | [`src/lean/free_energy.py`](src/lean/free_energy.py) |
| e/m-flatness, m-projection, Pythagorean | [`Geometry`](lean/ActinfPolicyEntanglement/Geometry.lean) | [`src/lean/geometry.py`](src/lean/geometry.py) |
| Bipartite mean-field factorization, archetypes | [`Spectral`](lean/ActinfPolicyEntanglement/Spectral.lean) | [`src/lean/spectral.py`](src/lean/spectral.py) |
| Schmidt rank upper-semicontinuity, sparsity-rank envelope | [`SpectralWitnesses`](lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) | (round-3 witness payload) |
| Hierarchical AIF λ-limit, sophisticated-inference embedding | [`ConnectionsWitnesses`](lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) | (round-3 witness payload) |
| Heterogeneous VFE / EFE, coupling tax (Thm 9.1) | [`Heterogeneous`](lean/ActinfPolicyEntanglement/Heterogeneous.lean) | [`src/lean/heterogeneous.py`](src/lean/heterogeneous.py) |
| K=2 Bernoulli toy | [`BernoulliToy`](lean/ActinfPolicyEntanglement/BernoulliToy.lean) | [`src/lean/bernoulli_toy.py`](src/lean/bernoulli_toy.py) |
| Theorem 5.1 (`thm_4_1`) entanglement decomposition | [`Decomposition`](lean/ActinfPolicyEntanglement/Decomposition.lean) | [`src/lean/decomposition.py`](src/lean/decomposition.py) |
| Free-energy convexity / local concavity at λ = 0 | [`Convexity`](lean/ActinfPolicyEntanglement/Convexity.lean) | (witness payload — Python checks via sweep) |
| Markov-blanket separation identity | [`MarkovBlanket`](lean/ActinfPolicyEntanglement/MarkovBlanket.lean) | (witness payload — Python checks via sweep) |
| pymdp-grounded coupled posterior + free-energy bundle | (no Lean counterpart — runtime layer) | [`src/simulation/inference.py`](src/simulation/inference.py) |
| Simulation hyperparameters (single source of truth) | (no Lean counterpart) | [`src/simulation/hyperparameters.py`](src/simulation/hyperparameters.py) |
| Manuscript registry + token rendering + auto-numbering | (no Lean counterpart) | [`src/manuscript/`](src/manuscript/) |

## Verification gates (before commit)

A contributor must pass all four gates locally before pushing:

```bash
# Gate 1 — Lean budget: zero sorry/axiom/unsafe regressions
uv run python scripts/build_lean.py

# Gate 2 — Python tests + coverage floor
uv sync --group sim --group viz
uv run pytest tests/ --cov=src --cov-fail-under=95

# Gate 3 — Full pipeline (canonical `scripts/run_all.py` order; exits 0 end-to-end on green)
uv run python scripts/run_all.py

# Optional release gate — full pipeline plus PDF render validation
uv run python scripts/run_all.py --with-pdf

# Full release gate with optional additive MathlibProofs build recorded:
uv run python scripts/run_all.py --with-pdf --with-mathlib

# Gate 4 — Lint + type-check (must be 0 errors each)
uvx ruff check src/ scripts/ tests/
uv run mypy src/ scripts/
```

CI runs each gate independently; the project-wide hyperlink audit
test (`tests/test_project_wide_hyperlinks.py`) additionally validates
that every cross-link inside `AGENTS.md`, `README.md`, `docs/`,
`manuscript/`, and `lean/` resolves to a real file.

## Known limitations

- The Mathlib-witness analytic content (KL chain rule, SVD-based
  matrix rank, Bregman Taylor expansion, real-analytic continuity) is
  exposed by the boundary fragment as **witness-consuming theorems**:
  the caller (or the separate additive `MathlibProofs` layer) supplies the
  analytic witness, and the boundary fragment certifies the resulting
  decomposition without any `sorry` of its own. See
  [`lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
  and
  [`docs/reference/lean_reference.md`](docs/reference/lean_reference.md)
  for per-theorem witness signatures.
- The canonical manuscript is the modular set under `manuscript/`;
  `scripts/generate_figures.py`, `scripts/simulate_*.py`, and
  `scripts/manuscript_variables.py` feed it numerical content from
  `src/` via `output/`.
- `docs/` is the technical reference — improvements and
  clarifications welcome.

## See also

- [`README.md`](README.md) — elevator pitch and current ground-truth snapshot
- [`docs/README.md`](docs/README.md) — documentation hub
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — per-round revision history
- [`docs/FAQ.md`](docs/FAQ.md) — common questions
- [`docs/READING_ORDER.md`](docs/READING_ORDER.md) — curated reading paths
- [`manuscript/INDEX.md`](manuscript/INDEX.md) — manuscript section index
- [`lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
  — witness-payload-discharge plan
- [`scripts/run_all.py`](scripts/run_all.py) — canonical default pipeline plus optional release subgates
- [`docs/reference/reproducibility_checklist.md`](docs/reference/reproducibility_checklist.md)
  — release/readiness gate and reviewer audit checklist
- [`docs/guides/styleguide.md`](docs/guides/styleguide.md) — manuscript ↔ code contract
- [`docs/reference/veridical_status.md`](docs/reference/veridical_status.md) — live audit page
