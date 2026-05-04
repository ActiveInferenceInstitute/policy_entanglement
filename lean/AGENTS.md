# AGENTS.md — `lean/`

Working notes for agents editing the Lean 4 boundary fragment.

## Constitution

1. **Mathlib-free.**  No `import Mathlib...` anywhere under
   `ActinfPolicyEntanglement/` or `FepSketches/`.  Mathlib refinement
   is a Phase 7 task — see
   [`../docs/reference/phase7_plan.md`](../docs/reference/phase7_plan.md).
2. **Pin: Lean 4 v4.29.0.**  Match `lean-toolchain` to the FEP_Lean
   release environment used elsewhere in the monorepo.
3. **Reserved tokens.**  Never use `Π` (binder for dependent products)
   or `λ` (binder for lambda) as identifiers.  Substitutes: `Pol`,
   `q_lam`, `lam`, `pi`.  This rule was load-bearing during the
   initial build — see commit history if you hit
   `expected token` parse errors.
4. **Cycle hygiene.**  `ActinfPolicyEntanglement.lean` (root) imports
   submodules under its own namespace only.  `FepSketches.lean`
   imports the boundary fragment to re-export it.  Never have the
   root import `FepSketches.*` — Lake will detect the cycle.
5. **Boundary-form sorries.**  Theorems whose analytic content
   depends on Mathlib (KL non-negativity, `Real.log` identities, SVD
   rank lemmas) are stated with `sorry` placeholders.  These are
   intentional and must remain until Phase 7.  Do not silence them
   with `axiom` or `set_option linter.unusedVariables false`.
6. **Token-level renames** (e.g. `Π` → `Pol`) must be applied
   consistently across every file that uses the symbol.  Use the
   helper script in commit history for guidance, or `sed -i`
   carefully.
7. **`lake build` must stay green.**  A build break blocks every
   downstream consumer (FepSketches, manuscript, future Mathlib
   refinement pass).  Run before commit.

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

## Refining a sorry away (Phase 7)

When Mathlib is wired in:
1. Add the appropriate `import Mathlib...` line.
2. Replace `Float` with `ℝ` (`Real`) and `0.0`/`1.0` stub bodies with
   real numeric content.
3. Replace `sorry` with the genuine proof.
4. Update [`docs/reference/lean_reference.md`](../docs/reference/lean_reference.md) to
   move the theorem out of the "boundary form" column.
5. Mirror the test in `tests/test_<module>.py` (the Python suite already
   verifies the analytic content numerically — it's a sanity rail for
   the Lean proof).

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `expected token` at a `Π` | reserved binder | rename to `Pol` |
| `unexpected token 'λ'` in identifier | reserved binder | rename to `lam` |
| `failed to generate Inhabited instance` | derived `Inhabited` on a struct whose fields lack instances | drop `deriving Inhabited` |
| `bad import` between Actinf and FepSketches | cycle | remove the cross-import |
| `no such file or directory` for a `globs` entry | Lake glob references a missing top-level file | create the top-level shim or remove the glob |
