# Python API: subpackage `simulation/`

*Latest generated audit.* The simulation API now includes the
canonical pymdp harness plus reviewer-facing robustness, coupling
ablation, and long-horizon replicate sidecars.  The new empirical
surface is still source-driven: grids and seeds live in
`hyperparameters.py`, numerical helpers live in `simulation/`, and
scripts only orchestrate I/O.

`inferactively-pymdp==1.0.1`-backed `pymdp` POMDP simulation harness:
hyperparameters, agent factory, coupled-policy posterior, free-energy
bundle, λ-sweep, deterministic rollout, structured JSONL logging,
bundle-aggregation statistics.

Imports: `from simulation.<module> import …` (`pythonpath = src/`).

Companion: [`../simulation/pomdp_simulation.md`](../simulation/pomdp_simulation.md) (harness guide),
[`statistics_reference.md`](statistics_reference.md) (determinism + bundle observables).

---

## Subpackage `simulation/`

`inferactively-pymdp==1.0.1` is an optional dependency
(`uv sync --group sim`) that provides the `pymdp` import/API; the
agent / inference / rollout modules raise
`ModuleNotFoundError(PYMDP_INSTALL_HINT)` when it is missing.
`pymdp_available()` lets callers gate gracefully.

### `specs.py`

```python
@dataclass(frozen=True)
class StreamSpec:
    A: ArrayF; B: ArrayF; C: ArrayF; D: ArrayF; name: str = ""
    def num_obs() / num_states() / num_controls() -> int
    def validate() -> None  # raises ValueError on shape / stochasticity issues

@dataclass(frozen=True)
class CoupledEnsembleSpec:
    streams: tuple[StreamSpec, ...]
    coupling_j: ArrayF; coupling_kc: ArrayF; gamma: float = 1.0
    def num_streams() -> int; policy_shape() -> tuple[int, ...]; validate() -> None
```

### `builders.py`

```python
def two_state_identity_likelihood(num_states: int = 2) -> ArrayF
def two_action_swap_transitions(num_states: int = 2) -> ArrayF
def make_bernoulli_stream(name: str, *,
                          preference_strength: float = 1.0,
                          prior_bias: float = 0.5) -> StreamSpec
def ising_coupling_tensor(shape: tuple[int, ...], scale: float = 1.0) -> ArrayF
def make_ising_ensemble(*, coupling_lambda: float = 1.0,
                        preference_strength: float = 1.0,
                        num_streams: int = 2, gamma: float = 1.0) -> CoupledEnsembleSpec
```

### `agents.py`

```python
PYMDP_INSTALL_HINT: str
def pymdp_available() -> bool
def build_pymdp_agent(spec: StreamSpec, *,
                      policy_len: int = 1, gamma: float = 1.0,
                      inference_algo: str = "fpi") -> Any  # source returns Any (pymdp.agent.Agent at runtime)
def build_pymdp_agents(spec: CoupledEnsembleSpec, **kwargs) -> list[Any]  # source returns list[Any] (list of pymdp Agents at runtime)
```

### `inference.py`

```python
def per_stream_efe(spec, observations) -> list[ArrayF]
def per_stream_policy_posterior(spec, observations) -> list[ArrayF]
def coupled_policy_posterior(spec, observations, lam: float) -> ArrayF

@dataclass(frozen=True)
class FreeEnergyBundle:
    lam: float
    vfe_per_stream: ArrayF       # F[q^k_λ] per stream
    vfe_total: float             # Σ_k F[q^k_λ]
    efe_per_stream: tuple[ArrayF, ...]   # G_k from pymdp
    efe_under_posterior: ArrayF  # ⟨G_k⟩_{q^k_λ}
    joint_entropy: float         # H(q_λ)
    marginal_entropies: ArrayF   # H(q^k_λ) per stream
    total_correlation: float     # I(q_λ) = Σ H(q^k) − H(q)
    coupling_term: float         # λ ⟨J⟩_{q_λ}
    action_distribution: ArrayF  # q_λ flat over Π

@dataclass(frozen=True)
class DecompositionWitness:
    lam: float
    lhs: float
    rhs: float
    residual: float

def variational_free_energy(spec, observations, lam: float) -> ArrayF
def expected_free_energy_under_posterior(spec, observations, lam: float) -> ArrayF
def coupling_energy(spec, observations, lam: float) -> float
def free_energy_bundle(spec, observations, lam: float) -> FreeEnergyBundle
def free_energy_curve(spec, observations, lams) -> list[FreeEnergyBundle]
def decomposition_witness_curve(spec, observations, lams) -> list[DecompositionWitness]
```

