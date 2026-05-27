# Python API: subpackage `lean/`

*Latest generated audit.* The Lean track has
**17 submodules** (round-3 adds `SpectralWitnesses` and
`ConnectionsWitnesses` on top of round-2's `Convexity` and
`MarkovBlanket`); the Python mirror list below is unchanged — all
four round-2 / round-3 submodules are witness-form and consume Python
helpers already exposed by `bernoulli_toy.py`, `free_energy.py`,
`spectral.py`, `decomposition.py`, and `simulation/inference.py`.
The Python signatures `pythagorean_residual(q, mf_reference)` (Prop
7.5 mirror) and the TT-rank helper
`tensor_train_ranks(q, atol=1e-12)` (replacing the round-0
one-dimensional `schmidt_gap` proxy) are stable.

**Round-3 additions** (not in `src/lean/` — they live under
`scripts/`): `simulate_multi_k.py` (configured multi-K Ising sweep),
`simulate_long_horizon.py` (configured `LONG_HORIZON_STEPS` coupled rollout),
`simulate_revertibility.py` (m-projection KL identity sweep).  These
exercise the new witnesses `schmidtRank_upperSemicontinuous_witness`,
`sparsityRank_tradeoff_witness`, `hierarchicalAIF_lambda_limit_witness`,
and `sophisticatedInference_embedding_witness` numerically; see
[`python_api_simulation.md`](python_api_simulation.md) for the
underlying `src/simulation/` helpers.

Analytical mirrors of the Lean boundary fragment.
Imports: `from lean.<module> import …` (`pythonpath = src/`).

Companion: [`lean_reference.md`](lean_reference.md) (Lean theorem inventory),
[`manuscript_map.md`](manuscript_map.md) (per-theorem four-track wiring),
[`python_api.md`](python_api.md) (subpackage index).

---

## Subpackage `lean/`

### `joint_dist.py`

```python
def is_non_negative(q: ArrayF, atol: float = 0.0) -> bool
def is_pmf(q: ArrayF, atol: float = 1e-9) -> bool
def normalize(q: ArrayF) -> ArrayF                         # raises ValueError on non-positive total mass
def mean_field_to_joint(marginals: Sequence[ArrayF]) -> ArrayF
def joint_marginal(q: ArrayF, k: int) -> ArrayF            # raises IndexError if k out of range
def joint_marginals(q: ArrayF) -> list[ArrayF]
def is_mean_field(q: ArrayF, atol: float = 1e-9) -> bool
def m_projection(q: ArrayF) -> ArrayF
```

### `coupling.py`

```python
def trivial_coupling(shape: Sequence[int]) -> ArrayF
def entangled_prior_unnormalised(mf_prior: Sequence[ArrayF],
                                  coupling_j: ArrayF, lam: float) -> ArrayF
def entangled_prior(mf_prior, coupling_j, lam) -> ArrayF
def entangled_posterior(mf_prior: Sequence[ArrayF],
                         per_stream_G: Sequence[ArrayF],
                         coupling_j: ArrayF, coupling_kc: ArrayF,
                         gamma: float, lam: float) -> ArrayF
def expected_value(q: ArrayF, f: ArrayF) -> float
def entangled_log_weight_affine_in_lambda(coupling_j, coupling_kc,
                                           gamma, pi_index) -> tuple[float, float]
def coupling_log_weight(coupling_j, coupling_kc, gamma, lam) -> ArrayF
```

### `free_energy.py`

```python
def shannon_entropy(p: ArrayF) -> float
def kl_divergence(q: ArrayF, p: ArrayF) -> float           # returns +inf on absolute-continuity violation
def joint_entropy(q: ArrayF) -> float
def marginal_entropy(q: ArrayF, k: int) -> float
def total_correlation(q: ArrayF) -> float
def total_correlation_via_kl(q: ArrayF) -> float
def total_correlation_lean_companion(q: ArrayF, sum_stream_entropies: float) -> float  # Lean-boundary-shaped 2-arg form for parity testing; mirrors ActinfPolicyEntanglement.totalCorrelation
def free_energy(q: ArrayF, prior: ArrayF, G: ArrayF, gamma: float) -> float
def marginal_free_energy(q, mf_prior, per_stream_G, gamma, k) -> float
```

### `geometry.py`

