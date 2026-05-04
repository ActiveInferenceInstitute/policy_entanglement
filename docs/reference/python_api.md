# Python API reference

Per-function signatures and contracts for the four subpackages of
[`../../src/`](../../src/):

* [`src/lean/`](../../src/lean/) — analytical mirrors of the Lean modules.
* [`src/simulation/`](../../src/simulation/) — pymdp 1.0.1 POMDP harness.
* [`src/visualizations/`](../../src/visualizations/) — reusable plotting helpers.
* [`src/manuscript/`](../../src/manuscript/) — auto-injection + validation toolkit.

Bare-module imports (`from joint_dist import …`,
`from specs import …`, `from heatmaps import …`,
`from registry import …`) are supported because all four subpackages
are on `pythonpath` (see `pyproject.toml`).

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
                                  coupling_J: ArrayF, lam: float) -> ArrayF
def entangled_prior(mf_prior, coupling_J, lam) -> ArrayF
def entangled_posterior(mf_prior: Sequence[ArrayF],
                         per_stream_G: Sequence[ArrayF],
                         coupling_J: ArrayF, coupling_Kc: ArrayF,
                         gamma: float, lam: float) -> ArrayF
def expected_value(q: ArrayF, f: ArrayF) -> float
def entangled_log_weight_affine_in_lambda(coupling_J, coupling_Kc,
                                           gamma, pi_index) -> tuple[float, float]
def coupling_log_weight(coupling_J, coupling_Kc, gamma, lam) -> ArrayF
```

### `free_energy.py`

```python
def shannon_entropy(p: ArrayF) -> float
def kl_divergence(q: ArrayF, p: ArrayF) -> float           # returns +inf on absolute-continuity violation
def joint_entropy(q: ArrayF) -> float
def marginal_entropy(q: ArrayF, k: int) -> float
def total_correlation(q: ArrayF) -> float
def total_correlation_via_kl(q: ArrayF) -> float
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
def is_e_geodesic(coupling_J, coupling_Kc, gamma, pi_index, lams,
                  atol: float = 1e-9) -> bool
def revertibility(q: ArrayF) -> ArrayF
def coupling_pays_off(mf_prior, per_stream_G, coupling_J, coupling_Kc,
                      gamma, lam, atol: float = 1e-12) -> bool