`decomposition_witness_curve` is the pymdp-backed Theorem 5.1 identity
check used by `scripts/simulate_pymdp.py`. It runs pymdp once for the
mean-field base, evaluates the entangled posterior on every λ, and
records `free_energy_against_entangled_prior` versus
`entanglement_decomposition_rhs(...).total`.  The helper zeroes
per-stream `G` vectors in the analytical call because pymdp has
already absorbed EFE into the policy posterior.

### `hyperparameters.py` (facade — import from here only)

Domain constants live in ``hyperparameters_{grids,pymdp,robustness,experiments,sentinels}.py``;
this module re-exports the full public surface and hosts
``grid_count`` / ``figure_hyperparameter_summary``.

```python
@dataclass(frozen=True)
class FigureGrid:
    start: float; stop: float; num: int; label: str = ""
    def values() -> ArrayF                        # 1-D linspace

# Grids (read by figure scripts; mirrored into manuscript_variables.json):
PARAMETER_SWEEP_LAMBDAS:    FigureGrid           # 121 pts on [0, 6]
COUPLING_TAX_LAMBDAS:       FigureGrid           # 31 pts on [0, 1.5]
PHASE_DIAGRAM_LAMBDAS:      FigureGrid           # 401 pts on [0, 4]
OPTIMAL_LAMBDA_DELTAS:      FigureGrid           # 191 pts on [-0.95, 0.95]
SCHMIDT_RANK_LAMBDAS:       FigureGrid           # 81 pts on [0, 4]
PHASE_LANDSCAPE_LAMBDAS:    FigureGrid           # 41 pts on [0, 4]
PHASE_LANDSCAPE_UTILITIES:  FigureGrid           # 21 pts on [0, 2]
LOG_WEIGHT_FLOW_LAMBDAS:    FigureGrid           # 31 pts on [0, 3]
KL_GEODESIC_LAMBDAS:        FigureGrid           # 21 pts on [0, 4]
LAMBDA_STAR_UTILITIES:      FigureGrid           # 20 pts on [0, 0.95]
LAMBDA_STAR_GAMMAS:         FigureGrid           # 16 pts on [0.5, 2]
PYMDP_SWEEP_LAMBDAS:        FigureGrid           # 21 pts on [0, 4]
MULTI_K_SWEEP_LAMBDAS:      FigureGrid           # 9 pts on [0, 4] (T1: K>2 sweep)
ROBUSTNESS_SWEEP_LAMBDAS:   FigureGrid           # one-axis stress-test sweep

# Scalars:
PYMDP_ROLLOUT_STEPS:           int               # 10
PYMDP_ROLLOUT_SEED:            int               # 0
PYMDP_ROLLOUT_LAMBDA:          float             # 2.0
PYMDP_SWEEP_OBSERVATIONS:      tuple[int, ...]   # (0, 0)
FIGURE_GLOBAL_SEED:            int               # 42
PYMDP_ENSEMBLE_K:              int               # 2
PYMDP_ENSEMBLE_GAMMA:          float             # 1.0
PYMDP_ENSEMBLE_COUPLING_LAMBDA:float             # 1.0
PYMDP_DECOMPOSITION_RESIDUAL_TOLERANCE: float    # 1e-9
PHASE_LAMBDA_C1:               float             # 0.5
PHASE_LAMBDA_C2:               float             # 2.5
COUPLING_TAX_PROBE_LAMBDA:     float             # 0.05
TT_RANK_PROFILE_LAMBDA:        float             # 2.0
SPECTRAL_RANK_ATOL:            float             # 1e-9
JOINT_HEATMAP_LAMBDA:          float             # 2.0
ARCHETYPE_DENDROGRAM_LAMBDA:   float             # 3.0
COUPLING_GRAPH_STREAM_COUNT:   int               # 4
BERNOULLI_VERIFICATION_TOLERANCE: float           # mirrored to manuscript variables
PARAMETER_SWEEP_AGREEMENT_TOLERANCE: float       # mirrored to manuscript variables
PYMDP_MARGINAL_AGREEMENT_TOLERANCE: float        # mirrored to manuscript variables
PYMDP_TC_ZERO_TOLERANCE:        float             # mirrored to manuscript variables
PYMDP_COUPLING_ZERO_TOLERANCE:  float             # mirrored to manuscript variables
PYMDP_ENTROPY_ADD_TOLERANCE:    float             # mirrored to manuscript variables
PYMDP_SINGLE_STREAM_FLOAT_TOLERANCE: float        # mirrored to manuscript variables
ROBUSTNESS_OBSERVATION_CONTEXTS: tuple[tuple[int, ...], ...]
ROBUSTNESS_GAMMAS: tuple[float, ...]
ROBUSTNESS_PREFERENCE_STRENGTHS: tuple[float, ...]
ROBUSTNESS_COUPLING_SCALES: tuple[float, ...]
COUPLING_ABLATION_VARIANTS: tuple[str, ...]
COUPLING_ABLATION_KC_MATRIX: tuple[tuple[float, float], tuple[float, float]]

# Sentinel-λ tuples for VAR exports:
ISING_MI_SENTINEL_LAMBDAS:               tuple[float, ...]  # (0.5, 1, 2)
ISING_MI_SATURATION_LAMBDA:              float
OPTIMAL_LAMBDA_SENTINEL_DELTAS:          tuple[float, ...]  # (0.5, 0.9)
SPECTRAL_SENTINEL_LAMBDAS:               tuple[float, ...]  # (0, 1, 3)
ISING_ALIGNMENT_SENTINEL_LAMBDAS:        tuple[float, ...]
MOTOR_ATTENTION_SENTINEL_LAMBDAS:        tuple[float, ...]
TT_RANK_STREAM_COUNTS:                   tuple[int, ...]    # (2, 3, 4, 5)
PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS:tuple[float, ...]
BERNOULLI_VERIFICATION_LAMBDAS:           tuple[float, ...]

def grid_count(grid: FigureGrid) -> int
def figure_hyperparameter_summary() -> dict[str, object]
```

