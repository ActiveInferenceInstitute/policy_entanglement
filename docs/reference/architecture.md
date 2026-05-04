# Architecture

## Two layers, two tracks

The project sits inside the [`docxology/template`](https://github.com/docxology/template)
research-template repository, which separates *generic* infrastructure
from *project-specific* code (the **two-layer** architecture).  Within
this project, we further split the project-specific code into **two
tracks**: a Lean 4 boundary fragment and a Python numerical companion.

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
│   │   re-exports for FEP_Lean   │    │                            │         │
│   └─────────────────────────────┘    └────────────────────────────┘         │
│                                                                             │
│   manuscript/        modular markdown sections + config + preamble          │
│   docs/              technical documentation (this directory)               │
│   output/            disposable, regenerable artefacts                      │
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
* `infrastructure.rendering` — markdown → PDF / HTML / slides.
* `infrastructure.reporting` — pipeline reporting and error aggregation.
* `infrastructure.scientific` — best-practice helpers (RNG, stability).
* `infrastructure.steganography` — cryptographic PDF watermarking.
* `infrastructure.validation` — PDF / output / markdown checks.

## Layer 2: this project (domain-specific)

Everything under
`projects/actinf_policy_entanglement_lean/`:

* **Lean track** — [`../lean/`](../../lean/), Mathlib-free.
* **Python track** — [`../src/`](../../src/) + [`../tests/`](../../tests/) +
  [`../scripts/`](../../scripts/).
* **Manuscript** — [`../manuscript/`](../../manuscript/).
* **Docs** — this directory.
* **Outputs** — [`../output/`](../../output/) (disposable).

### Cross-track invariant

For every concept that appears in
[`../lean/ActinfPolicyEntanglement/<Module>.lean`](../../lean/ActinfPolicyEntanglement/),
there is a sibling `src/<module>.py` that *actually computes* it on
finite ndarrays, and a `tests/test_<module>.py` that exercises the
mathematical property to floating tolerance.

This is the *sanity rail*: when a Lean `sorry` is later discharged
via Mathlib, the Python test suite has already verified the analytic
content numerically, so the proof and the implementation cannot
silently diverge.

## Thin orchestrator pattern

Scripts are *coordinators*, not *implementations*:

```python
# scripts/generate_figures.py (illustrative)
from coupling import entangled_posterior            # logic in src/
from spectral import schmidt_rank
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

## Pinned versions

* Lean: `leanprover/lean4:v4.29.0` (matches the FEP_Lean release env).
* Python: `>= 3.10` (matches the parent template).
* numpy: `>= 1.24`, scipy: `>= 1.10`, matplotlib: `>= 3.7`.
