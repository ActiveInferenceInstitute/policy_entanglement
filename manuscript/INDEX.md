# Manuscript Table of Contents

Authoritative section ordering, **auto-generated** from [`refs/labels.yaml`](refs/labels.yaml) by [`../scripts/generate_index.py`](../scripts/generate_index.py).  Do not hand-edit — modify the registry instead.

The manuscript is organized into six parts (Introduction, Theory, Formal Verification, Empirical Grounding, Connections, and Discussion).  Each body file uses a `<digit><letter>_*` prefix (e.g. `2D_decomposition.md`) so the renderer's lexical-sort discovery places it correctly within its part; supplementary appendices use an `S0N_*` prefix.

| File | Title | Subject |
|---|---|---|
| [`preamble.md`](preamble.md) | Preamble | LaTeX preamble + author front-matter |
| [`00_abstract.md`](00_abstract.md) | Abstract | _(part divider — unnumbered)_ |
| [`0A_abstract.md`](0A_abstract.md) | Abstract | _(part divider — unnumbered)_ |
| [`1A_part1_introduction.md`](1A_part1_introduction.md) | Part I — Introduction | _(part divider — unnumbered)_ |
| [`1B_motivation.md`](1B_motivation.md) | §1 Motivation and Position: Why Multi-Stream Active Inference Needs Parametric Coupling | Problem statement, six independent reasons, position relative to alternatives |
| [`1C_background_and_prior_work.md`](1C_background_and_prior_work.md) | §2 Background and Prior Work: Antecedents in Active Inference, Variational Coupling, Information Geometry, and Tensor Networks | Antecedents in active inference, variational coupling, information geometry, tensor networks |
| [`2A_part2_theory.md`](2A_part2_theory.md) | Part II — Theory | _(part divider — unnumbered)_ |
| [`2B_setup.md`](2B_setup.md) | §3 Setup and Standing Assumptions: Discrete-Time POMDP Active Inference, Single- and Multi-Stream | Single-stream POMDP recap; multi-stream extension; mean-field baseline |
| [`2C_lambda_deformation.md`](2C_lambda_deformation.md) | §4 The $\lambda$-Deformation: Coupling the Mean-Field Baseline Toward Arbitrary Joint Policy Structure | Coupling potentials, λ-entangled prior + posterior |
| [`2D_decomposition.md`](2D_decomposition.md) | §5 The Entanglement Decomposition Theorem: Variational Free Energy as Marginals + Coupling + Total Correlation | Theorem 5.1 (the load-bearing identity), verdicts, MF limit |
| [`2E_examples.md`](2E_examples.md) | §6 Examples and Worked Cases: K=2 Bernoulli Closed Form, Motor + Attention, and Multi-Timescale Coupling | K=2 Bernoulli toy, motor + attention example, multi-timescale |
| [`2F_geometry.md`](2F_geometry.md) | §7 Information Geometry of the Entanglement Manifold: Dual e/m-Flatness, $\lambda$-Family as e-Geodesic, and Pythagorean Decomposition | e/m flatness, m-projection, e-geodesic (Theorem 7.4), Pythagorean (Prop 7.5) |
| [`2G_spectral.md`](2G_spectral.md) | §8 Spectral and Tensor-Network Structure: Schmidt Decomposition, Archetypal Eigenvectors, and Tensor-Train Bond Dimensions for $K \geq 2$ | Schmidt decomposition, archetypes, tensor-train ranks (Theorem 8.3) |
| [`2H_heterogeneous.md`](2H_heterogeneous.md) | §9 Coupled Updates and Heterogeneous Inference: VFE / EFE Mixed Ensembles and the $O(\lambda^2)$ Coupling-Tax Bound | Three-level hierarchy, coupling tax (Theorem 9.1), precision-on-coupling |
| [`2I_phase_structure.md`](2I_phase_structure.md) | §10 Phase Structure and Symmetry Breaking: Disordered, Mixed, and Frozen Coupling Regimes with Behavioral Phenomenology | Disordered / mixed / frozen phases, order parameters, behavioral signatures |
| [`2J_comparative_statics.md`](2J_comparative_statics.md) | §11 Comparative Statics: When Does Coupling Pay? Sensitivity, Two-Parameter Generalization, and Potential-Structure Dependence | Coupling-pays-for-itself verdicts under parameter sweeps |
| [`3A_part3_formal_verification.md`](3A_part3_formal_verification.md) | Part III — Formal Verification | _(part divider — unnumbered)_ |
| [`3B_lean_formalization.md`](3B_lean_formalization.md) | §12 Lean 4 Formalization: Current Boundary, Witness Contracts, and Mathlib Scope | Boundary-fragment status table, witness payloads, MathlibProofs trajectory |
| [`4A_part4_empirical_grounding.md`](4A_part4_empirical_grounding.md) | Part IV — Empirical Grounding | _(part divider — unnumbered)_ |
| [`4B_empirical_suite.md`](4B_empirical_suite.md) | §13 Empirical Simulation Suite: Closed-Form Validation, Heterogeneous Coupling Tax, Phase Diagram, and Spectral Structure | Closed-form Bernoulli + heterogeneous tax + phase + spectral + e-geodesic + coupling graph; pymdp content split into §14–§16 |
| [`4C_pymdp_harness.md`](4C_pymdp_harness.md) | §14 pymdp 1.0.1 Grounded POMDP Harness: Layered Architecture, $\lambda$-Sweep, and Deterministic Coupled Rollout | pymdp 1.0.1 POMDP harness — layered architecture, λ-sweep, deterministic rollout |
| [`4D_pymdp_free_energy.md`](4D_pymdp_free_energy.md) | §15 pymdp Free-Energy Bundle: VFE / EFE / Entropy / Coupling-Term Observables and Auto-Injected Summary Statistics | Free-energy bundle — VFE / EFE / entropy / coupling-term / TC observables + 5 dashboards |
| [`4E_pymdp_validation.md`](4E_pymdp_validation.md) | §16 pymdp Validation, Structured JSONL Logging, and the Reproducibility Contract | Three-tier validation gate + JSONL run log + reproducibility contract |
| [`5A_part5_connections.md`](5A_part5_connections.md) | Part V — Connections to Existing Frameworks | _(part divider — unnumbered)_ |
| [`5B_connections_aif.md`](5B_connections_aif.md) | §17 Connections to Active Inference Frameworks: pymdp / SPM, Hierarchical / Deep AIF, Sophisticated Inference, and Branching-Time AIF | Classical AIF connections — pymdp / SPM, hierarchical / deep AIF, sophisticated inference, branching-time AIF |
| [`5C_connections_control_rl.md`](5C_connections_control_rl.md) | §18 Connections to Stochastic Control and Reinforcement Learning: KL / Path-Integral Control, Options, Products / Mixtures of Experts, and Copula VI | Control + RL connections — KL / path-integral control, options framework, PoE/MoE, copula VI |
| [`5D_connections_multi_agent.md`](5D_connections_multi_agent.md) | §19 Connections to Multi-Agent Inference, Renormalization-Group AIF, Markov Blankets, and CEREBRUM Case Grammar | Multi-agent + geometric connections — interactive inference, RG-AIF, Markov blankets, CEREBRUM |
| [`6A_part6_discussion.md`](6A_part6_discussion.md) | Part VI — Discussion and Outlook | _(part divider — unnumbered)_ |
| [`6B_open_questions.md`](6B_open_questions.md) | §20 Open Questions: Analytical, Identifiability, Empirical, Conceptual, and Practical | Q1–Q15: analytical, identifiability, empirical, conceptual, practical |
| [`6C_discussion_and_outlook.md`](6C_discussion_and_outlook.md) | §21 Discussion and Outlook: Worldview, Live Artifact State, and Limitations | Worldview, live artifact state, alignment implications, limitations, open directions |
| [`99_bibliography.md`](99_bibliography.md) | Bibliography | Auto-generated from [`refs/citations.yaml`](refs/citations.yaml) |