```python
def is_in_mean_field_submanifold(q: ArrayF, atol: float = 1e-9) -> bool
def m_projection_minimises_kl(q: ArrayF,
                               candidate_marginals: Sequence[ArrayF],
                               atol: float = 1e-12) -> bool
def pythagorean_residual(q: ArrayF, mf_reference: Sequence[ArrayF]) -> float
def is_e_geodesic(coupling_j, coupling_kc, gamma, pi_index, lams,
                  atol: float = 1e-9) -> bool
def revertibility(q: ArrayF) -> ArrayF
def coupling_pays_off(mf_prior, per_stream_G, coupling_j, coupling_kc,
                      gamma, lam, atol: float = 1e-12) -> bool
def coupling_log_weight_affine_check(coupling_j, coupling_kc, gamma,
                                      lams, atol: float = 1e-9) -> bool
```

### `spectral.py`

```python
@dataclass(frozen=True)
class Archetype:
    weight: float
    u: ArrayF
    v: ArrayF

def schmidt_rank(q: ArrayF, atol: float = 1e-12) -> int               # K=2 only
def schmidt_decomposition(q: ArrayF, atol: float = 1e-12) -> list[Archetype]
def entanglement_entropy(q: ArrayF, atol: float = 1e-12) -> float
def schmidt_rank_one_iff_mean_field(q: ArrayF, atol: float = 1e-9) -> bool
def tensor_train_ranks(q: ArrayF, atol: float = 1e-12) -> list[int]   # K-general
def entanglement_spectrum(q: ArrayF) -> list[int]                     # alias of tensor_train_ranks
def archetype_marginal_pattern(arch: Archetype, atol: float = 1e-12)
        -> tuple[ArrayF, ArrayF]
def entanglement_entropy_per_cut(q: ArrayF, k: int,
                                 atol: float = 1e-12) -> float        # per-cut TT bond entropy
def mps_decomposition(q: ArrayF, atol: float = 1e-12) -> list[ArrayF]  # left-canonical TT-SVD factors
```

### `bernoulli_toy.py`

```python
def ising_coupling(shape: tuple[int, int] = (2, 2)) -> ArrayF
def symmetric_mean_field_prior() -> tuple[ArrayF, ArrayF]
def ising_mutual_information(lam: float) -> float
def ising_joint_posterior(lam: float) -> ArrayF
def empirical_mutual_information(lam: float) -> float
def empirical_mutual_information_montecarlo(lam: float, n_samples: int,
                                            seed: int) -> float
def optimal_lambda(delta: float, delta_max: float = 1.0) -> float
def ising_free_energy_curve(lam: float, utility: float) -> float
def coupling_phase_at(lam: float, lam_c1: float = 0.5,
                      lam_c2: float = 2.5) -> str
def is_mean_field_at_zero(atol: float = 1e-9) -> bool
```

### `heterogeneous.py`

```python
class InferenceMode(Enum):
    VFE = "vfe"
    EFE = "efe"
    SOPHISTICATED = "sophisticated"

def is_planning_stream(mode: InferenceMode) -> bool
def is_reflexive_stream(mode: InferenceMode) -> bool
def is_purely_reflexive(modes: Sequence[InferenceMode]) -> bool
def is_purely_planning(modes: Sequence[InferenceMode]) -> bool
def is_heterogeneous(modes: Sequence[InferenceMode]) -> bool
def coupling_norm_sq(coupling_kc: ArrayF) -> float
def fixed_reflexive_posterior(mf_prior, per_stream_G, coupling_j,
                               coupling_kc, gamma, lam, modes) -> ArrayF
def coupling_tax(mf_prior, per_stream_G, coupling_j, coupling_kc,
                  gamma, lam, modes) -> float
def quadratic_bound_curvature(mf_prior, per_stream_G, coupling_j,
                               coupling_kc, gamma, modes,
                               lam_probe: float = 1e-2) -> float
def coupling_tax_within_quadratic_bound(mf_prior, per_stream_G, coupling_j,
                                         coupling_kc, gamma, lam, modes,
                                         safety_factor: float = 4.0,
                                         lam_probe: float = 1e-2) -> bool
```

### `decomposition.py`

