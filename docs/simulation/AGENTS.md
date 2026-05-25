# AGENTS.md — `docs/simulation/`

Documentation for the `inferactively-pymdp==1.0.1`-backed `pymdp`
POMDP simulation harness under [`../../src/simulation/`](../../src/simulation/)
and the rendering helpers under
[`../../src/visualizations/`](../../src/visualizations/).

## Files

| File | Scope |
|---|---|
| `pomdp_simulation.md` | The end-to-end pymdp harness: state spaces, ensemble specs, builders, agents, rollout loop, free-energy bundle, and JSONL run logger. Mirrors what `manuscript/4C_pymdp_harness.md` and `4D_pymdp_free_energy.md` describe. |
| `visualizations.md` | The plot helpers under `src/visualizations/`: heatmaps, joint plots, spectral, trajectory, graph, log-weight, free-energy dashboards, pymdp-extra dashboards, and the PNG `tEXt` reproducibility metadata helpers. |

## Rules

1. **Code-truth invariant.** Every API mentioned here must match the actual
   public symbol in `src/simulation/<module>.py` or
   `src/visualizations/<module>.py`. Verified by
   [`tests/test_python_api_coverage.py`](../../tests/test_python_api_coverage.py).
2. **Hyperparameter source-of-truth.** All defaults shown in code blocks
   must source from
   [`../../src/simulation/hyperparameters.py`](../../src/simulation/hyperparameters.py).
   Hardcoding a hyperparameter value here drifts from the live default and
   silently breaks the manuscript variable injection.
3. **No mocks; pymdp is real.** When showing an example invocation, the
   command must run end-to-end against the real `pymdp` import/API supplied
   by `inferactively-pymdp==1.0.1` (`uv sync --group sim`). If a tutorial
   requires `inferactively-pymdp` that is not installed by default, gate the
   section with an explicit `requires_pymdp` flag.
4. **Reproducibility tEXt metadata.** When showing how to call a figure
   helper, include the metadata recipe (`metadata.figure_metadata` /
   `metadata.read_figure_metadata`) so consumers can verify provenance.

## Current ground truth

- `inferactively-pymdp==1.0.1` is pinned in the `sim` group of
  `pyproject.toml` and provides the `pymdp` import/API.
- K = 2 streams default (override via `make_ising_ensemble(num_streams=…)`);
  configured multi-K sweep via `scripts/simulate_multi_k.py`.
- PNG figure count is live in `output/reports/release_readiness.json`
  and `output/figures/`; registered figures live in
  `manuscript/refs/labels.yaml::figures`.
- JAX runs in float32 by default — the precision boundary is noted
  inline in `manuscript/4C_pymdp_harness.md` and reflected in the
  tolerance budget used by `tests/test_simulation_pymdp.py`.
- Reproducibility metadata: PNGs carry `tEXt`-chunk provenance
  (seed, script, git short SHA) plus automatic figure-statistics
  summaries, so reruns are **numerically identical modulo the embedded
  build timestamp** — see
  [`visualizations.md`](visualizations.md).

## See also

- [`../../src/simulation/AGENTS.md`](../../src/simulation/AGENTS.md)
- [`../../src/visualizations/AGENTS.md`](../../src/visualizations/AGENTS.md)
- [`../../manuscript/4C_pymdp_harness.md`](../../manuscript/4C_pymdp_harness.md)
- [`../../manuscript/4D_pymdp_free_energy.md`](../../manuscript/4D_pymdp_free_energy.md)
