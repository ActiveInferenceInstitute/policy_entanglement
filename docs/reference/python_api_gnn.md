# Python API — `src/gnn/` (Generalized Notation Notation fifth track)

The `gnn/` subpackage is the project-owned implementation of the GNN bridge
(manuscript Supplement §S8). It parses authentic GNN v1.1 source files
(`gnn/*.gnn.md`), reconstructs the policy-entanglement mutual-information curve
from the GNN-declared coupling (the round-trip), verifies the production pymdp
harness against its GNN specification, emits a Lean typed-structure contract,
and feeds the GNN-sourced manuscript variables. No upstream GNN code is
imported — the parser is project-owned, and its conformance to the real
upstream parser is a test-time check against the pinned release recorded in
`gnn/upstream.json` (`tests/test_gnn_upstream_conformance.py`).

## `gnn/parser.py` — GNN v1.1 parser

| Identifier | Kind | Purpose |
|---|---|---|
| `parse_gnn` | function | Parse GNN source text into a `GnnModel`; raises on missing required sections / grammar errors. |
| `parse_gnn_file` | function | Read and parse a `.gnn.md` file from disk. |
| `GNNParseError` | exception | Raised on a structural/grammatical parse failure (missing section, dimension mismatch, named-dimension reference, missing `type=`). |
| `REQUIRED_SECTIONS` | constant | The tuple of GNN v1.1 sections that must be present (`GNNSection`, `GNNVersionAndFlags`, `ModelName`, `StateSpaceBlock`, `Connections`). |

## `gnn/model.py` — typed model objects

| Identifier | Kind | Purpose |
|---|---|---|
| `GnnModel` | dataclass | A fully parsed GNN model: section, version, name, variables, connections, ontology, model parameters. Accessors: `variable`, `has`, `edges_for`, `num_streams`. |
| `GnnVariable` | dataclass | One `StateSpaceBlock` declaration (name, dims, dtype, comment, parameterized value). Accessors: `size`, `matrix`, `vector`, `scalar`. |
| `GnnConnection` | dataclass | One `Connections` edge (source, target, directed, optional label). |

## `gnn/bridge.py` — GNN → framework binding (executable view)

| Identifier | Kind | Purpose |
|---|---|---|
| `reconstruct_mi_curve` | function | Reconstruct the multi-information curve `I(λ)` from a parsed model via the framework's general `entangled_posterior` + `total_correlation` (never the closed form). |
| `entangled_joint` | function | Reconstruct the entangled joint posterior at coupling `lam` from the GNN-declared priors and coupling. |
| `build_joint_coupling` | function | Assemble the joint coupling tensor over the product policy space (single `J` for K=2; additive pairwise `Jab` for K>2). |
| `per_stream_priors` | function | Return the per-stream habit priors `[E1, E2, ...]` as 1-D arrays. |
| `stream_cardinality` | function | Policy cardinality per stream (from the `pi1` declaration). |
| `to_pymdp_config` | function | Emit a pymdp/hyperparameters-equivalent config dict from a GNN model (the `scripts/gnn_to_pymdp.py` generator). |

## `gnn/harness.py` — production-harness binding (`gnn/production_ensemble.gnn.md`)

| Identifier | Kind | Purpose |
|---|---|---|
| `per_stream_specs` | function | Build one `StreamSpec` per declared stream from the `A{k}`/`B{k}`/`C{k}`/`D{k}` factors, validated against the harness PMF contract. |
| `ensemble_from_gnn` | function | Build the coupled ensemble (streams + joint coupling + `gamma`) from the GNN declarations alone. |
| `production_ensemble` | function | The harness's production ensemble, built from `simulation.hyperparameters` (optional `num_streams` / `coupling_amplitude` / `gamma` overrides for the multi-K family). |
| `EnsembleConformance` | dataclass | Elementwise comparison record: stream counts, policy shapes, per-stream `(A, B, C, D)` max-abs-diffs, coupling and `gamma` diffs, `max_abs_diff`, `conformant`, `to_payload`. |
| `conformance_report` | function | Compare a GNN-declared ensemble against a reference build (zero tolerance) and return the `EnsembleConformance` report. |
| `conformance_negative_control` | function | Max-abs-diff after swapping stream 1's declared control slices — the non-vacuity control for `conformance_report`. |
| `harness_config` | function | Emit the full pymdp-harness configuration (per-stream arrays, joint coupling, `gamma`, cardinalities) from the GNN declarations (`scripts/gnn_to_pymdp.py --harness`). |

## `gnn/upstream.py` — upstream pin + parser-conformance support