```python
@dataclass(frozen=True)
class DecompositionTerms:
    sum_marginal_free_energies: float
    coupling_cost_term: float
    coupling_prior_term: float
    total_correlation_gain: float  # equals `I(q)`; see `multi_information_term`
    @property
    def multi_information_term(self) -> float
    @property
    def total(self) -> float

def sum_marginal_free_energies(q, mf_prior, per_stream_G, gamma) -> float
def coupling_cost_term(q, coupling_kc, gamma, lam) -> float
def coupling_prior_term(q, coupling_j, mf_prior, lam) -> float
def multi_information_term(q) -> float
def total_correlation_gain(q) -> float  # Lean mirror; synonym of multi_information_term
def entanglement_decomposition_rhs(q, mf_prior, per_stream_G,
                                    coupling_j, coupling_kc,
                                    gamma, lam) -> DecompositionTerms
def decomposition_at_zero(q, mf_prior, per_stream_G,
                           coupling_j, coupling_kc,
                           gamma) -> DecompositionTerms        # Cor 4.3 mirror
def free_energy_against_entangled_prior(q, mf_prior, per_stream_G, coupling_j,
                                         coupling_kc, gamma, lam) -> float
def coupling_pays_for_itself(q_lam, q_zero, atol: float = 1e-12) -> bool
```

### `invariants.py`

Pure-compute invariant builders driving the interactive simulation
dashboard (`scripts/build_dashboard.py`) and the plaintext invariants
report (`output/reports/dashboard_invariants.txt`). Every check is
configurable through :class:`SweepGrid` plus optional utility / phase
threshold arguments — change a knob and the same flow re-validates the
new regime. Each builder returns a list of
:class:`reporting.interactive_dashboard.Invariant`.

```python
@dataclass(frozen=True)
class SweepGrid:
    lam_min: float
    lam_max: float
    num: int
    def values(self) -> ArrayF

@dataclass(frozen=True)
class DecompositionSweepPoint:
    lam: float
    residual: float
    lhs: float
    rhs_total: float

def decomposition_sweep_points(grid: SweepGrid) -> list[DecompositionSweepPoint]

def ising_invariants(grid: SweepGrid, agreement_tol: float = 1e-9) -> list[Invariant]
def free_energy_invariants(grid: SweepGrid,
                           utilities: Sequence[float] = (0.0, 0.5, 1.0, 2.0)) -> list[Invariant]
def optimal_lambda_invariants(deltas: Sequence[float] = (0.0, 0.1, 0.5, 0.9),
                              delta_max: float = 1.0) -> list[Invariant]
def phase_invariants(lam_c1: float = 0.5, lam_c2: float = 2.5) -> list[Invariant]
def marginal_invariants(grid: SweepGrid) -> list[Invariant]
def all_invariants(grid: SweepGrid, *, utilities=..., optimal_deltas=...,
                   optimal_delta_max=1.0, lam_c1=0.5, lam_c2=2.5,
                   agreement_tol=1e-9,
                   coupling_pays_threshold=0.1) -> list[Invariant]
def decomposition_invariants(grid: SweepGrid) -> list[Invariant]
def decomposition_invariants_from_points(
    points: Sequence[DecompositionSweepPoint],
) -> list[Invariant]
def coupling_pays_invariants(grid: SweepGrid,
                             lam_threshold: float = 0.1) -> list[Invariant]
def affine_log_weight_invariants(
    lam_grid: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0),
) -> list[Invariant]
```

### `build_gate.py`

Lean boundary-fragment build gate consumed by `scripts/build_lean.py`.
Runs `lake build` and enforces the sorry/axiom/unsafe/Mathlib-import budget.

```python
def scrape_lake_warnings(stderr_text: str) -> list[dict[str, str]]
def emit_infra_log(rows: list[dict[str, str]], *, log_path: Path) -> None
def count_sorries(lean_dir: Path, *, exclude_subtree: Path) -> int
def count_axioms(lean_dir: Path, *, exclude_subtree: Path) -> int
def count_disallowed(lean_dir: Path, *, exclude_subtree: Path) -> int
def count_mathlib_imports(lean_dir: Path, *, exclude_subtree: Path) -> int
```

### `mathlib_proofs_gate.py`

MathlibProofs build + `#print axioms` audit consumed by
`scripts/build_mathlib_proofs.py`.

```python
ALLOWED_AXIOMS: set[str]
KEYSTONE_THEOREMS: tuple[str, ...]
FORBIDDEN_LOCAL_TOKENS: tuple[str, ...]
def declared_keystones(mathlib_src: Path) -> list[str]
def axiom_audit(
    mathlib_dir: Path,
    mathlib_src: Path,
    *,
    project_root: Path | None = None,
) -> list[str]
def local_hygiene_issues(mathlib_dir: Path, project_root: Path) -> list[str]
def local_warning_issues(output: str) -> list[str]
def run_mathlib_proofs_gate(project_root: Path) -> int
```

### `phase_constants.py`

Manuscript phase-transition λ defaults shared with `simulation/hyperparameters.py`:

```python
PHASE_LAMBDA_C1: float
PHASE_LAMBDA_C2: float
```

---
