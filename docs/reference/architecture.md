# Architecture

*Latest generated audit.*

## Two layers, executable tracks

The project sits inside the [`docxology/template`](https://github.com/docxology/template)
research-template repository, which separates *generic* infrastructure
from *project-specific* code (the **two-layer** architecture).  Within
this project, the executable core has two primary tracks — a Lean 4
boundary fragment and a Python numerical companion — with manuscript,
documentation, registry, figure, and GNN bridge surfaces tied back to
those tracks by validation gates.

**Layer-2 totals (current local audit).** 17 Lean submodules under
`lean/ActinfPolicyEntanglement/` build under 22 `lake` jobs, exposing
76 public theorems / lemmas, 39 `def`s, and 11 witness `structure`s
for 126 declarations total. The boundary fragment is `sorry`-free, axiom-free,
Mathlib-import-free, and `unsafe`/`partial`/`noncomputable`-free. Round 2
added the `Convexity` and `MarkovBlanket` submodules; round 3 added
`SpectralWitnesses` and `ConnectionsWitnesses`, graduating the four
remaining `deferred` theorems (Prop 8.2 Schmidt-rank
upper-semicontinuity, Thm 8.3 sparsity-rank tradeoff, Thm 17.1
hierarchical AIF λ→∞ limit, Prop 17.2 sophisticated-inference
embedding) to `witness` status.  Zero deferred theorems remain.

```
┌────────────────────────── repository (Layer 1) ─────────────────────────────┐
│  infrastructure/          generic build / validate / render tools           │
│  scripts/                 entry-point orchestrators (00–07)                 │
│  tests/infra_tests/       infrastructure test suite                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────── projects/actinf_policy_entanglement_lean/ (Layer 2) ────────────────┐
│                                                                             │
│   ┌──────── Lean 4 track ───────┐    ┌────── Python track ────────┐         │
│   │ lean/ActinfPolicyEntangle.. │    │ src/        — pure compute │         │
│   │   Mathlib-free; types &     │    │ tests/      — no mocks     │         │
│   │   theorem statements        │◄──►│ scripts/    — thin orch.   │         │
│   │ lean/FepSketches/           │    │                            │         │
│   │   re-exports for fep_lean layout │    │                            │         │
│   └─────────────────────────────┘    └────────────────────────────┘         │
│                                                                             │
│   manuscript/        modular markdown sections + config + preamble          │
│   docs/              technical documentation (this directory)               │
│   output/            disposable, regenerable artifacts                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Layer 1: infrastructure (template-wide, generic)

Shared with every project under `projects/`:

* `infrastructure.config` — repository-wide configuration loader.
* `infrastructure.core` — logging, exceptions, file ops, pipeline,
  telemetry, security.
* `infrastructure.documentation` — figure / API / glossary management.
* `infrastructure.llm` — local Ollama integration (optional).
* `infrastructure.project` — multi-project discovery (this is what
  picks us up under `projects/`).
* `infrastructure.publishing` — DOI, citations, Zenodo, arXiv.
* project-local `scripts/build_pdf.py` — Markdown → combined PDF via
  Pandoc/XeLaTeX/BibTeX.
* project-local `reporting.interactive_dashboard` — dashboard panels,
  controls, invariant records, and plaintext witness reports.
* `infrastructure.scientific` — best-practice helpers (RNG, stability).
* `infrastructure.steganography` — cryptographic PDF watermarking.
* `infrastructure.validation` — PDF / output / markdown checks.

## Layer 2: this project (domain-specific)

Everything under
`projects/actinf_policy_entanglement_lean/`:

* **Lean track** — [`../lean/`](../../lean/), Mathlib-free.
* **Python track** — [`../src/`](../../src/) + [`../tests/`](../../tests/) +
  [`../scripts/`](../../scripts/).
* **Manuscript / registry track** — [`../manuscript/`](../../manuscript/).
* **GNN bridge** — [`../../gnn/`](../../gnn/) +
  [`../../src/gnn/`](../../src/gnn/), a structural-and-numerical fifth
  representation rather than a theorem-proving track.
* **Docs** — this directory.
* **Outputs** — [`../output/`](../../output/) (disposable).

### Lean submodule inventory (17 files, 22 lake jobs)

| Module | Purpose |
|---|---|
| `Basic` | Stream / policy index types, decidability instances |
| `Scalar` | `CommScalar` ring-law typeclass (Mathlib-free algebra) |
| `JointDist` | Joint / mean-field PMF arithmetic |
| `Coupling` | λ-deformation: `couplingLogWeight`, `entangledPosteriorLogWeight` |
| `FreeEnergy` | `shannonEntropy`, `kl`, `totalCorrelation`, `variationalFreeEnergy` |
| `Geometry` | e/m-flatness, e-geodesic, Pythagorean witness (Prop 7.1–7.5) |
| `Spectral` | Bipartite Schmidt factorization (Prop 8.1 ⇔) |
| `Heterogeneous` | `BoundedQuadraticTax` / `SmallLambdaTolerance` (Thm 9.1, Cor 9.2) |
| `BernoulliToy` | K=2 closed-form Ising MI, free-energy curve, phase classifier |
| `Decomposition` | Theorem 5.1 + corollaries 5.2–5.4 + Thm 5.5 witness; round-3 `couplingVerdict_correct` Cor 5.2 boundary identity |
| `Constructive` | `CommScalar`-polymorphic substantive `= 0` lemmas |
| `Monotonicity` | Constructive `Nat`/`Or`/`List`/`Fin` lemmas |
| **`Convexity`** (round 2) | Thm 5.6 (convexity of F in λ) + Prop 11.1 (local concavity at λ=0), both witness-form |
| **`MarkovBlanket`** (round 2) | Prop 19.3 Markov-blanket separation identity `sep = 1 − I(q)/H(q)`, witness-form |
| **`SpectralWitnesses`** (round 3) | Prop 8.2 (Schmidt rank upper-semicontinuous in λ) + Thm 8.3 (sparsity-rank tradeoff), both witness-form |
| **`ConnectionsWitnesses`** (round 3) | Thm 17.1 (hierarchical AIF as λ→∞ limit) + Prop 17.2 (sophisticated-inference embedding), both witness-form |
| `FloatRealResidualWitness` | Typed numerical-to-real residual witness boundary for finite-precision audit rows |

`lean/FepSketches/PolicyEntanglementBoundary.lean` re-exports the
boundary fragment under the `fep_lean` catalog layout; this is part of
what the build expands into the 22 lake jobs.

### Cross-track invariant

For every concept that appears in
[`../lean/ActinfPolicyEntanglement/<Module>.lean`](../../lean/ActinfPolicyEntanglement/),
there is a sibling `src/<module>.py` that *actually computes* it on
finite ndarrays, and a `tests/test_<module>.py` that exercises the
mathematical property to floating tolerance.

This is the *sanity rail*: when a witness payload is later discharged
via Mathlib, or when the existing headline Mathlib proof is compared
against the Float pipeline, the Python test suite has already verified
the analytic content numerically, so the proof and the implementation
cannot silently diverge.

## Thin orchestrator pattern

Scripts are *coordinators*, not *implementations*:

```python
# scripts/generate_figures.py (illustrative)
from lean.coupling import entangled_posterior       # logic in src/
from lean.spectral import schmidt_rank
import matplotlib.pyplot as plt

q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=2.0)
plt.plot(...); plt.savefig(out)
print(out)
```

If a script grows a function that *computes* something rather than
*moves data around*, that function should be lifted into `src/`.

## Output policy

* `output/` is **disposable**: every file in it can be regenerated
  by re-running the corresponding script.
* `output/figures/` — manuscript figures (PNG, 300 dpi).
* `output/data/` — JSON / CSV variable substitutions for the
  rendering pipeline.
* `output/` is **never** committed (matches the parent repository's
  `.gitignore`).

## Python library packages (beyond the four domain subpackages)

| Package | Role |
|---|---|
| `src/gates/` | Regression gate library (`regression_gate.py`); consumed by `scripts/regression_gate.py` |
| `src/orchestration/` | Pipeline runner (`run_all.py`) and PDF renderer (`build_pdf.py`) |
| `src/lean/build_gate.py` | Lean build + hygiene scanners; consumed by `scripts/build_lean.py` |
| `src/manuscript/output_gates/` | Release artifact validators; consumed by `scripts/validate_outputs.py` |
| `src/dashboard_types/` | Shared dashboard datatypes for `lean/invariants.py` and `reporting/` |

## Pinned versions

* Lean: `leanprover/lean4:v4.29.0` (matches the `fep_lean` catalog pin).
* Python: `>= 3.10` (matches the parent template).
* numpy: `>= 1.24`, scipy: `>= 1.10`, matplotlib: `>= 3.7`.