| Identifier | Kind | Purpose |
|---|---|---|
| `UpstreamPin` | dataclass | The pinned upstream release identity (`repository`, `tag`, `commit`, `parser_module`, `parser_class`, plus `schema`/`recorded` when the canonical importer-pin schema is declared). |
| `UpstreamPinError` | exception | Raised when the pin is malformed/unusable or an upstream digest payload is incomplete. |
| `load_upstream_pin` | function | Read and validate `gnn/upstream.json` (required keys, optional `gnn-importer-pin/v1` `schema`/`recorded`, HTTPS GitHub URL, stable tag, full commit, dotted module, identifier class; any other field is refused). |
| `default_gnn_root` | function | Conventional sibling checkout path of the upstream GNN repository. |
| `resolve_gnn_root` | function | Resolve the checkout root: explicit `POLICY_ENTANGLEMENT_GNN_ROOT` selection wins, otherwise the sibling checkout. |
| `gnn_checkout_python` | function | Interpreter of the upstream checkout's `.venv` (runs the pinned parser). |
| `checkout_available` | function | Whether the checkout carries both the parser module and its interpreter. |
| `spec_digest` | function | Project-side conformance digest of a parsed model: name, version, time, variables (dims + dtype), connection edges, ontology, `ModelParameters`, parameterized values. |
| `normalize_upstream_digest` | function | Normalize the upstream driver's JSON digest into the project digest shape (raises on incomplete payloads). |
| `digest_divergences` | function | Compare two digests and describe every divergence (empty list = conformance). |
| `DIGEST_DRIVER_SOURCE` | constant | Stdlib-only driver program executed by the pinned checkout's interpreter; prints the upstream parser identity (module/class/version/file/SHA-256) plus one digest per spec. |
| `DEFAULT_UPSTREAM_DIRNAME` | constant | Conventional directory name of the sibling upstream checkout. |
| `ENV_UPSTREAM_ROOT` | constant | Environment variable that explicitly selects a checkout (`POLICY_ENTANGLEMENT_GNN_ROOT`). |
| `PIN_RELATIVE_PATH` | constant | Repo-relative path of the pinned release identity (`gnn/upstream.json`). |
| `PIN_SCHEMA` | constant | Canonical importer-pin schema identifier (`gnn-importer-pin/v1`); a pin that declares it also records the date it was taken. |
| `PARSER_RELATIVE_PATH` | constant | Checkout-relative path of the upstream markdown parser (`src/gnn/parsers/markdown_parser.py`). |

## `gnn/runner.py` — round-trip pipeline stage

| Identifier | Kind | Purpose |
|---|---|---|
| `compute_roundtrip` | function | Parse the toy, reconstruct the MI curve, compare to the closed form, and build the (deterministic) sidecar payload incl. the embedded zero-coupling negative-control residual. |
| `compute_production_conformance` | function | Parse the production spec, compare it elementwise against the hyperparameter-driven harness build, and build the conformance payload incl. the control-swap negative control. |
| `run` | function | Execute the GNN stage; emit both JSON sidecars, the figure, and the emitted Lean file; return a non-zero exit code if the round-trip fails, the production harness drifts, or either negative control is vacuous. |
| `TOY_GNN` | constant | Filename of the K=2 toy GNN source (`bernoulli_toy.gnn.md`). |
| `PRODUCTION_GNN` | constant | Filename of the production harness GNN source (`production_ensemble.gnn.md`). |
| `SIDECAR_NAME` | constant | Round-trip sidecar filename (`gnn_bernoulli_roundtrip.json`). |
| `CONFORMANCE_SIDECAR_NAME` | constant | Production-conformance sidecar filename (`gnn_production_conformance.json`). |
| `FIGURE_NAME` | constant | Output figure filename (`gnn_bernoulli_roundtrip.png`). |
| `LEAN_NAME` | constant | Emitted Lean filename (`BernoulliToyGnn.lean`). |

## `gnn/lean_emit.py` — GNN → Lean typed-structure contract

| Identifier | Kind | Purpose |
|---|---|---|
| `emit_lean_structure` | function | Emit a self-contained, Mathlib-free Lean `structure` contract for a K=2 GNN model. The output is a **typed contract, not a proof** — it certifies the structural signature, promotes no registry row, and type-checks under the stock Lean toolchain. |

## Honesty note

The GNN track reproduces the framework's *structure and numbers*; it does not
prove theorems. The round-trip certifies the gauge-invariant coupling *gap*
(the entangled posterior `q ∝ E·exp(λ J)` is invariant under additive shifts of
`J`); the literal coupling-matrix entries are pinned separately by
`to_pymdp_config`, `harness_config`, and the GNN concordance parity test. The
upstream checks certify *agreement*, not upstream correctness: the conformance
test compares digests of what the two parsers extract from the same bytes, and
the harness test compares the declared arrays against the builder arrays. Two
known-normalization differences are deliberate: the declared version `GNN v1.1`
normalizes to `1.1`, and the project parser accepts the spaced ontology section
name as an alias while upstream ignores it (so shipped specs use the canonical
`## ActInfOntologyAnnotation` spelling, and the test's mutant pins the
difference). See manuscript §S8.
