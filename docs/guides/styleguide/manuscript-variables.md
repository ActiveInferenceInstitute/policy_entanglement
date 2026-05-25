# §2 — Auto-injected manuscript variables (no hardcoded numbers)

Back to the styleguide hub: [`../styleguide.md`](../styleguide.md).

## The token namespace

The renderer in
[`src/manuscript/renderer.py`](../../../src/manuscript/renderer.py)
expands the following tokens during the `inject_manuscript_variables`
step:

| Token | Resolves to | Source |
| --- | --- | --- |
| `[[VAR:key]]` | a numeric value, numeric list, or explicitly allowlisted categorical descriptor | `output/data/manuscript_variables.json` |
| `[[VAR:key:fmt]]` | the same value formatted with Python `format(value, fmt)` | as above |
| `[[FIG:label]]` / `[[FIGREF:label]]` | image directive / inline cross-ref | `manuscript/refs/labels.yaml` → `figures` |
| `[[EQ:label]]` / `[[EQREF:label]]` | display equation / inline cross-ref | `manuscript/refs/labels.yaml` → `equations` |
| `[[SEC:label]]` / `[[SECREF:label]]` | full section heading / inline `§N` | `manuscript/refs/labels.yaml` → `sections` |
| `[[THM:label]]` / `[[THMREF:label]]` | bold theorem block / inline ref | `manuscript/refs/labels.yaml` → `theorems` |
| `[[LEAN:label]]` | fenced Lean source extracted from `lean/ActinfPolicyEntanglement/<module>.lean` | live source |
| `[@key]` / `[@k1; @k2]` | `(Author year)` inline citation | `manuscript/refs/citations.yaml` |
| `[[CITELIST:topic]]` | topic-grouped bibliography section | as above |

## The numeric-value contract

* Every numeric value mentioned in prose must use `[[VAR:key:fmt]]`
  (e.g. `[[VAR:ising_mi_at_lam_05:.4f]]`).
* Every grid count / range / agreement tolerance must use
  `[[VAR:param_sweep_grid_points]]` etc., never an integer literal.
* The validator
  ([`scripts/validate_manuscript.py`](../../../scripts/validate_manuscript.py))
  iterates all `[[VAR:key]]` tokens; missing keys are CI failures.
* Numeric ranges are checked: each value lies inside a published
  `EXPECTED_RANGES` interval.
* Non-numeric variables are exceptional and must be controlled
  categorical descriptors, such as configured ablation variant names or
  observation contexts. Add them only when the category itself is a
  source-of-truth hyperparameter, and extend the veridicality allowlist
  in `tests/test_veridicality.py`.

## The "no hardcoded numbers" rule, operationally

A reviewer scanning a section file should see only:

* registry tokens (`[[FIG:...]]`, `[[EQ:...]]`, …),
* `[[VAR:...]]` substitutions for numbers,
* prose, and
* (small) literal mathematical constants like $\log 2$, $1/2$, $\pi$
  that have no run-dependent value.

If you see `121`, `0.5`, `seed = 0`, or `T = 10` written into the
manuscript, that's a styleguide violation — those numbers belong in
`hyperparameters.py` and reach prose via `[[VAR:...]]`.

The same source-field rule applies to references. Paper-facing source
must not hand-write `§9.5`, `Theorem 5.1`, `Figure 7`, or `Eq. (3)` in
headings, captions, short labels, registry titles, or ordinary prose.
Use `[[SECREF:...]]`, `[[THMREF:...]]`, `[[FIGREF:...]]`, and
`[[EQREF:...]]`, or use a neutral heading such as "Entanglement
decomposition" followed by the registry token in the first sentence.
Rendered output is allowed to contain the resolved display labels.

## CI enforcement: `find_hardcoded_numeric_literals`

