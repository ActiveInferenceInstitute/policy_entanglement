# AGENTS.md - `lean/MathlibProofs/`

`lean/MathlibProofs/` is the separate Mathlib4 analytic-discharge
package. It is allowed to import Mathlib and to use mathematically
required `noncomputable` real-analysis definitions, but it must not
weaken the stock-Lean boundary under
[`../ActinfPolicyEntanglement/`](../ActinfPolicyEntanglement/).

Rules for edits:

1. Keep boundary modules Mathlib-free. Never move `import Mathlib` into
   `lean/ActinfPolicyEntanglement/` or `lean/FepSketches/`.
2. Do not introduce `sorry`, `axiom`, `unsafe`, or `partial`.
3. Any theorem cited as a MathlibProofs result must be real compiled
   Lean source in this package, not pseudo-code or a planned row.
4. Run `uv run python scripts/build_mathlib_proofs.py` after edits.
   The keystone `#print axioms` audit must remain foundational-only.
5. The current package discharges the headline real-valued
   decomposition and supporting general-K finite-KL kernel. Remaining
   witness rows still need row-specific compiled source before the
   manuscript may promote their status.
