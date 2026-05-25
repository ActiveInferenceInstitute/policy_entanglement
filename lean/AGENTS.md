# AGENTS.md — `lean/`

Working notes for agents editing the Lean 4 boundary fragment.

**Live state.** Counts and build status come from
`output/data/manuscript_variables.json` (`lean_*`, `theorem_registry_count`)
and `scripts/build_lean.py` / `output/reports/test_results.json` — do not
hard-code declaration totals here. The boundary fragment builds on the pin in
`lean/lean-toolchain` (currently Lean 4 v4.29.0). Per-theorem status lives in
[`docs/reference/veridical_status.md`](../docs/reference/veridical_status.md).
The additive MathlibProofs plan lives in
[`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md);
Lean coding style (file headers, naming, witness-form idiom, layering)
is in [`STYLE.md`](STYLE.md).

## Constitution

1. **Mathlib-free.**  No `import Mathlib...` anywhere under
   `ActinfPolicyEntanglement/` or `FepSketches/`.  Mathlib refinement
   is an additive MathlibProofs task — see
   [`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md).
2. **Pin: Lean 4 v4.29.0.**  Match `lean-toolchain` to the release pin
   used in
   [`ActiveInferenceInstitute/fep_lean`](https://github.com/ActiveInferenceInstitute/fep_lean)
   so template-side builds stay comparable.
3. **Reserved tokens.**  Never use `Π` (binder for dependent products)
   or `λ` (binder for lambda) as identifiers.  Substitutes: `Pol`,
   `q_lam`, `lam`, `pi`.  This rule was load-bearing during the
   initial build — see commit history if you hit
   `expected token` parse errors.
4. **Cycle hygiene.**  `ActinfPolicyEntanglement.lean` (root) imports
   submodules under its own namespace only.  `FepSketches.lean`
   imports the boundary fragment to re-export it.  Never have the
   root import `FepSketches.*` — Lake will detect the cycle.
5. **Witness-form theorems.**  Theorems whose analytic content
   depends on Mathlib (KL non-negativity, `Real.log` identities, SVD
   rank lemmas) are stated in *witness-consuming* form: the caller
   supplies the analytic witness and the boundary certifies the
   resulting decomposition without `sorry`.  The boundary fragment
   is currently zero-strict-`sorry`; do not introduce one — express
   any new analytic dependence as a witness argument instead.
6. **Token-level renames** (e.g. `Π` → `Pol`) must be applied
   consistently across every file that uses the symbol.  Use the
   helper script in commit history for guidance, or `sed -i`
   carefully.
7. **`lake build` must stay green.**  A build break blocks every
   downstream consumer (FepSketches, manuscript, separate MathlibProofs
   refinement pass).  Run before commit. Current expectation: **22/22
   jobs** (17 submodules + root + FepSketches re-export +
   `FepSketches.lean` hub + 1 manifest job, depending on Lake's
   internal accounting).

## Adding a new submodule

1. Create `ActinfPolicyEntanglement/Foo.lean` with header docstring
   matching the existing style.
2. Add `import ActinfPolicyEntanglement.Foo` to `ActinfPolicyEntanglement.lean`.
3. (Optional) Re-export load-bearing theorems via
   `FepSketches/PolicyEntanglementBoundary.lean`.
4. Mirror the concept in `src/foo.py` + `tests/test_foo.py` if the
   module has computable content.
5. Update [`README.md`](README.md) submodule index.
6. Run `lake build` and confirm green.

## Separate MathlibProofs Layer

The boundary is stable at zero strict `sorry` across all **17
submodules** (11 witness + 5 proved + 1 forwarder + 3 boundary
theorems wired to the manuscript). The `lean/MathlibProofs/` package is
separate from the boundary package and is independently checkable with
`uv run python scripts/build_mathlib_proofs.py`; only that layer may
import Mathlib. It now discharges the headline real-valued
free-energy decomposition through `free_energy_decomposition_full`.
Its remaining purpose is to discharge the analytic payloads of the
other witness/boundary rows
(`totalCorrelation_eq_kl_to_mprojection`,
`couplingTax_quadratic_bound`, `couplingTax_small_lambda_tolerance`,
`dualFlat_pythagorean_witness`, `freeEnergy_convex_in_lam_witness`,
`freeEnergy_localConcavity_at_zero_witness`,
`markovBlanket_separation_identity_witness`,
`schmidtRank_upperSemicontinuous_witness`, `sparsityRank_tradeoff_witness`,
`hierarchicalAIF_lambda_limit_witness`,
`sophisticatedInference_embedding_witness`).  See
[`ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
for the layered import / discharge plan.  Procedure:

1. Create `lean/MathlibProofs/<Module>.lean` and add it as a separate
   Lake library target in `lakefile.lean`.
2. `import Mathlib...` *only there*.
3. Provide the analytic witness using
   `Mathlib.Probability.Entropy.Basic`,
   `Mathlib.Analysis.SpecialFunctions.Log.Basic`, etc.
4. Forward the boundary theorem with the discharged witness.
5. Update [`docs/reference/lean_reference.md`](../docs/reference/lean_reference.md)
   to mark the witness as discharged.
6. Mirror in Python tests (`tests/test_<module>.py`) — the Python
   suite is the numerical sanity rail.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `expected token` at a `Π` | reserved binder | rename to `Pol` |
| `unexpected token 'λ'` in identifier | reserved binder | rename to `lam` |
| `failed to generate Inhabited instance` | derived `Inhabited` on a struct whose fields lack instances | drop `deriving Inhabited` |
| `bad import` between Actinf and FepSketches | cycle | remove the cross-import |
| `no such file or directory` for a `globs` entry | Lake glob references a missing top-level file | create the top-level shim or remove the glob |
