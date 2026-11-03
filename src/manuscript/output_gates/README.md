# `src/manuscript/output_gates/`

Output-artifact validation for the manuscript pipeline, imported as
`manuscript.output_gates`. `__init__.py` re-exports `validate_figures` and
`validate_variables` plus the constants they use (`REQUIRED_FIGURES`,
`OPTIONAL_FIGURES`, `REQUIRED_VARIABLES`, the PNG and font floors, and
`OUTPUT_DIR`).

The modules split by artifact: `artifact_validators`, `png_validation`,
`sweep_validation`, `csv_helpers`, `_reporting`, and the pymdp-specific
validators for sweep, robustness, revertibility and long-horizon outputs.

`constants.py` is the single home for the figure and variable lists and the
thresholds; add a new required artifact there rather than in a validator.
