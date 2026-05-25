# Manuscript Syntax Reference (`actinf_policy_entanglement_lean`)

Project-specific overlay on [`docs/guides/styleguide.md`](../docs/guides/styleguide.md). Read that file first; this document describes the **registry-backed token system** used in this project.

## Token families

| Token pattern | Purpose | Source |
|---|---|---|
| `VAR` token (`key`, optional `:fmt`) | Numeric and string values from live runs | `output/data/manuscript_variables.json` via `src/simulation/hyperparameters.py` |
| `FIG` / `FIGREF` token (`label`) | Registered figures with provenance captions | `manuscript/refs/labels.yaml` |
| `EQ` / `EQREF` token (`label`) | Display equations (auto-numbered at render) | `manuscript/refs/labels.yaml` |
| `SEC` / `SECREF` token (`label`) | Section cross-references | `manuscript/refs/labels.yaml` |
| `THM` / `THMREF` token (`label`) | Theorem labels and references | `manuscript/refs/labels.yaml` |
| `LEAN` token (`label`) | Live Lean source excerpts | `lean/ActinfPolicyEntanglement/*.lean` via `src/manuscript/lean_extract.py` |
| Pandoc citekey (`@citekey`) | Bibliography entries | `manuscript/refs/citations.yaml` → generated `output/manuscript/references.bib` |
| CITELIST token (`all`) | Auto-built bibliography section | `scripts/inject_manuscript_variables.py` |

Authoring uses double-bracket delimiters around each family name and label (for example: open-bracket open-bracket, `VAR`, colon, `key`, close-bracket close-bracket).

## Authoring rules

1. **No hardcoded numeric literals** in prose, captions, or registry titles when a variable token exists in `hyperparameters.py`.
2. **No hand-typed section or theorem numbers** — use section-reference and theorem-reference tokens.
3. **Figures must exist** under `output/figures/` before validation passes; paths are registry-backed.
4. Rendered manuscript lives under `output/manuscript/`; do not edit injected copies by hand.

## Pipeline

```bash
# Variable mirror
uv run python scripts/manuscript_variables.py

# Token injection + equation auto-numbering
uv run python scripts/inject_manuscript_variables.py

# Combined PDF (project-local renderer, not template 03_render_pdf.py)
uv run python scripts/build_pdf.py
```

Full release path: `uv run python scripts/run_all.py --with-pdf` or `make pipeline-pdf`.

## Claim strength and theorem registry fields

Theorem rows in [`refs/labels.yaml`](refs/labels.yaml) carry `status:` (`proved`, `boundary`, `witness`, `forwarder`, `roadmap`, …) and optional `faithfulness:` (`substantive`, `typed-witness`, `numerical_corroboration_only`, …). Prose must respect those tiers — see [`docs/reference/methods_and_assumptions.md`](../docs/reference/methods_and_assumptions.md) §3 and the claim-strength legend at [[SECREF:app.claim_strength]].

| Label | Meaning in this project |
|---|---|
| `proved` | Machine-checked boundary or Mathlib-analytic row at the registered strength |
| `witness` / `boundary` | Typed Lean shell; analytic payload may be external or Mathlib-discharge |
| `forwarder` | Structural alias / geodesic forwarder without standalone analytic proof |
| `roadmap` | Planned work with artifact hooks but no promotion claim (e.g. Float↔ℝ bridge) |
| `empirical` | Script-generated sidecar validated by CSV/JSON/PNG gates |

## Roadmap vs `[[LEAN:]]` rows

`[[LEAN:…]]` injects live source from `lean/ActinfPolicyEntanglement/` when the registry row names a `lean_module` / `lean_name`. **Roadmap** rows (such as `roadmap_float_real_residual`) may ship witness shells and JSON sidecars (`output/reports/float_real_residual.json`) without upgrading abstract claim strength.

## Float residual artifact

The Float↔ℝ scaffold writes `output/reports/float_real_residual.json` and registers `FloatRealResidualWitness.lean`. Dashboard invariants bind the executable Float pipeline numerically; the formal bridge remains roadmap-tier until Q14 discharge.

## File naming

Body sections use `<part><letter>_*.md` (e.g. `2D_decomposition.md`); supplements use `S0N_*.md`; abstract is `0A_abstract.md`. Ordering is driven by [`manuscript/refs/labels.yaml`](refs/labels.yaml) and regenerated [`INDEX.md`](INDEX.md).

## See also

- [`manuscript/AGENTS.md`](AGENTS.md) — prose + registry rules
- [`manuscript/refs/labels.yaml`](refs/labels.yaml) — single source of truth for labels
- [`../src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py) — numeric source of truth
