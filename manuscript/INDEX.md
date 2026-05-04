# Manuscript Table of Contents

Authoritative section ordering, **auto-generated** from [`refs/labels.yaml`](refs/labels.yaml) by [`../scripts/generate_index.py`](../scripts/generate_index.py).  Do not hand-edit — modify the registry instead.

The *physical* layout is intentionally flat: the parent template rendering pipeline concatenates files in alphanumeric order, so every body section uses a `00_…`–`17_…` prefix and every supplementary appendix uses an `S0N_…` prefix.

| File | Title | Subject |
|---|---|---|
| [`preamble.md`](preamble.md) | Preamble | LaTeX preamble + author front-matter |
| [`00_abstract.md`](00_abstract.md) | Abstract | One-page summary |
| [`01_motivation_and_position.md`](01_motivation_and_position.md) | §1 Motivation and Position | Problem statement, six independent reasons, position relative to alternatives |
| [`02_setup_and_assumptions.md`](02_setup_and_assumptions.md) | §2 Setup, Notation, and Standing Assumptions | Single-stream POMDP recap; multi-stream extension; mean-field baseline |
| [`02a_notation_glossary.md`](02a_notation_glossary.md) | §2a Notation Glossary | Symbol-by-symbol reference for the body and appendices |
| [`03_lambda_deformation.md`](03_lambda_deformation.md) | §3 The λ-Deformation | Coupling potentials, λ-entangled prior + posterior |
| [`04_entanglement_decomposition.md`](04_entanglement_decomposition.md) | §4 Entanglement Decomposition Theorem | Theorem 4.1 (the load-bearing identity), verdicts, MF limit |
| [`05_examples_and_worked_cases.md`](05_examples_and_worked_cases.md) | §5 Examples and Worked Cases | K=2 Bernoulli toy, motor + attention example, multi-timescale |
| [`06_information_geometry.md`](06_information_geometry.md) | §6 Information Geometry of the Entanglement Manifold | e/m flatness, m-projection, e-geodesic (Theorem 6.4), Pythagorean (Prop 6.5) |
| [`07_spectral_and_tensor_network.md`](07_spectral_and_tensor_network.md) | §7 Spectral and Tensor-Network Structure | Schmidt decomposition, archetypes, tensor-train ranks (Theorem 7.3) |
| [`08_heterogeneous_inference.md`](08_heterogeneous_inference.md) | §8 Coupled Updates and Heterogeneous Inference | Three-level hierarchy, coupling tax (Theorem 8.1), precision-on-coupling |
| [`09_phase_structure.md`](09_phase_structure.md) | §9 Phase Structure and Symmetry Breaking | Disordered / mixed / frozen phases, order parameters, clinical phenomenology |
| [`10_comparative_statics.md`](10_comparative_statics.md) | §10 Comparative Statics | Coupling-pays-for-itself verdicts under parameter sweeps |
| [`11_connections_to_existing_frameworks.md`](11_connections_to_existing_frameworks.md) | §11 Connections to Existing Frameworks | pymdp, hierarchical AIF, BTAI, KL control, options, PoE/MoE, copula VI, RG-AIF, CEREBRUM |
| [`12_lean_formalization_plan.md`](12_lean_formalization_plan.md) | §12 Lean Formalization Plan | Phase 0 status table (16/16 jobs), Phase 1–7 roadmap |
| [`13_empirical_simulation_suite.md`](13_empirical_simulation_suite.md) | §13 Empirical / Simulation Suite | Closed-form numerics + pymdp 1.0.1 grounded harness, every figure |
| [`14_open_theoretical_questions.md`](14_open_theoretical_questions.md) | §14 Open Theoretical Questions | Q1–Q12 |
| [`15_companion_paper_outline.md`](15_companion_paper_outline.md) | §15 Companion Paper Outline | Future work tracked in a separate manuscript |
| [`16_discussion_worldview.md`](16_discussion_worldview.md) | §16 Discussion and Worldview | Implications |
| [`17_closing_remarks.md`](17_closing_remarks.md) | §17 Closing Remarks | Take-aways |
| [`99_bibliography.md`](99_bibliography.md) | §99 Bibliography | Auto-generated from [`refs/citations.yaml`](refs/citations.yaml) |
| [`S01_proof_of_decomposition_theorem.md`](S01_proof_of_decomposition_theorem.md) | §A Full proof of Theorem 4.1 | Full proof of Theorem 4.1 |
| [`S02_convexity_of_free_energy.md`](S02_convexity_of_free_energy.md) | §B Convexity of F[q_λ] | Convexity of $F[q_\lambda]$ |
| [`S03_bernoulli_complete_derivation.md`](S03_bernoulli_complete_derivation.md) | §C K=2 Bernoulli derivation | K=2 Bernoulli derivation |
| [`S04_tensor_train_inference_algorithm.md`](S04_tensor_train_inference_algorithm.md) | §D Tensor-train inference algorithm | Tensor-train inference algorithm |
| [`S05_lean_code_skeleton.md`](S05_lean_code_skeleton.md) | §E Lean code skeleton | Lean code skeleton |

## Registry directory ([`refs/`](refs/))

| File | Purpose |
|---|---|
| [`refs/labels.yaml`](refs/labels.yaml) | Single source of truth for every figure, equation, **section**, and **theorem** referenced via `[[FIG:...]]` / `[[EQ:...]]` / `[[SEC:...]]` / `[[THM:...]]` tokens |
| [`refs/citations.yaml`](refs/citations.yaml) | Single source of truth for every Pandoc-style citation token |
| [`refs/README.md`](refs/README.md) | How the registry feeds the auto-injection pipeline |

## Render the manuscript

```bash
uv run python scripts/manuscript_variables.py
uv run python scripts/inject_manuscript_variables.py
uv run python scripts/validate_manuscript.py
uv run python scripts/generate_index.py     # refresh this file
```