The validator
[`scripts/validate_manuscript.py`](../../../scripts/validate_manuscript.py)
calls
[`manuscript.validation.find_hardcoded_numeric_literals`](../../reference/python_api.md#validationpy)
on every manuscript section and
`find_hardcoded_rendered_source_literals` on headings plus the
rendered fields in `manuscript/refs/labels.yaml`.  The numeric gate
flags these pattern families:

| Pattern | Example caught | Replacement |
|---|---|---|
| `\d+-point\s+(grid\|linspace\|sweep\|sample)` | "121-point grid" | `[[VAR:param_sweep_grid_points]]-point grid` |
| `\d+\s+(grid points\|linspace points\|sweep points\|samples)` | "21 grid points" | `[[VAR:pymdp_sweep_grid_points]] grid points` |
| `seed\s*=\s*\d+` | "seed = 42" | `seed = [[VAR:figure_global_seed]]` |
| `T\s*=\s*\d+\s+(step\|steps\|rollout)` | "T = 10 steps" | `T = [[VAR:pymdp_rollout_steps]]` steps |

**Protected regions** (where literals are allowed): headings, fenced
code blocks, inline code spans (`` `T = 10` ``), `[[...]]` token
bodies, and the bold theorem-block paragraph
(`**Theorem 5.1.** ...`).

**Bypass**: there is no opt-out.  If a numeric literal is genuinely
fixed by mathematical convention (e.g. `K = 2` for the Bernoulli
toy, `\log 2` saturation), it must either (a) be a defined symbol
in [`S06_notation_and_concordance.md`](../../../manuscript/S06_notation_and_concordance.md)
or (b) live inside an inline code span / display-math block
where the validator already does not flag it.  Otherwise extend
`hyperparameters.py` and `manuscript_variables.py` so the value
flows from JSON.

The regression test
[`tests/test_pymdp_extras.py::test_real_manuscript_has_no_hardcoded_numeric_literals`](../../../tests/test_pymdp_extras.py)
asserts that the production manuscript stays clean.

## How variables get into the JSON

Each `_*_facts` helper in `manuscript_variables.py` derives values
from sentinel tuples (`H.ISING_MI_SENTINEL_LAMBDAS` …) and writes
them under stable keys.  `_hyperparameter_facts` mirrors the entire
hyperparameters summary verbatim.  The two together fully populate
the namespace the manuscript can refer to.

## Live derived variables (not hardcoded)

Three keys are now **live-derived** by `manuscript_variables.py`
rather than hardcoded — they are recomputed every render and locked
by the round-2 tests:

| Key | Resolves to | How it is derived | Replaces |
|---|---|---|---|
| `run_all_script_count` | `len(scripts.run_all.SCRIPTS)` | `_run_all_facts()` imports the live `SCRIPTS` tuple from `scripts/run_all.py` | hand-maintained script-count prose |
| `lean_structure_count` | count of `structure` declarations across the 17 Lean submodules (current value: **11**, including `FloatRealResidualWitness`) | `_lean_facts()` scans comment-stripped Lean source; legacy key `lean_inductive_count` removed | the old `lean_inductive_count` name |
| `lean_total_declarations` | `lean_def_count + lean_theorem_count + lean_structure_count` | derived live from the three constituent counts in `_lean_facts()` (current value: **126** = 39 + 76 + 11) | hardcoded total of 84 / 90 / 103 |
| `theorem_status_*_count` | theorem-status counts from `manuscript/refs/labels.yaml` | `_registry_facts()` derives the 21-row theorem roll-up (5 proved, 11 witness, 3 boundary, 1 forwarder, 1 roadmap) | typed status summaries in prose |
| `manuscript_section_file_count` | source/rendered section-file count used by the manuscript build | `_registry_facts()` counts the canonical manuscript section files; read `output/data/manuscript_variables.json` for the live value instead of hand-maintaining it here | stale "56 sections" prose |

Every prose mention of these counts must use `[[VAR:…]]`; the
hardcoded-numeric-literals validator (above) flags any drift.