## Supplementary appendices

| File | Title | Subject |
|---|---|---|
| [`S01_proof_of_decomposition_theorem.md`](S01_proof_of_decomposition_theorem.md) | §A Full Proof of the Entanglement Decomposition Theorem | Full proof of Theorem 5.1 (entanglement decomposition) |
| [`S02_convexity_of_free_energy.md`](S02_convexity_of_free_energy.md) | §B Convexity of the Free Energy in $\lambda$: Sufficient Conditions and Counter-Example Construction | Convexity of $F[q_\lambda]$ in $\lambda$ |
| [`S03_bernoulli_complete_derivation.md`](S03_bernoulli_complete_derivation.md) | §C K=2 Bernoulli Toy: Complete Derivation of $I(\lambda)$, $\lambda^\star(\Delta)$, and the Closed-Form Free-Energy Curve | K=2 Bernoulli toy — complete derivation |
| [`S04_tensor_train_inference_algorithm.md`](S04_tensor_train_inference_algorithm.md) | §D Tensor-Train Inference Algorithm Sketch: Bond-Dimension Sweep and Sparsity-Rank Trade-Off | Tensor-train inference algorithm sketch |
| [`S05_lean_code_skeleton.md`](S05_lean_code_skeleton.md) | §E Lean 4 Boundary Fragment: Live Source Excerpts and Validation Wiring | Lean code skeleton (registry-backed submodule count; witness contracts) |
| [`S06_notation_and_concordance.md`](S06_notation_and_concordance.md) | §S6 Notation Concordance: Symbol Registry Across Manuscript, LaTeX, Python, and Lean | Symbol-by-symbol reference for the body and appendices |
| [`S07_reference_tables.md`](S07_reference_tables.md) | §S7 Reference Tables: Claim Strength, Variant Recovery, Lean Inventory, pymdp Bundle Statistics, and JSONL Run-Log Schema | Lean module inventory, pymdp bundle stats, JSONL run-log schema |
| [`S08_gnn_generalized_notation_extension.md`](S08_gnn_generalized_notation_extension.md) | §S8 GNN as a Shipped Fifth Track: Triple-Play Mapping, a Verified K=2 Bernoulli Round-Trip, and a Lean Typed-Contract Emitter |  |