### `statistics.py`

```python
@dataclass(frozen=True)
class BundleSummary:
    n_lambda_points: int; lambda_min: float; lambda_max: float
    tc_min: float; tc_max: float; tc_mean: float
    tc_at_half_saturation: float; lambda_at_half_saturation: float
    vfe_total_min/max/mean: float
    coupling_term_min/max: float
    joint_entropy_min/max: float
    aligned_mass_min/max/at_lambda_max: float
    kl_to_lambda_zero_min/max: float
    kl_to_uniform_at_lambda_max: float
    action_entropy_min/max: float
    action_mode_prob_at_lambda_max: float

def pymdp_summary_statistics(bundles) -> BundleSummary
def summary_to_var_dict(summary, *, prefix="pymdp") -> dict[str, float]

@dataclass(frozen=True)
class QuantileEnvelope:
    """Per-grid-point quantile statistics over a stack of sweeps."""
    lams: ArrayF
    median: ArrayF
    lower: ArrayF      # default 0.25 quantile
    upper: ArrayF      # default 0.75 quantile
    minimum: ArrayF
    maximum: ArrayF
    n_runs: int
    quantile_lower: float
    quantile_upper: float

def quantile_envelope_over_sweeps(
    sweeps, *, field="total_correlation",
    quantile_lower=0.25, quantile_upper=0.75,
) -> QuantileEnvelope
def is_monotone_nondecreasing(values, *, atol=1e-9) -> bool
def total_correlation_saturation_index(
    bundles, *, saturation_fraction=0.95,
) -> float
```

### `logging_utils.py`

```python
@dataclass
class RunLogger:
    path: Path; enabled: bool = True
    def fresh(): ...                 # truncate the JSONL log
    def emit(record: Mapping): ...   # append one JSON record + timestamp
    def timed(**base) -> TimedRecord  # context manager; auto-records runtime_ms

@dataclass
class TimedRecord:
    def update(**fields): ...
    def set_status(status: str): ...
    def close(): ...                  # called by context manager exit

def default_logger(project_root: Path) -> RunLogger
```

### `pymdp_pipeline.py`

CLI parsing and hyperparameter override layer for the pymdp simulation
harness. Consumed by ``scripts/simulate_pymdp.py``.

```python
def parse_args(argv: list[str] | None = None) -> argparse.Namespace
def apply_overrides(args: argparse.Namespace) -> None
def main(argv: list[str] | None = None) -> None
```

### `long_horizon_pipeline.py`

Long-horizon coupled rollout orchestration consumed by
``scripts/simulate_long_horizon.py``.

```python
def figure_metadata_snapshot(project_root: Path, source_function: str, **extra) -> dict[str, str]
def run_long_horizon_pipeline(project_root: Path) -> int
```

### `multi_k_pipeline.py`

Multi-K ensemble sweep orchestration consumed by ``scripts/simulate_multi_k.py``.

```python
def figure_metadata_snapshot(project_root: Path, source_function: str, **extra) -> dict[str, str]
def write_multi_k_csv(sim_dir: Path, k: int, results) -> Path
def run_multi_k_pipeline(project_root: Path) -> int
```

