# AGENTS.md — `tests/lean/`

Tests that exercise the Lean 4 boundary fragment under
[`../../lean/`](../../lean/) from Python — building, hygiene budget,
and structural sanity.

## Files

| File | Coverage |
|---|---|
| `test_lean_build.py` | End-to-end `lake build` invocation; asserts `lake build` exits 0 and the boundary fragment is `sorry`-free, axiom-free, and contains no `unsafe` / `partial` / `noncomputable` declarations. |

## Rules

1. **Real builds, no shortcuts.** Tests here run the actual `lake build`
   subprocess; do not mock or simulate Lean output. The boundary's hygiene
   budget (zero strict `sorry`, zero axioms) is the *load-bearing*
   invariant of the project — never weaken the test to make it pass.
2. **Slow but rare.** Lean compilation is ~30–60s. Mark long Lean tests
   with `@pytest.mark.slow` so the fast loop (`pytest -m "not slow"`)
   stays sub-minute.
3. **Sympathetic to Lake state.** `lake build` caches in `lean/.lake/`;
   never delete that cache from a test (it's not the test's responsibility,
   and a clean build can take many minutes).
4. **Pair with the hygiene gate.** `tests/lean/` complements
   [`scripts/build_lean.py`](../../scripts/build_lean.py), which is the
   CI gate. The script and the tests must agree on what counts as a
   hygiene violation.

## See also

- [`../../lean/AGENTS.md`](../../lean/AGENTS.md)
- [`../../lean/ActinfPolicyEntanglement/AGENTS.md`](../../lean/ActinfPolicyEntanglement/AGENTS.md)
- [`../../scripts/build_lean.py`](../../scripts/build_lean.py)