def coupling_log_weight_affine_check(coupling_J, coupling_Kc, gamma,
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
```

### `bernoulli_toy.py`

```python
def ising_coupling(shape: tuple[int, int] = (2, 2)) -> ArrayF
def symmetric_mean_field_prior() -> tuple[ArrayF, ArrayF]
def ising_mutual_information(lam: float) -> float
def ising_joint_posterior(lam: float) -> ArrayF
def empirical_mutual_information(lam: float) -> float
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
def coupling_norm_sq(coupling_Kc: ArrayF) -> float
def fixed_reflexive_posterior(mf_prior, per_stream_G, coupling_J,
                               coupling_Kc, gamma, lam, modes) -> ArrayF
def coupling_tax(mf_prior, per_stream_G, coupling_J, coupling_Kc,
                  gamma, lam, modes) -> float
def quadratic_bound_curvature(mf_prior, per_stream_G, coupling_J,
                               coupling_Kc, gamma, modes,
                               lam_probe: float = 1e-2) -> float
def coupling_tax_within_quadratic_bound(mf_prior, per_stream_G, coupling_J,
                                         coupling_Kc, gamma, lam, modes,
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
    total_correlation_gain: float
    @property
    def total(self) -> float

def sum_marginal_free_energies(q, mf_prior, per_stream_G, gamma) -> float
def coupling_cost_term(q, coupling_Kc, gamma, lam) -> float
def coupling_prior_term(q, coupling_J, mf_prior, lam) -> float
def total_correlation_gain(q) -> float
def entanglement_decomposition_rhs(q, mf_prior, per_stream_G,
                                    coupling_J, coupling_Kc,
                                    gamma, lam) -> DecompositionTerms
def decomposition_at_zero(q, mf_prior, per_stream_G,
                           coupling_J, coupling_Kc,
                           gamma) -> DecompositionTerms        # Cor 4.3 mirror
def free_energy_against_entangled_prior(q, mf_prior, coupling_J,
                                         coupling_Kc, gamma, lam) -> float
def coupling_pays_for_itself(q_lam, q_zero, atol: float = 1e-12) -> bool
```

---

## Subpackage `simulation/`

`pymdp` 1.0.1 is an optional dep (`uv sync --group sim`); the
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
    coupling_J: ArrayF; coupling_Kc: ArrayF; gamma: float = 1.0
    def K() -> int; policy_shape() -> tuple[int, ...]; validate() -> None
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
                        K: int = 2, gamma: float = 1.0) -> CoupledEnsembleSpec
```

### `agents.py`

```python
PYMDP_INSTALL_HINT: str
def pymdp_available() -> bool
def build_pymdp_agent(spec: StreamSpec, *,
                      policy_len: int = 1, gamma: float = 1.0,
                      inference_algo: str = "fpi") -> pymdp.agent.Agent
def build_pymdp_agents(spec: CoupledEnsembleSpec, **kwargs) -> list[Agent]
```

### `inference.py`

```python
def per_stream_efe(spec, observations) -> list[ArrayF]
def per_stream_policy_posterior(spec, observations) -> list[ArrayF]
def coupled_policy_posterior(spec, observations, lam: float) -> ArrayF
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

def simulate_coupled_rollout(spec, *, T: int = 8, lam: float = 1.0,
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
    def K(self) -> int

def lambda_sweep(spec, observations, lams) -> list[LambdaSweepResult]
def total_correlation_curve(spec, observations, lams) -> ArrayF
def marginal_trajectory(rollout: Rollout, k: int) -> ArrayF
```

---

## Subpackage `visualizations/`

`seaborn`, `networkx`, `plotly` are optional deps (`uv sync --group viz`);
the `graphs.plot_coupling_graph` helper returns `None` when networkx is
missing.  All other helpers work on stock matplotlib.

### `setup.py`

```python
def deterministic_setup(seed: int = 42, dpi: int = 150,
                         save_dpi: int = 300) -> None
def ensure_outdir(path: Path | str) -> Path
```

### `heatmaps.py`

```python
def plot_lambda_utility_heatmap(*, lams, utilities, score: ArrayF,
                                 title: str, cbar_label: str,
                                 out_path, cmap: str = "viridis") -> Path
def plot_schmidt_entropy_surface(*, lams, utilities, entropies: ArrayF,
                                  out_path) -> Path
```

### `joint_plots.py`

```python
def plot_joint_heatmap_with_marginals(*, q: ArrayF, title: str, out_path,
                                       xticklabels=None, yticklabels=None) -> Path
```

### `spectral_plots.py`

```python
def plot_archetype_dendrogram(*, weights, overlap_matrix: ArrayF, out_path) -> Path
def plot_tensor_train_rank_surface(*, K_values, rank_profiles, out_path) -> Path
```

### `trajectory_plots.py`

```python
def plot_rollout_marginals(*, marginals_per_stream: Sequence[ArrayF],
                            titles: Sequence[str],
                            total_correlations: ArrayF,
                            out_path) -> Path
```

### `graphs.py`

```python
def has_seaborn() -> bool
def has_networkx() -> bool
def plot_coupling_graph(*, coupling_J: ArrayF, out_path,
                         threshold: float = 0.05) -> Path | None
```

### `geodesic.py`

```python
def plot_kl_geodesic_in_simplex(*, lams, joints: Sequence[ArrayF],
                                 out_path) -> Path
def plot_lambda_star_locus(*, utilities, gammas,
                            lambda_star: ArrayF, out_path) -> Path
```

### `log_weight.py`

```python
def plot_log_weight_flow(*, lams, log_weights: ArrayF, out_path,
                          pi_labels: Sequence[str] | None = None) -> Path
```

---

## Subpackage `manuscript/`

Auto-injection + validation toolkit consumed by
[`scripts/inject_manuscript_variables.py`](../../scripts/inject_manuscript_variables.py)
and [`scripts/validate_manuscript.py`](../../scripts/validate_manuscript.py).

### `registry.py`

```python
@dataclass(frozen=True)
class Figure:
    label: str; path: str; caption: str; short: str
    sections: tuple[str, ...]; source: str; number: int

@dataclass(frozen=True)
class Equation:
    label: str; latex: str; name: str
    sections: tuple[str, ...]; number: int

@dataclass(frozen=True)
class Citation:
    key: str; authors: str; year: int; title: str; venue: str
    volume: str = ""; pages: str = ""; doi: str = ""; url: str = ""
    note: str = ""; topic: str = ""
    def render_inline(self) -> str            # "(Author year)"
    def render_bibliography(self) -> str       # Markdown bullet line

@dataclass(frozen=True)
class Section:
    label: str; number: str; title: str; file: str; parent: str

@dataclass(frozen=True)
class TheoremEntry:
    label: str; kind: str; number: str; name: str; section: str
    def render_block(self) -> str             # "**Kind N (Name).**"
    def render_inline(self) -> str            # "Kind N"

@dataclass(frozen=True)
class LabelsRegistry:
    figures: dict[str, Figure]
    equations: dict[str, Equation]
    sections: dict[str, Section]              # added in v0.3
    theorems: dict[str, TheoremEntry]         # added in v0.3

@dataclass(frozen=True)
class CitationRegistry:
    entries: dict[str, Citation]
    topic_order: tuple[str, ...]
    topic_titles: dict[str, str]

@dataclass(frozen=True)
class Registry:
    labels: LabelsRegistry
    citations: CitationRegistry

def load_labels(path: Path) -> LabelsRegistry
def load_citations(path: Path) -> CitationRegistry
def load_registry(refs_dir: Path) -> Registry
```

### `tokens.py`

```python
FIG_RE: re.Pattern        # [[FIG:label]]
FIGREF_RE: re.Pattern     # [[FIGREF:label]]
EQ_RE: re.Pattern         # [[EQ:label]]
EQREF_RE: re.Pattern      # [[EQREF:label]]
SEC_RE: re.Pattern        # [[SEC:label]]      → "§<n> <title>"
SECREF_RE: re.Pattern     # [[SECREF:label]]   → "§<n>"
THM_RE: re.Pattern        # [[THM:label]]      → "**<Kind> <n> (<Name>).**"
THMREF_RE: re.Pattern     # [[THMREF:label]]   → "<Kind> <n>"
VAR_RE: re.Pattern        # [[VAR:key]] or [[VAR:key:fmt]]
CITATION_RE: re.Pattern   # [@citekey]
CITELIST_RE: re.Pattern   # [[CITELIST:topic]]

def iter_tokens(text: str) -> Iterator[tuple[str, str, tuple[int, int]]]
```

### `renderer.py`

```python
@dataclass
class RenderResult:
    text: str
    missing_figures: list[str]
    missing_equations: list[str]
    missing_citations: list[str]
    missing_variables: list[str]
    @property
    def is_complete(self) -> bool

def render_section(text: str, *, registry: Registry,
                   variables: Mapping[str, Any],
                   manuscript_dir: Path) -> RenderResult

def render_all(*, manuscript_dir: Path, output_dir: Path,
               registry: Registry,
               variables_path: Path) -> dict[str, RenderResult]
```

### `bibliography.py`

```python
def auto_bibliography(reg: CitationRegistry,
                      topic: str = "all") -> str
```

### `lean_extract.py`

Auto-extracts Lean theorem signatures from
`lean/ActinfPolicyEntanglement/*.lean` so `[[LEAN:label]]` tokens can
embed live source.  Pure-string parser (no Lean toolchain required).

```python
@dataclass(frozen=True)
class LeanSnippet:
    label: str            # registry label (`thm_4_1`, …)
    module: str           # Lean module name (`Decomposition`)
    qualified_name: str   # full Lean name (`Bipartite.<...>`)
    keyword: str          # `theorem` / `def` / `lemma` / `instance`
    docstring: str
    body: str
    file_path: Path
    start_line: int

def load_lean_snippets(lean_dir: Path) -> dict[tuple[str, str], LeanSnippet]
def render_lean_snippet(snip: LeanSnippet, *, status: str = "") -> str
```

### `validation.py`

```python
@dataclass
class ManuscriptValidationReport:
    section_files: list[str]
    undefined_tokens: dict[str, list[tuple[str, str]]]
    broken_links: dict[str, list[str]]
    missing_figure_files: dict[str, list[str]]
    out_of_range_variables: dict[str, str]
    missing_headings: list[str]
    empty_captions: list[str]
    @property
    def is_clean(self) -> bool

def section_paths(manuscript_dir: Path) -> list[Path]
def validate_undefined_tokens(text, registry, variables) -> list[tuple[str, str]]
def validate_hyperlinks(text: str, base: Path) -> list[str]
def validate_figure_files(text: str, manuscript_dir: Path) -> list[str]
def validate_variables_against_ranges(variables, ranges) -> dict[str, str]
def validate_manuscript_tree(*, manuscript_dir, registry, variables,
                              variable_ranges=None) -> ManuscriptValidationReport
```

---

## Conventions

* `ArrayF = numpy.typing.NDArray[numpy.float64]`.
* `Sequence[ArrayF]` is used for the K-tuple of per-stream marginals
  (or per-stream EFEs).
* Joint distributions are dense `ndarray`s with one axis per stream.
* Errors raised: `ValueError` for shape / value mismatches,
  `IndexError` for out-of-range indices.
* Determinism: every randomness-bearing helper takes an explicit seed;
  module-level RNGs are forbidden.