### `rollout.py`

```python
@dataclass(frozen=True)
class RolloutStep:
    t: int; observations: tuple[int, ...]
    mean_field_marginals: tuple[ArrayF, ...]
    coupled_joint: ArrayF
    sampled_actions: tuple[int, ...]; total_correlation: float

@dataclass(frozen=True)
class Rollout:
    steps: tuple[RolloutStep, ...]
    spec: CoupledEnsembleSpec; lam: float; seed: int
    def total_correlations() -> ArrayF
    def joint_trajectory() -> ArrayF

def simulate_coupled_rollout(spec, *, horizon: int = 8, lam: float = 1.0,
                             seed: int = 0,
                             initial_observations: Sequence[int] | None = None,
                             on_step: Callable[[RolloutStep], None] | None = None
                             ) -> Rollout
```

### `sweep.py`

```python
@dataclass(frozen=True)
class LambdaSweepResult:
    lam: float; joint: ArrayF; marginals: tuple[ArrayF, ...]
    total_correlation: float; is_pmf: bool
    @property
    def num_streams(self) -> int

def lambda_sweep(spec, observations, lams) -> list[LambdaSweepResult]
def total_correlation_curve(spec, observations, lams) -> ArrayF
def marginal_trajectory(rollout: Rollout, k: int) -> ArrayF
```

### `multi_k_experiments.py` (T1: K>2 ensemble experiments)

```python
@dataclass(frozen=True)
class MultiKResult:
    K: int; lam: float
    total_correlation: float
    marginal_entropies: tuple[float, ...]
    joint_entropy: float
    coupling_term: float
    tt_ranks: tuple[int, ...]
    aligned_mass: float

def run_multi_k_sweep(
    K: int, lams, *, coupling_lambda_gen, gamma, observations=None,
) -> list[MultiKResult]
def multi_k_joint_snapshot(
    K: int, lam: float, *, coupling_lambda_gen, gamma, observations=None,
) -> ArrayF
def multi_k_summary(results: Sequence[MultiKResult]) -> dict[str, float]
```

Hyperparameters consumed: `MULTI_K_VALUES`, `MULTI_K_SWEEP_LAMBDAS`,
`MULTI_K_SENTINEL_LAMBDA`. CSV sidecars are emitted as one
``output/simulations/pymdp_K*_sweep.csv`` file per configured stream
count.

### `multi_k_pipeline.py` (thin-script orchestration for `scripts/simulate_multi_k.py`)

```python
def figure_metadata_snapshot(project_root: Path, source_function: str, **extra) -> dict[str, str]
def write_multi_k_csv(sim_dir: Path, k: int, results) -> Path
def run_multi_k_pipeline(project_root: Path) -> int
```

### `long_horizon.py` (T2: configured habit-accumulation rollout)

```python
@dataclass(frozen=True)
class LongHorizonResult:
    T: int; lam: float; seed: int
    total_correlations: ArrayF
    joint_trajectory: ArrayF
    marginal_trajectories: tuple[ArrayF, ...]
    tail_marginal_means: tuple[ArrayF, ...]
    tail_kl_per_stream: tuple[float, ...]
    tail_kl_first_per_stream: tuple[float, ...]
    tail_kl_mean_per_stream: tuple[float, ...]
    tail_kl_max_per_stream: tuple[float, ...]
    adjacent_kl_mean_per_stream: tuple[float, ...]
    adjacent_kl_max_per_stream: tuple[float, ...]
    tail_window: int
    habit_accumulation: bool
    steady_state_tol: float

def long_horizon_rollout(
    *, coupling_lambda_gen, gamma, num_streams, horizon, lam, seed,
    tail_window, steady_state_tol, progress_callback=None,
) -> LongHorizonResult
def long_horizon_summary(result: LongHorizonResult) -> dict[str, float]
def trajectory_tc_nonneg(result, atol=1e-9) -> bool
def trajectory_tc_finite(result) -> bool
def trajectory_marginals_are_pmfs(result, atol=1e-7) -> bool
def recompute_total_correlations(result: LongHorizonResult) -> ArrayF
def tc_trajectory_recomputable(result, atol=1e-9) -> bool
def tail_window_kl(
    marginal_trajectories: tuple[ArrayF, ...], tail_window: int
) -> tuple[tuple[ArrayF, ...], tuple[float, ...]]
def tail_window_kl_statistics(
    marginal_trajectories: tuple[ArrayF, ...], tail_window: int
) -> tuple[tuple[ArrayF, ...], tuple[float, ...], tuple[float, ...],
           tuple[float, ...], tuple[float, ...], tuple[float, ...]]
```

