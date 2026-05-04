# AGENTS.md — `src/`

## Layout

Python companion package for the Policy Entanglement project, organised
into three subpackages — each with its own `AGENTS.md`:

| Subpackage | Path | Purpose |
|---|---|---|
| `lean` | [`src/lean/`](lean/) | Analytical mirrors of the Lean 4 boundary fragment (joint distributions, coupling, free energies, geometry, spectral, heterogeneous, Bernoulli toy, decomposition theorem) |
| `simulation` | [`src/simulation/`](simulation/) | pymdp 1.0.1 POMDP harness for coupled-policy ensembles (specs, builders, agents, inference, rollout, sweep) |
| `visualizations` | [`src/visualizations/`](visualizations/) | Reusable plotting helpers (heatmaps, joint plots, spectral, trajectory, graph, log-weight) |

## Constitution

1. **Pure compute, no I/O.**  Every module under `src/` is a library:
   takes ndarrays, returns ndarrays / floats / dataclasses.  Print, save,
   plot — none of that.  I/O lives in [`../scripts/`](../scripts/).
   Exception: `visualizations/` writes PNGs but is itself driven by
   scripts and tests, never imported by `lean/` or `simulation/`.
2. **No mocks, no stubs.**  Tests pass real arrays through the actual
   computations.  If you need configurable behaviour, add a parameter,
   don't add a mock.
3. **Bare imports.**  Every subpackage is on `pythonpath` directly, so
   write `from coupling import …`, `from specs import …`,
   `from heatmaps import …`.  Never use relative imports.
4. **Type hints everywhere.**  Public signatures use
   `numpy.typing.NDArray[np.float64]` aliased as `ArrayF`.
5. **Validate at boundaries.**  Public entry points raise
   `ValueError` / `IndexError` on shape / index issues with
   informative messages.
6. **Determinism.**  No `time`, no module-level randomness.  RNGs are
   created locally with explicit seeds in tests.
7. **Coverage floor: 90 %.**  Each new function lands with tests in
   `tests/test_<module>.py`.

## Cross-subpackage rules

* `lean/` is the analytical core — no `pymdp`, no `matplotlib`,
  no `seaborn` / `networkx`.
* `simulation/` may import from `lean/` but **not** from
  `visualizations/`.  pymdp / jax imports live exclusively in
  `simulation/agents.py`.
* `visualizations/` may import from `lean/` (for analytical helpers
  used in plot construction) and may consume `simulation` outputs at
  call time, but does no inference of its own.

## Mirror invariant

For every concept that lives in
[`../lean/ActinfPolicyEntanglement/<Module>.lean`](../lean/ActinfPolicyEntanglement/),
provide an executable Python implementation in `src/lean/<module>.py`
and a test in `tests/test_<module>.py`.  This is the load-bearing
sanity rail for the eventual Mathlib-backed Lean proofs.

## Numerical pitfalls

* **`log(0)`**: use `_safe_log` (in `lean/free_energy.py`) when computing
  `∑ q · log q`; floors at `1e-300` so zero entries don't blow up.
* **Floating divisions**: `normalize()` raises if the total mass is
  ≤ 0.  Never divide by an unchecked sum.
* **Schmidt rank**: choose the SVD threshold deliberately
  (`atol=1e-9` works for most cases; `1e-12` is too tight for the
  Ising posterior at finite λ where the small singular value is
  ~1e-10).
* **Sign of total correlation gain**:
  `total_correlation_gain = -total_correlation(q)`.  Don't double-negate.
* **pymdp double-EFE**: `coupled_policy_posterior` passes `zero_G` to
  `entangled_posterior` because pymdp's `q_pi` already absorbs the
  per-stream EFE.  Do not "fix" this by piping `per_stream_efe`'s
  output back in — that double-counts the bias.
