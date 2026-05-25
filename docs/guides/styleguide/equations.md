# §3 — Auto-numbered + cross-referenced equations

Back to the styleguide hub: [`../styleguide.md`](../styleguide.md).

As of **2026-05-12** the registry has **11 registered equations**
(8 currently referenced): `tc_decomp`, `ising_mi_closed_form`,
`optimal_lambda`, `pythagorean`, `e_geodesic`, `coupling_tax_bound`,
`total_correlation`, the round-2-added `mi_derivative_covariance` —
which records the identity
$\frac{d}{d\lambda} I_\lambda = \mathrm{Cov}_{q_\lambda}(J, K_c)$ that
underwrites the convexity witness discussion in `Convexity.lean` —
plus the registered-but-not-yet-referenced `closed_form_F`,
`d2F_dlambda2`, and `dF_dlambda`.

## Numbering scheme

* Each section's display equations are numbered `S.K`, where `S` is
  the section's `number` from `manuscript/refs/labels.yaml` and `K`
  is the 1-indexed source-order count of `[[EQ:label]]` tokens *and*
  bare `$$..$$` blocks together.
* Numbering is computed by
  [`src/manuscript/equation_numbering.py`](../../../src/manuscript/equation_numbering.py)
  in a single pre-pass over `manuscript/*.md` (deterministic; only
  depends on file content + registry).
* `retag_display_math` rewrites every rendered `$$..$$` block to
  carry the auto-assigned `\tag{S.K}`, overwriting any pre-existing
  tag — registered and bare equations share the same counter.
* `[[EQREF:label]]` resolves to the auto-assigned `S.K`; the legacy
  registry `number:` field is no longer load-bearing.

## Authoring rules

* **Do** define a top-level / load-bearing equation by writing
  `[[EQ:my_label]]` at its location and adding the LaTeX body to
  `manuscript/refs/labels.yaml` under `equations:`.
* **Do** reference it elsewhere with `[[EQREF:my_label]]`.
* **Don't** use `\tag{...}` or `\label{...}` by hand — auto-numbering
  owns those.
* **Don't** worry about renumbering when you reorder paragraphs:
  the numbering is recomputed each render.

## Validator checks

[`tests/test_equation_numbering.py`](../../../tests/test_equation_numbering.py)
asserts:

* every `[[EQ:label]]` token in `manuscript/*.md` ends up with a
  numeric assignment in the precomputed map;
* every rendered `$$..$$` block carries a `\tag{...}` after render;
* tags emitted in section §N start with the prefix `N.`.

## Adding a new equation

1. Add the LaTeX body to `manuscript/refs/labels.yaml`:

   ```yaml
   equations:
     my_eq:
       latex: |
         x \;=\; y + z
       name: "My new identity"
       sections: ["§N"]
   ```

2. In the body of section *N*'s markdown, write `[[EQ:my_eq]]` at the
   point where the equation should appear.
3. Reference it from anywhere with `[[EQREF:my_eq]]`.
4. Run `uv run python scripts/inject_manuscript_variables.py` and
   `uv run python scripts/validate_manuscript.py` to confirm.