`joint_trajectory` keeps the full dense joint path so
`recompute_total_correlations` can recompute `I(q_t)` directly from
the saved joint distributions. `tc_trajectory_recomputable` is the
validator-facing invariant: it fails if the stored total-correlation
curve ever drifts from the retained joint path.

`tail_window_kl` is the backward-compatible pure-numpy helper returning
the first-tail KL against the trailing-window mean.  The richer
`tail_window_kl_statistics` helper also returns mean-tail, max-tail,
and adjacent-step KL summaries, so prose and captions do not conflate
$D_{\mathrm{KL}}(q_t^k\|\bar q^k_{\mathrm{tail}})$ with
$D_{\mathrm{KL}}(q_t^k\|q_{t-1}^k)$.  The habit-accumulation test uses
the max-tail KL against `LONG_HORIZON_STEADY_STATE_TOL`, and all of
this can be exercised at arbitrary synthetic horizons without
re-running pymdp.
Tests in [`tests/test_tail_window_kl.py`](../../tests/test_tail_window_kl.py).

Hyperparameters consumed: `LONG_HORIZON_STEPS`, `LONG_HORIZON_LAMBDA`,
`LONG_HORIZON_SEED`, `LONG_HORIZON_TAIL_WINDOW`,
`LONG_HORIZON_STEADY_STATE_TOL`. CSV sidecar:
``output/simulations/pymdp_long_horizon.csv``.

### `robustness.py` (facade — stress tests, ablations, and replicate sidecars)

Import from ``simulation.robustness`` only. Domain modules (package-internal):

| Module | Role |
|--------|------|
| `robustness_scenarios.py` | Dataclasses + scenario builders |
| `robustness_core.py` | Shared λ-loop |
| `robustness_one_axis.py` | One-axis suite |
| `robustness_interaction.py` | Two-axis interaction suite |
| `robustness_controls.py` | Ablation + marginal-null control |
| `robustness_replicates.py` | Long-horizon replicate sidecars |
| `robustness_stats.py` | Wilson intervals |
| `robustness_emit.py` | CSV/JSON + figure metadata |
| `robustness_runner.py` | Pipeline glue |

Boundary contract: [`docs/_audit/ISA_20260525_robustness_cluster.md`](../_audit/ISA_20260525_robustness_cluster.md).

