# Python API — `src/gnn/` (Generalized Notation Notation fifth track)

The `gnn/` subpackage is the project-owned implementation of the GNN bridge
(manuscript Supplement §S8). It parses authentic GNN v1.1 source files
(`gnn/*.gnn.md`), reconstructs the policy-entanglement mutual-information curve
from the GNN-declared coupling (the round-trip), emits a Lean typed-structure
contract, and feeds the GNN-sourced manuscript variables. No upstream GNN code
is imported — the parser is spec-conformant and project-owned.

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

## `gnn/runner.py` — round-trip pipeline stage

| Identifier | Kind | Purpose |
|---|---|---|
| `compute_roundtrip` | function | Parse the toy, reconstruct the MI curve, compare to the closed form, and build the (deterministic) sidecar payload incl. the embedded zero-coupling negative-control residual. |
| `run` | function | Execute the GNN round-trip stage; emit the JSON sidecar, the figure, and the emitted Lean file; return a non-zero exit code if the round-trip fails or its negative control is vacuous. |
| `TOY_GNN` | constant | Filename of the K=2 toy GNN source (`bernoulli_toy.gnn.md`). |
| `SIDECAR_NAME` | constant | Output sidecar filename (`gnn_bernoulli_roundtrip.json`). |
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
`to_pymdp_config` and the GNN concordance parity test. See manuscript §S8.
