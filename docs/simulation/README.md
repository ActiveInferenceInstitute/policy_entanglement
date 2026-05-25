# `docs/simulation/` — pymdp + visualization technical reference

Documents the *grounded* layer of the project: a deterministic
end-to-end simulation harness on top of pymdp 1.0.1, plus the
matplotlib helpers that render every manuscript figure.

| File | Purpose |
|---|---|
| [`pomdp_simulation.md`](pomdp_simulation.md) | pymdp 1.0.1 POMDP harness architecture, layered design, and full API |
| [`visualizations.md`](visualizations.md) | Reusable plotting helpers (heatmaps, joint plots, spectral, trajectory, graph, log-weight) |

Current simulation baseline: **pymdp 1.0.1**, default stream count from
`PYMDP_ENSEMBLE_K` and the configured multi-K sweep from
`MULTI_K_VALUES`. PNG figure count is reported by
`output/reports/release_readiness.json` / `output/figures/` across
`scripts/generate_figures.py`, `scripts/simulate_pymdp.py`,
`scripts/simulate_multi_k.py`, `scripts/simulate_long_horizon.py`,
`scripts/simulate_revertibility.py`, plus the stress-test and
fixed-marginal null-control sidecars from `scripts/simulate_robustness.py`.  See
[`../guides/build_run.md`](../guides/build_run.md) for the figure-count
scoping table.