```python
@dataclass(frozen=True)
class RobustnessScenario:
    scenario_id: str; axis: str; level: str
    observations: tuple[int, ...]
    gamma: float; preference_strength: float; coupling_scale: float

@dataclass(frozen=True)
class RobustnessRow:
    scenario_id: str; axis: str; level: str
    observations: tuple[int, ...]
    gamma: float; preference_strength: float; coupling_scale: float
    lam: float; total_correlation: float
    joint_entropy: float; marginal_entropy_sum: float
    coupling_term: float; aligned_mass: float
    decomposition_lhs: float; decomposition_rhs: float
    decomposition_residual: float

@dataclass(frozen=True)
class RobustnessScenarioSummary:
    scenario_id: str; axis: str; level: str
    tc_max: float; tc_final: float
    lambda_half_saturation: float | None
    residual_max: float; monotone_tc: bool

@dataclass(frozen=True)
class CouplingAblationRow:
    variant: str; lam: float
    total_correlation: float; joint_entropy: float
    marginal_entropy_sum: float; coupling_term: float
    aligned_mass: float
    decomposition_lhs: float; decomposition_rhs: float
    decomposition_residual: float

@dataclass(frozen=True)
class LongHorizonReplicateRecord:
    seed: int; habit_accumulation: bool
    tc_initial: float; tc_final: float; tc_mean: float; tc_max: float
    tail_kl_window_max: float; adjacent_kl_max: float

@dataclass(frozen=True)
class LongHorizonThresholdSensitivityRow:
    threshold: float; pass_rate: float
    pass_count: int; fail_count: int
    ci_low: float; ci_high: float

@dataclass(frozen=True)
class MarginalNullControlRow:
    lam: float
    original_total_correlation: float
    null_total_correlation: float
    original_aligned_mass: float
    null_aligned_mass: float
    tc_removed: float
    aligned_mass_shift: float

@dataclass(frozen=True)
class InteractionRobustnessScenario:
    scenario_id: str; family: str
    level_a: str; level_b: str
    observations: tuple[int, ...]
    gamma: float; preference_strength: float
    coupling_scale: float; variant: str = "aligned"

@dataclass(frozen=True)
class InteractionRobustnessRow:
    family: str; scenario_id: str
    level_a: str; level_b: str
    observations: tuple[int, ...]
    gamma: float; preference_strength: float
    coupling_scale: float; variant: str; lam: float
    total_correlation: float
    joint_entropy: float; marginal_entropy_sum: float
    coupling_term: float; aligned_mass: float
    decomposition_lhs: float; decomposition_rhs: float
    decomposition_residual: float

@dataclass(frozen=True)
class InteractionRobustnessSummary:
    family: str; scenario_id: str
    level_a: str; level_b: str
    tc_max: float; tc_final: float
    residual_max: float; monotone_tc: bool

@dataclass(frozen=True)
class LongHorizonSeedDiagnostic:
    seed: int; habit_accumulation: bool
    tc_final: float; tc_max: float
    tail_kl_window_max: float; adjacent_kl_max: float
    margin_to_tolerance: float
    failure_mode: str

def robustness_scenarios() -> tuple[RobustnessScenario, ...]
def run_robustness_suite(lams=None, *, progress_callback=None) -> list[RobustnessRow]
def summarize_robustness_rows(rows) -> tuple[list[RobustnessScenarioSummary], dict[str, float]]
def coupling_ablation_spec(variant: str) -> CoupledEnsembleSpec
def run_coupling_ablation(lams=None) -> list[CouplingAblationRow]
def summarize_coupling_ablation_rows(rows) -> dict[str, float]
def run_marginal_null_control(lams=None) -> list[MarginalNullControlRow]
def summarize_marginal_null_control_rows(rows) -> dict[str, float]
def run_long_horizon_replicates(seeds=None, *, progress_callback=None) -> list[LongHorizonResult]
def long_horizon_replicate_record(result: LongHorizonResult) -> LongHorizonReplicateRecord
def long_horizon_tc_envelope(results) -> dict[str, list[float]]
def summarize_long_horizon_replicates(results) -> tuple[list[LongHorizonReplicateRecord], dict[str, float]]
def interaction_robustness_scenarios() -> tuple[InteractionRobustnessScenario, ...]
def run_interaction_robustness_suite(lams=None, *, progress_callback=None) -> list[InteractionRobustnessRow]
def summarize_interaction_robustness_rows(rows) -> tuple[list[InteractionRobustnessSummary], dict[str, float]]
def long_horizon_seed_diagnostic(result: LongHorizonResult) -> LongHorizonSeedDiagnostic
def long_horizon_seed_diagnostics(results) -> list[LongHorizonSeedDiagnostic]
def long_horizon_threshold_sensitivity(records, thresholds=None) -> list[LongHorizonThresholdSensitivityRow]
def long_horizon_threshold_pass_rates(records, thresholds=None) -> dict[str, float]
def long_horizon_threshold_sensitivity_summary(records: Sequence[LongHorizonSeedDiagnostic], thresholds=None) -> dict[str, float]
def wilson_score_interval(successes: int, total: int, *, z=1.959963984540054) -> tuple[float, float]
```

The robustness branch runs one-axis-at-a-time perturbations rather than
a Cartesian grid.  The ablation branch fixes the four variants in
`COUPLING_ABLATION_VARIANTS`.  The marginal-null-control branch keeps
each stream's marginal posterior fixed while replacing the joint with
the product of marginals; it is the negative control for the
total-correlation signal.  The replicate branch uses
`LONG_HORIZON_REPLICATE_SEEDS`, reports Wilson intervals around the
pass rate, and leaves the canonical fixed-seed long-horizon figure
untouched.

### `robustness_runner.py`

Pipeline orchestration for robustness CSV/JSON/PNG sidecars (compute →
``robustness_emit`` → plots). Consumed by ``scripts/simulate_robustness.py``.

```python
def run_robustness_pipeline(
    *,
    fig_dir: Path,
    sim_dir: Path,
    data_dir: Path,
    project_root: Path | None = None,
) -> list[Path]
```

### `robustness_core.py` (package-internal λ-loop)

```python
def rows_for_spec(
    spec: CoupledEnsembleSpec,
    observations: Sequence[int],
    lams: Sequence[float],
) -> list[tuple[float, ArrayF, float, float, float, float, float, float, float]]
```

### `robustness_emit.py` (CSV writers and figure metadata)

```python
def snapshot() -> dict[str, Any]
def figure_metadata_dict(source_function: str, *, statistics=None, project_root=None) -> dict[str, str]
def write_robustness_csv(rows, sim_dir: Path) -> Path
def write_ablation_csv(rows, sim_dir: Path) -> Path
def write_interaction_csv(rows, sim_dir: Path) -> Path
def write_long_horizon_replicate_csv(results, records, sim_dir: Path) -> Path
def write_long_horizon_seed_diagnostics_csv(diagnostics, sim_dir: Path) -> Path
def write_long_horizon_threshold_sensitivity_csv(diagnostics, sim_dir: Path) -> Path
def write_marginal_null_control_csv(rows, sim_dir: Path) -> Path
```

