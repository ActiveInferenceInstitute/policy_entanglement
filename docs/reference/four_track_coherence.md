# Four-Track Coherence: how prose ↔ equations ↔ code ↔ Lean stay in lockstep

A "show, not tell" reference for the auto-injection contract that
keeps the manuscript, the equation registry, the Python numerical
companions, and the Lean boundary fragment from drifting apart.

*Latest generated audit.* The registry has
**21 theorem entries** with status breakdown **11 witness / 5 proved /
0 deferred / 0 sketch / 1 forwarder / 3 boundary / 1 roadmap** (round 3 graduated
the four remaining `deferred` theorems to `witness` and the two
remaining `sketch` rows to `proved` — see "Round-3 witness
graduations" below). **`status: proved` is not "proved as named":** of
the 5 `proved` rows, only 2 are `substantive` (`cor_4_2`, `cor_4_3`)
and 3 are `statement-restricted` (`prop_6_1` proves membership not
e-flatness; `prop_6_2` a conditional KL equality not minimality;
`prop_7_1` an `Iff.rfl` unfolding not the Schmidt-rank equivalence) —
see the `faithfulness:` field in `manuscript/refs/labels.yaml` and the
per-row audit in
[`veridical_status.md`](veridical_status.md). All other counts and
validation-gate counts are sourced from the latest generated readiness
artifacts.

## Why this matters

The thesis of the project is that policy entanglement is *one*
mathematical object expressible in four registers — natural-language
prose, LaTeX equations, executable Python, and machine-checked Lean.
A reader (human or LLM) should be able to start in any register and
land in any other in a single hop.

If the four tracks could drift independently, the thesis would
collapse: the prose would refer to a theorem the Lean fragment never
states, the Lean fragment would prove a theorem the Python never
witnesses, and the Python numerics would be untethered to anything
written down. The four-track contract — and the CI gates that
enforce it — exist to make that drift impossible.

## The four tracks

| Track | Source of truth | Render path |
|---|---|---|
| 1. **Prose** (sectioned manuscript) | `manuscript/*.md` | rendered to `output/manuscript/*.md` and ultimately the PDF |
| 2. **Equations / labels** | `manuscript/refs/labels.yaml` and `manuscript/refs/citations.yaml` | injected into prose via `[[EQ:...]]`, `[[EQREF:...]]`, `[[FIG:...]]`, `[[THMREF:...]]`, `[[VAR:...]]`, `[[SECREF:...]]`, `[[LEAN:...]]`, Pandoc citation keys, and `[[CITELIST:...]]` |
| 3. **Python numerical companion** | `src/lean/*.py`, `src/simulation/*.py`, `src/visualizations/*.py` | tested under `tests/test_*.py`; numerical witnesses serialized to `output/data/manuscript_variables.json` |
| 4. **Lean boundary fragment** | `lean/ActinfPolicyEntanglement/*.lean` | live source extracted by `src/manuscript/lean_extract.py`, embedded into prose at render time via `[[LEAN:label]]` |

## Registry injection references

Every numeric value, equation, figure, theorem, section reference,
citation list, and Lean snippet that appears in the rendered manuscript
is resolved through one of these registry-backed references:

| Token | Resolves to | Source |
|---|---|---|
| `[[VAR:key]]` | Numerical scalar / list | `output/data/manuscript_variables.json` (produced by `scripts/manuscript_variables.py`) |
| `[[EQ:label]]` / `[[EQREF:label]]` | LaTeX display equation with auto-numbered tag | `manuscript/refs/labels.yaml::equations` |
| `[[FIG:label]]` / `[[FIGREF:label]]` | Image reference with caption | `manuscript/refs/labels.yaml::figures` (PNG produced by `scripts/generate_figures.py` or `scripts/simulate_pymdp.py`) |
| `[[THMREF:label]]` / `[[THM:label]]` | Theorem cross-reference with kind + number | `manuscript/refs/labels.yaml::theorems` |
| `[[LEAN:label]]` | Live Lean source snippet | `lean/ActinfPolicyEntanglement/<lean_module>.lean` resolved via `lean_module` / `lean_name` fields of the theorem registry |
| `[[SECREF:label]]` | Section number / link | `manuscript/refs/labels.yaml::sections` |
| `[@key]` / `[@k1; @k2]` / `[[CITELIST:topic]]` | Bibliography entry or topic list | `manuscript/refs/citations.yaml` |

A manuscript file containing a single hardcoded number or theorem
reference outside one of these tokens fails the CI gate immediately;
no value reaches the rendered PDF by hand.

## The orchestrator pipeline

`scripts/run_all.py` runs the live `SCRIPTS` table in the order below; each
stage produces inputs for the next.

```
0.  build_lean.py             → enforces 0 sorry / 0 axiom on lean/
1.  generate_figures.py       → output/figures/*.png  (every analytical figure)
2.  dump_archetypes.py        → output/data/ising_archetypes.csv
3.  parameter_sweep.py        → output/data/parameter_sweep.csv
4.  simulate_pymdp.py         → output/figures/pymdp_*.png + output/simulations/*.csv + JSONL log
5.  simulate_multi_k.py       → output/figures/multi_k_*.png + output/data/multi_k_summary.json  (round 3)
6.  simulate_long_horizon.py  → output/figures/long_horizon_*.png + output/data/long_horizon_summary.json  (round 3)
7.  simulate_revertibility.py → output/figures/revertibility_*.png + output/data/revertibility_summary.json  (round 3)
8.  simulate_robustness.py    → robustness / ablation / replicate CSVs, JSON summaries, and PNGs
9.  simulate_btai.py          → output/data/btai_baseline.json + BTAI figure
10. simulate_adversarial.py   → output/data/adversarial_sweep.json + adversarial figure
11. simulate_gnn.py           → GNN K=2 round-trip + Lean typed-contract emitter sidecars
12. manuscript_variables.py   → output/data/manuscript_variables.json (every [[VAR:...]] value)
13. build_dashboard.py        → output/web/dashboard.html + output/data/dashboard_payload.json
                                  + output/reports/dashboard_invariants.txt
14. generate_index.py         → manuscript/INDEX.md (auto-generated from registry)
15. generate_theorem_map.py   → docs/reference/_theorem_map.md (per-theorem four-track wiring)
16. inject_manuscript_variables.py
                              → output/manuscript/*.md   (every token resolved into rendered prose)
17. validate_outputs.py       → CI gate: every artifact present and well-formed
18. validate_manuscript.py    → CI gate: every token resolves, no hardcoded numbers,
                                 no British spellings, **four-track wiring is coherent**
19. regression_gate.py        → CI gate: test/coverage/invariant/Lean-budget drift
```

The project-local dispatcher is `scripts/run_all.py`. Parent template
tooling may delegate into this project, but the source of truth for this
project's stage list, manifest, and optional PDF / MathlibProofs gates
is the `SCRIPTS` table in `scripts/run_all.py`.

For the more detailed dependency narrative, including why
`manuscript_variables.py` runs after the empirical sidecar producers,
see [`methods_orchestration.md`](methods_orchestration.md).

## The four CI gates

The four-track contract is enforced by four CI gates, each independent:

1. **Lean budget gate** — `scripts/build_lean.py`: `lake build` succeeds, and the boundary fragment has 0 `sorry`, 0 `axiom`, 0 `unsafe`/`partial`/`noncomputable`.
2. **Test gate** — `pytest tests/ --cov=src --cov-fail-under=95`: every analytical helper, every simulation method, every visualization helper, every manuscript-track validator has a direct unit test, and the suite stays at ≥ 95 % coverage on `src/`.
3. **Output gate** — `scripts/validate_outputs.py`: every figure declared in `labels.yaml::figures` exists on disk; every CSV / JSON output has the expected schema.
4. **Manuscript gate** — `scripts/validate_manuscript.py`: every `[[VAR:...]]`, `[[EQ:...]]`, `[[FIG:...]]`, `[[THMREF:...]]`, `[[LEAN:...]]`, `[[SECREF:...]]`, Pandoc citation key, and `[[CITELIST:...]]` resolves; every relative link points at an existing file; every numeric variable lies inside a published expected range; **every theorem in the registry whose `lean_module` field is populated resolves to a real Lean declaration**; no hardcoded grid counts, seeds, rollout horizons, or empirical results bypass the variables JSON.

The fourth gate's last clause — the four-track wiring check — is the
"show, not tell" enforcement: if a registered theorem says
`lean_module: Decomposition, lean_name: entanglement_decomposition`,
then `lean/ActinfPolicyEntanglement/Decomposition.lean` must contain
a declaration named `entanglement_decomposition`, or the gate fails
and the manuscript will not ship.

## How the four tracks compose in practice

A reader following the entanglement-decomposition theorem (the
canonical example) traverses all four tracks:

1. **Prose** in
   [`manuscript/2D_decomposition.md`](../../manuscript/2D_decomposition.md)
   states the theorem in natural language with the registry token
   `[[THMREF:thm_4_1]]`.

2. **Equation** `[[EQ:tc_decomp]]` resolves to a registered LaTeX
   display block with auto-numbered tag (e.g. `(4.1)`) — a single
   source of truth in
   [`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml).

3. **Python companion**
   [`lean.decomposition.entanglement_decomposition_rhs`](../../src/lean/decomposition.py)
   computes the four-term split numerically. The companion is exercised
   by [`tests/test_decomposition.py`](../../tests/test_decomposition.py)
   on the K = 2 Ising toy at floating tolerance.

4. **Lean witness** `[[LEAN:thm_4_1]]` resolves at render time to
   [`Decomposition.entanglement_decomposition`](../../lean/ActinfPolicyEntanglement/Decomposition.lean)
   — the live Lean source, with the file path and line number printed
   in the inlined caption. The witness-consuming `structure` parameter
   is the API contract for the separate MathlibProofs refinement layer.

The same pattern repeats across the **20 Lean-backed theorem rows**;
the additional roadmap row resolves to the `FloatRealResidualWitness`
boundary scaffold but is not a theorem-proving claim. Round 3 closed
the four remaining `deferred` rows, so every manuscript theorem now
has a live Lean companion. The per-theorem
table in [`docs/reference/_theorem_map.md`](_theorem_map.md)
(auto-generated) lists every row in one place, and
[`docs/reference/manuscript_map.md`](manuscript_map.md) maps each row
to its surrounding section.

## Round-3 witness graduations

Round 3 of the manuscript revisions added two new Lean submodules
(`SpectralWitnesses.lean`, `ConnectionsWitnesses.lean`) and graduated
all four remaining `deferred` rows to `witness`; round 3 also
graduated the two `sketch` rows (`cor_4_2`, `prop_6_1`) to `proved`:

| Registry label | Manuscript | New Lean witness | Witness structure (round 3) |
|---|---|---|---|
| `prop_7_2` | Proposition 8.2 — Schmidt rank upper-semicontinuous in λ | [`SpectralWitnesses.schmidtRank_upperSemicontinuous_witness`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) | `UpperSemicontinuousRankWitness {rank_at_zero, usc}` |
| `thm_7_3` | Theorem 8.3 — Sparsity-rank tradeoff | [`SpectralWitnesses.sparsityRank_tradeoff_witness`](../../lean/ActinfPolicyEntanglement/SpectralWitnesses.lean) | `SparsityRankEnvelope {cut_rank, bond_bound, envelope}` |
| `thm_11_1` | Theorem 17.1 — Hierarchical AIF as λ → ∞ limit | [`ConnectionsWitnesses.hierarchicalAIF_lambda_limit_witness`](../../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) | `HierarchicalConcentrationWitness {concentrate}` |
| `prop_11_2` | Proposition 17.2 — Sophisticated-inference embedding | [`ConnectionsWitnesses.sophisticatedInference_embedding_witness`](../../lean/ActinfPolicyEntanglement/ConnectionsWitnesses.lean) | `SophisticatedInferenceEmbedding {source, siValue, embed, preserveVFE}` |
| `cor_4_2` | Corollary 5.2 — Coupling-pays-for-itself | [`Decomposition.couplingVerdict_correct`](../../lean/ActinfPolicyEntanglement/Decomposition.lean) | (no new structure — boundary `Bool` / `decide` identity) |
| `prop_6_1` | Proposition 7.1 — MF submanifold is e-flat | [`Geometry.mfImage_isMeanField`](../../lean/ActinfPolicyEntanglement/Geometry.lean) | (no new structure — label-only correction; existing proof) |

The two new round-3 submodules import only `Basic`, `JointDist`,
`Coupling`, and `FreeEnergy`, preserving the Mathlib-free guarantee.
Each witness structure ties its numerical fields to the
boundary-fragment primitives via threading (e.g.
`HierarchicalConcentrationWitness.concentrate` threads through `kl`)
so the statements remain non-vacuous.

After the round-5 Pythagorean tie-in upgrade, the boundary fragment
exposes **10 witness structures**:

* `BoundedQuadraticTax`, `SmallLambdaTolerance` in `Heterogeneous.lean` (round 1)
* `FreeEnergyConvexityWitness`, `LocalConcavityAtZero` in `Convexity.lean` (round 2)
* `MarkovBlanketSeparationWitness` in `MarkovBlanket.lean` (round 2)
* `UpperSemicontinuousRankWitness`, `SparsityRankEnvelope` in `SpectralWitnesses.lean` (round 3)
* `HierarchicalConcentrationWitness`, `SophisticatedInferenceEmbedding` in `ConnectionsWitnesses.lean` (round 3)
* `PythagoreanWitness` in `Geometry.lean` (round 5)

and **zero deferred theorems remain** (down from 7 originally → 4
after round 2 → 0 after round 3). The Mathlib-refinement plan in
[`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
now describes the Mathlib *payload-discharge* roadmap (moving each
`witness` row to `proved` by supplying its analytic content from
Mathlib).

## Anti-drift mechanisms

The contract hardens against four classes of drift:

| Drift | Detection | Effect on CI |
|---|---|---|
| Lean theorem renamed without updating registry | `validate_lean_wiring` (Manuscript gate, four-track wiring clause) | **fail** with explanation pointing at the missing `(module, name)` |
| Numerical value changed in code without updating variables JSON | `manuscript_variables.py` re-runs in pipeline; `[[VAR:...]]` re-injects fresh value; range-check gate fails if value escapes published range | **fail** when JSON value is outside the validator's `EXPECTED_RANGES` |
| Figure renamed in code without updating `labels.yaml::figures` | `[[FIG:label]]` token fails to resolve at render time | **fail** at manuscript validator |
| Hardcoded literal slipped into prose | `find_hardcoded_numeric_literals` scans for grid counts, seeds, rollout horizons, empirical decimals, K-ensemble references | **fail** at manuscript validator |

**Scope of this guarantee (RedTeam 2026-05-19 Cat-3b — stated
precisely, no over-claim).** Every inter-track touch point has a
CI-time witness, so *name-resolution* drift (a renamed/deleted
label/`lean_name`/token) cannot accumulate silently. This is **not**
content-parity verification: `validate_lean_wiring` /
`check_concordance` confirm the named Lean declaration *exists* in the
declared module — they do **not** prove the Lean statement and its
Python witness encode the same mathematics. For the witness/boundary
tier the Lean body is a hypothesis-reexport projection (the analytic
content is an assumed `structure` field — see each row's
`faithfulness: typed-witness` in `labels.yaml`), so a Python witness
that computed something *different* from the Lean obligation would
**not** be caught here. The honest characterisation is therefore
"machine-checked Python + name-checked Lean wiring (the proved-tier ℝ
proofs in `MathlibProofs` are the genuinely machine-checked
mathematics; the witness tier is a typed contract, not a proof)".
Per-witness content-conformance tests (the `prop_6_3` independent-route
test is the template) are the open hardening; the `faithfulness:`
field + its registry-wide enforcement (`scripts/manuscript_variables.py`,
`tests/test_h1_headline_invariant.py::test_every_registry_row_declares_faithfulness`)
is what now prevents the *strength* of a witness row being silently
over-stated.

## Adding a new theorem (or witness)

1. Add the analytic helper in `src/lean/<module>.py` and a direct
   test in `tests/test_<module>.py`. Helpful: aim for ≥ 95 % line
   coverage on the new helper.
2. State the theorem in Lean under `lean/ActinfPolicyEntanglement/<Module>.lean`
   in *witness form* if it depends on Mathlib content
   (KL chain rule, Bregman Taylor, real-analytic continuity, matrix
   outer-product rank). The boundary fragment must remain `sorry`-free.
3. Register the theorem in `manuscript/refs/labels.yaml::theorems`
   with `lean_module`, `lean_name`, and `status` fields.
4. Reference it in prose with `[[THMREF:label]]` and embed the live
   Lean source with `[[LEAN:label]]`. If the theorem has a numerical
   witness consumed in prose, expose the witness via
   `scripts/manuscript_variables.py::_<your>_facts` and reference it
   with `[[VAR:key]]`.
5. Run `uv run python scripts/validate_manuscript.py` — the four-track
   wiring gate verifies that every step above is consistent.

If any one of those five steps is missed, the manuscript validator
fails before a render reaches a reader. That is the contract.

## S08 and the GNN Bridge

[`S08_gnn_generalized_notation_extension.md`](../../manuscript/S08_gnn_generalized_notation_extension.md)
now ships Generalized Notation Notation (GNN) [Smékal & Friedman 2023]
as a **fifth structural-and-numerical representation**, not as a fifth
proof track. The shipped pieces are concrete and CI-covered:

1. a project-owned GNN v1.1 parser under `src/gnn/`;
2. a K=2 Bernoulli round-trip from `gnn/bernoulli_toy.gnn.md` that
   reconstructs the closed-form mutual-information curve;
3. a Lean typed-contract emitter that produces boundary-compatible
   structure declarations;
4. the `simulate_gnn.py` pipeline stage plus parser, round-trip, and
   concordance tests.

This does **not** amend the four-track proof contract above. GNN
reproduces structure and numbers; it proves no theorem, promotes no
registry theorem row, and leaves the first-class upstream coupling
primitive, full-bundle pymdp regeneration, and GNN-to-Lean proving
paths as explicit open work in S08.
