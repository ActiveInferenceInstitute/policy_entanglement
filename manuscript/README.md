# `manuscript/` — Modular markdown sections

Each markdown file here corresponds to a numbered section of the
companion paper "Policy Entanglement in Active Inference".  The
template's PDF rendering pipeline concatenates them in lexical order to
produce the final PDF.

## File map

| File | Section / Title |
|---|---|
| [`config.yaml`](config.yaml) | Paper metadata (title, authors, DOI, keywords, LLM toggles) |
| [`preamble.md`](preamble.md) | LaTeX packages and theorem environments |
| [`00_abstract.md`](00_abstract.md) | Abstract |
| [`01_motivation_and_position.md`](01_motivation_and_position.md) | §1 Motivation and Position |
| [`02_setup_and_assumptions.md`](02_setup_and_assumptions.md) | §2 Setup, Notation, Standing Assumptions |
| [`02a_notation_glossary.md`](02a_notation_glossary.md) | §2a Notation Glossary (unified symbol reference) |
| [`03_lambda_deformation.md`](03_lambda_deformation.md) | §3 The λ-Deformation: Coupling Mean-Field Toward Joint Structure |
| [`04_entanglement_decomposition.md`](04_entanglement_decomposition.md) | §4 The Entanglement Decomposition Theorem (Theorem 4.1) |
| [`05_examples_and_worked_cases.md`](05_examples_and_worked_cases.md) | §5 Examples and Worked Cases |
| [`06_information_geometry.md`](06_information_geometry.md) | §6 Information Geometry of the Entanglement Manifold |
| [`07_spectral_and_tensor_network.md`](07_spectral_and_tensor_network.md) | §7 Spectral and Tensor-Network Structure |
| [`08_heterogeneous_inference.md`](08_heterogeneous_inference.md) | §8 Coupled Updates and Heterogeneous Inference (Theorem 8.1) |
| [`09_phase_structure.md`](09_phase_structure.md) | §9 Phase Structure and Symmetry Breaking |
| [`10_comparative_statics.md`](10_comparative_statics.md) | §10 Comparative Statics: When Does Coupling Pay? |
| [`11_connections_to_existing_frameworks.md`](11_connections_to_existing_frameworks.md) | §11 Connections to Existing Frameworks |
| [`12_lean_formalization_plan.md`](12_lean_formalization_plan.md) | §12 Lean Formalization Plan |
| [`13_empirical_simulation_suite.md`](13_empirical_simulation_suite.md) | §13 Empirical / Simulation Suite |
| [`14_open_theoretical_questions.md`](14_open_theoretical_questions.md) | §14 Open Theoretical Questions |
| [`15_companion_paper_outline.md`](15_companion_paper_outline.md) | §15 Manuscript Outline for the AII Companion Paper |
| [`16_discussion_worldview.md`](16_discussion_worldview.md) | §16 Discussion: The Worldview |
| [`17_closing_remarks.md`](17_closing_remarks.md) | §17 Closing |
| [`S01_proof_of_decomposition_theorem.md`](S01_proof_of_decomposition_theorem.md) | Appendix A — Full Proof of Theorem 4.1 |
| [`S02_convexity_of_free_energy.md`](S02_convexity_of_free_energy.md) | Appendix B — Convexity of `F[q_λ]` in `λ` |
| [`S03_bernoulli_complete_derivation.md`](S03_bernoulli_complete_derivation.md) | Appendix C — K=2 Bernoulli Complete Derivation |
| [`S04_tensor_train_inference_algorithm.md`](S04_tensor_train_inference_algorithm.md) | Appendix D — Tensor-Train Inference Algorithm Sketch |
| [`S05_lean_code_skeleton.md`](S05_lean_code_skeleton.md) | Appendix E — Lean Code Skeleton |
| [`99_bibliography.md`](99_bibliography.md) | Bibliography |

## Authoring conventions

* **Cross-reference Lean modules.**  When a section formally states or
  motivates a Lean theorem, link to the file under
  [`../lean/ActinfPolicyEntanglement/`](../lean/ActinfPolicyEntanglement/).
* **Cross-reference figures.**  Manuscript figures are produced by
  [`../scripts/generate_figures.py`](../scripts/generate_figures.py)
  and [`../scripts/simulate_pymdp.py`](../scripts/simulate_pymdp.py)
  and end up at `../output/figures/*.png`.  Embed them with the
  registry token `[[FIG:label]]` (where `label` is a key under
  `figures:` in [`refs/labels.yaml`](refs/labels.yaml)) — the
  injection pipeline substitutes the full Markdown image directive
  with the registered caption.  Inline cross-references use
  `[[FIGREF:label]]`.
* **Manuscript variables.**  In-text variable substitutions use
  the `[[VAR:key]]` or `[[VAR:key:fmt]]` token, where `key` is a
  field in [`../output/data/manuscript_variables.json`](../output/data/manuscript_variables.json)
  emitted by [`../scripts/manuscript_variables.py`](../scripts/manuscript_variables.py).
* **Citations.**  Use Pandoc-style `[@citekey]` referring to entries
  in [`refs/citations.yaml`](refs/citations.yaml); the bibliography
  body of [`99_bibliography.md`](99_bibliography.md) is auto-generated
  from the same source via `[[CITELIST:all]]`.
* **Determinism.**  Don't paste random numbers from notebooks; cite a
  scripted figure or a manuscript variable.

## Source-of-truth note

The modular markdown sections in this directory are the **canonical**
manuscript.  They are concatenated in lexical order by the template
PDF rendering pipeline.

## Building the PDF

The template-pipeline rendering job concatenates these files via
`infrastructure/rendering/pdf_renderer.py`.  Locally:

```bash
cd ../..   # back to template root
./run.sh --project actinf_policy_entanglement_lean --pipeline
```