### `revertibility_pipeline.py`

Thin orchestration for the m-projection witness sweep. Consumed by
``scripts/simulate_revertibility.py``.

```python
def revertibility_figure_metadata(project_root: Path, source_function: str, **extra: object) -> dict[str, str]
def write_revertibility_csv(path: Path, records: Sequence[RevertibilityRecord]) -> None
def write_revertibility_summary(path: Path, records: Sequence[RevertibilityRecord]) -> dict[str, float]
def run_revertibility_pipeline(*, project_root: Path, fig_dir: Path | None = None, sim_dir: Path | None = None, data_dir: Path | None = None) -> Mapping[str, Path]
def main(project_root: Path | None = None) -> int
```

### `revertibility.py` (T3: m-projection back-to-mean-field witness)

```python
@dataclass(frozen=True)
class RevertibilityRecord:
    lam: float
    multi_information: float
    kl_q_to_mproj: float
    kl_identity_residual: float
    marginal_max_abs_diff: float
    marginals_match: bool
    kl_identity_holds: bool
    revertible: bool

def m_projection_witness(
    q, *, tolerance, kl_identity_tolerance, lam,
) -> RevertibilityRecord
def revertibility_test(
    *, num_streams, coupling_lambda_gen, gamma,
    lambda_values, tolerance, kl_identity_tolerance,
    observations=None,
) -> list[RevertibilityRecord]
def revertibility_summary(records) -> dict[str, float]
def revertibility_kl_equals_multiinformation_witness(records) -> dict[str, object]
```

Hyperparameters consumed: `REVERTIBILITY_LAMBDAS`, `REVERTIBILITY_TOLERANCE`,
`REVERTIBILITY_KL_IDENTITY_TOLERANCE`. CSV sidecar:
``output/simulations/pymdp_revertibility.csv``. Dashboard invariant:
`revertibility_kl_equals_multiinformation`.

---

### `btai_baseline.py` (Branching-Time AIF head-to-head baseline)

Shipped comparison harness for §13 empirical grounding: BTAI
agent on the same K=2 Ising task as the lambda-coupled harness, with
MCTS expansion and per-step joint policy posteriors recovered from
visitation counts. Implements the standard tree-policy interface;
does not reimplement pymdp inference.

```python
@dataclass(frozen=True)
class BTAIScenario:
    horizon: int; mcts_budget: int; seed: int; lambda_value: float

@dataclass
class BTAIObservable:
    joint_posterior: ArrayF; total_correlation: float
    wall_clock_seconds: float; step_index: int

@dataclass
class BTAIRunResult:
    scenario: BTAIScenario
    per_step: list[BTAIObservable]
    final_posterior: ArrayF | None
    final_total_correlation: float | None
    wall_clock_total_seconds: float | None

@dataclass
class BTAITreeNode:  # mutable accumulator; not frozen
    visits: int; value_estimate: float
    children: dict[tuple[int, ...], BTAITreeNode]
    expected_free_energy: float

def joint_marginals(joint: ArrayF) -> tuple[ArrayF, ArrayF]
def total_correlation(joint: ArrayF) -> float
def ucb_score(parent_visits: int, child: BTAITreeNode, exploration: float) -> float
def run_btai_scenario(
    scenario, joint_action_space, expected_free_energy_fn, reference_posterior=None,
) -> BTAIRunResult
def kl_against_reference(measured: ArrayF, reference: ArrayF) -> float
def sample_complexity_exponent(budgets: list[int], kl_curve: list[float]) -> float
def default_mcts_budgets() -> list[int]   # [100, 1000, 10000]
def default_btai_scenarios(lambda_value: float = 1.0) -> list[BTAIScenario]
def pymdp_grounded_efe_fn(
    spec: CoupledEnsembleSpec, observations: Sequence[int],
) -> Callable[[tuple[int, ...]], float]
```

Hyperparameters consumed: `PYMDP_ROLLOUT_STEPS`, `LONG_HORIZON_STEPS`,
`PYMDP_ROLLOUT_SEED`. Tested by ``tests/test_btai_baseline.py``. The
``pymdp_grounded_efe_fn`` helper wires real ``pymdp.agent.Agent``
per-stream EFE into the BTAI tree-policy interface for the end-to-end
real-pymdp integration test.

