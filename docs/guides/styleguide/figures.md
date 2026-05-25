# §4 — Auto-numbered, method-anchored figures

Back to the styleguide hub: [`../styleguide.md`](../styleguide.md).

As of the latest generated audit, the figure count is derived from
`manuscript/refs/labels.yaml::figures` and mirrored into
`output/reports/release_readiness.json`.
See the build-and-run guide's
[figure-count scoping section](../build_run.md#figure-count-scoping)
for the breakdown between `scripts/generate_figures.py` (15 headline
analytical PNGs), `scripts/simulate_pymdp.py` (14 pymdp dashboards
and joint snapshots), the three round-3 sims
(`scripts/simulate_multi_k.py`, `scripts/simulate_long_horizon.py`,
`scripts/simulate_revertibility.py`), and the stress-test sidecars
from `scripts/simulate_robustness.py`, plus the shipped BTAI and
adversarial panels from `scripts/simulate_btai.py` and
`scripts/simulate_adversarial.py`. `scripts/simulate_gnn.py` emits a
validated non-registry diagnostic PNG for S08; it is not a numbered
manuscript figure.

## Caption contract

Every figure caption in `manuscript/refs/labels.yaml` must:

* state the figure's **uncertainty semantics** through the registry's
  `uncertainty:` field, using one of `deterministic_grid`,
  `canonical_seed`, `replicate_envelope`, `confidence_interval`, or
  `analytical_schematic`;
* name the **generation method** as a function path
  (`scripts/generate_figures.py::figure_ising_mi_curve`,
  `lean.coupling.entangled_posterior`, etc.);
* declare the **grid hyperparameter** used (e.g. "21-point linspace
  over $\lambda \in [0, 4]$
  (`simulation.hyperparameters.PYMDP_SWEEP_LAMBDAS`)");
* declare any **seed** or rollout horizon used;
* reference the **artifact path** under `output/` (CSV, JSON) when
  applicable;
* be otherwise concise and prose-readable — no jargon dump.

The renderer appends a short "Uncertainty semantics:" sentence from
the `uncertainty:` field, so captions remain short while the PDF still
tells the reader whether a plot is a deterministic grid, a canonical
fixed-seed trajectory, a replicate envelope, a confidence interval, or
an analytical schematic.  The same class is stored in each PNG as
`project.uncertainty_semantics`; `scripts/validate_outputs.py` fails
when the metadata is absent or outside the allowed vocabulary.

The `source:` field at the bottom of each figure's YAML entry must
match the `figure_*` function exactly so a reader can navigate from
caption → code in one step.

## Numbering

Figures are auto-numbered by pandoc (the downstream renderer); the
registry's `number:` field is *not* injected as a `Figure N:` prefix
because the renderer would double-prefix.  The captions therefore
contain only the *body* text; pandoc inserts "Figure N:" itself.

## The "Sources:" field

Every figure entry's `source:` field names the function in
`scripts/generate_figures.py` or `scripts/simulate_pymdp.py` that
produces the PNG.  Tests
([`tests/test_figure_scripts.py`](../../../tests/test_figure_scripts.py))
import each function and execute it end-to-end, confirming the PNG
header on disk.

## Adding a new figure

1. Add a `figure_*` function to `scripts/generate_figures.py` (pure
   I/O + plotting; computation comes from `lean.*` or `simulation.*`).
2. Read every grid / scalar from `H = simulation.hyperparameters`.
3. Register the figure in `manuscript/refs/labels.yaml`:

   ```yaml
   figures:
     my_fig:
       path: output/figures/my_fig.png
       caption: |
         <body, naming the function path + grid constant>.
       short: "Short label for cross-refs"
       sections: ["§N"]
       source: scripts/generate_figures.py::figure_my_fig
   ```

4. In the body of section *N*'s markdown, write `[[FIG:my_fig]]`.
5. Add a smoke test (see existing parametrized cases in
   `tests/test_figure_scripts.py`).