## Registry directory ([`refs/`](refs/))

| File | Purpose |
|---|---|
| [`refs/labels.yaml`](refs/labels.yaml) | Single source of truth for every figure, equation, **section**, and **theorem** referenced via `[[FIG:...]]` / `[[EQ:...]]` / `[[SEC:...]]` / `[[THM:...]]` tokens |
| [`refs/citations.yaml`](refs/citations.yaml) | Single source of truth for every Pandoc-style citation token |
| [`refs/README.md`](refs/README.md) | How the registry feeds the auto-injection pipeline |

## Render the manuscript

```bash
uv run python scripts/manuscript_variables.py        # JSON of every numeric value
uv run python scripts/inject_manuscript_variables.py # resolves all tokens, auto-numbers eqs
uv run python scripts/validate_manuscript.py         # gates: tokens, citations, ranges
uv run python scripts/generate_index.py              # refresh this file
```

## Authoring rules — required reading

The manuscript ↔ code contract is documented in [`../docs/guides/styleguide.md`](../docs/guides/styleguide.md):

* every numeric value reaches the prose via `[[VAR:key]]` (no hardcoded numbers);
* every figure is registered in [`refs/labels.yaml`](refs/labels.yaml) with a caption that names the generation method + grid hyperparameter;
* every display equation is auto-numbered as `S.K`; cross-refs use `[[EQ:label]]` / `[[EQREF:label]]`;
* every `[@citekey]` resolves through [`refs/citations.yaml`](refs/citations.yaml);
* simulation hyperparameters live in [`../src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py) — never as a literal in a script or in prose.