---

### `adversarial.py` (Q11 adversarial-perturbation harness)

Pre-registered harness for §20 Q11: bounded-norm adversaries
$\|\Delta J\|_\infty \leq \varepsilon$ with three classes
(analytical rank-one worst-case, uniformly random, sparse
single-cell) and the empirical-Lipschitz-vs-analytical-bound gate.

```python
@dataclass(frozen=True)
class AdversarialScenario:
    lambda_value: float; epsilon: float
    adversary_class: str   # "rank_one" | "uniform_random" | "sparse_single"
    seed: int

@dataclass
class AdversarialObservable:
    scenario: AdversarialScenario
    measured_kl_drift: float; analytical_bound: float
    bound_ratio: float; bound_holds: bool

def coupling_covariance(q_lambda: ArrayF, J: ArrayF) -> ArrayF
def variance_under_q(q_lambda: ArrayF, J: ArrayF) -> float
def analytical_lipschitz_bound(
    lambda_value: float, epsilon: float, q_lambda: ArrayF, J: ArrayF,
) -> float
def kl_divergence(p: ArrayF, q: ArrayF) -> float
def rank_one_adversary(q_lambda: ArrayF, J: ArrayF, epsilon: float) -> ArrayF
def uniform_random_adversary(J_shape: tuple[int, ...], epsilon: float, seed: int) -> ArrayF
def sparse_single_adversary(J_shape: tuple[int, ...], epsilon: float, seed: int) -> ArrayF
def build_adversary(
    scenario: AdversarialScenario, q_lambda: ArrayF, J: ArrayF,
) -> ArrayF
def perturbed_posterior(
    q_lambda: ArrayF, J: ArrayF, delta_J: ArrayF, lambda_value: float,
) -> ArrayF
def measure_drift(
    scenario: AdversarialScenario, q_lambda: ArrayF, J: ArrayF,
) -> AdversarialObservable
def default_epsilon_grid() -> list[float]
def default_lambda_grid() -> list[float]
def default_adversarial_scenarios(seed: int = 12345) -> Iterable[AdversarialScenario]
def run_full_sweep(
    q_lambda_provider, J: ArrayF, seed: int = 12345,
) -> list[AdversarialObservable]
def empirical_lipschitz_constant(observables: list[AdversarialObservable]) -> float
```

Tested by ``tests/test_adversarial.py``.

---

### `cross_references.py` (prose ↔ equation ↔ Lean registry)

Maps every public numerical witness to (a) the manuscript theorem /
equation / section it witnesses, (b) the Lean declaration that types
the analytic content, (c) the MathlibProofs declaration that
discharges it at $\mathbb{R}$-level, and (d) the dashboard invariant
that enforces it on every build. The same `CrossReference` strings
can be embedded verbatim in manuscript prose, figure captions, and
PNG `tEXt` metadata — no per-site translation. Pins drift via
`tests/test_cross_references.py`, which fails closed on any rename.

```python
@dataclass(frozen=True)
class CrossReference:
    function: str
    theorem: str | None       # [[THMREF:thm_4_1]] target
    equation: str | None      # [[EQREF:tc_decomp]] target
    section: str              # [[SECREF:decomposition]] target
    lean_declaration: str | None
    mathlib_proof: str | None
    dashboard_invariant: str | None
    description: str

CROSS_REFERENCES: tuple[CrossReference, ...]   # the registry

def cross_reference_for(function_name: str) -> CrossReference | None
def as_metadata_dict(entry: CrossReference) -> dict[str, str]
def to_markdown_table() -> str
```

`python -m simulation.cross_references` dumps the markdown-table
view for inclusion in the manuscript / docs.

### `metrics.py`

Shared TC / alignment metrics used by ``statistics.py`` and
``robustness.py`` so hypercube-corner mass and half-saturation λ
semantics stay canonical.

```python
def aligned_hypercube_mass(q: ArrayF) -> float
def aligned_policy_mass(action_distribution: ArrayF) -> float
def half_saturation_lambda(lams: Sequence[float], tcs: Sequence[float]) -> float | None
def half_saturation_interpolated(lams: Sequence[float], tcs: Sequence[float]) -> tuple[float, float]
```

### `robustness_scenarios.py`

Scenario dataclasses, ``robustness_scenarios()``, ensemble builders
``_spec_for_scenario`` / ``_spec_for_variant`` / ``coupling_ablation_spec``,
and the variant registry ``_VARIANT_BUILDERS``.

### `robustness_stats.py`

```python
def wilson_score_interval(successes: int, total: int, *, z: float | None = None) -> tuple[float, float]
```

---
