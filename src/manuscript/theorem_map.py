"""Per-theorem four-track wiring table — auto-generated body.

Business logic for ``scripts/generate_theorem_map.py``. Reads the
single source of truth (``manuscript/refs/labels.yaml::theorems``)
and emits the auto-generated companion to ``manuscript_map.md``.

The generated file lists every numbered theorem in the manuscript
with its (a) registry label, (b) manuscript token, (c) Lean
qualified name (linked to the live ``.lean`` file), (d) Python
numerical companion, (e) test gate that verifies the witness, and
(f) Mathlib-readiness status.

The Python + test columns come from the static :data:`PYTHON_COMPANION`
and :data:`TEST_GATE` mappings — a single place to update when a new
theorem is added. The Mathlib readiness column comes from the
hand-authored :data:`MATHLIB_READINESS` map (proof-engineering
judgement, not registry metadata).

Drift gate: ``tests/test_theorem_map_generated.py`` asserts that
re-running this generator produces no change to the on-disk file.
"""

from __future__ import annotations

from pathlib import Path

from manuscript.registry import load_registry

# Per-theorem Python numerical companion (relative to ``src/``).
# Each entry is ``(qualified_dotted_path, source_file_relative_to_src)``.
# The source file path is used to construct the markdown link target.
PYTHON_COMPANION: dict[str, tuple[str, str]] = {
    "thm_4_1": ("lean.decomposition.entanglement_decomposition_rhs", "lean/decomposition.py"),
    "thm_4_2": ("lean.decomposition.coupling_pays_for_itself", "lean/decomposition.py"),
    "cor_4_2": ("lean.decomposition.coupling_pays_for_itself", "lean/decomposition.py"),
    "cor_4_3": ("lean.coupling.entangled_log_weight_affine_in_lambda", "lean/coupling.py"),
    "cor_4_4": ("lean.free_energy.total_correlation", "lean/free_energy.py"),
    "thm_4_3": ("lean.decomposition.free_energy_against_entangled_prior", "lean/decomposition.py"),
    "prop_6_1": ("lean.geometry.is_e_flat", "lean/geometry.py"),
    "prop_6_2": ("lean.geometry.m_projection", "lean/geometry.py"),
    "prop_6_3": ("lean.free_energy.total_correlation_via_kl", "lean/free_energy.py"),
    "thm_6_4": ("lean.coupling.entangled_log_weight_affine_in_lambda", "lean/coupling.py"),
    "prop_6_5": ("lean.geometry.pythagorean_residual", "lean/geometry.py"),
    "prop_7_1": ("lean.spectral.schmidt_decomposition", "lean/spectral.py"),
    "prop_7_2": ("lean.spectral.schmidt_rank", "lean/spectral.py"),
    "thm_7_3": ("lean.spectral.tensor_train_ranks", "lean/spectral.py"),
    "thm_8_1": ("lean.heterogeneous.coupling_tax_within_quadratic_bound", "lean/heterogeneous.py"),
    "cor_8_2": ("lean.heterogeneous.coupling_tax_within_quadratic_bound", "lean/heterogeneous.py"),
    "prop_10_1": ("lean.bernoulli_toy.ising_free_energy_curve", "lean/bernoulli_toy.py"),
    # thm_11_1 / prop_11_2 deliberately ABSENT (RedTeam 2026-05-19 R2):
    # their prior mappings (free_energy_against_entangled_prior /
    # coupled_policy_posterior) do NOT exercise the Lean obligation
    # (a (ε,λ₀) concentration quantifier; the embedding VFE-preservation
    # identity). No genuine content-binding Python witness exists; the
    # honest marker is rendered instead of a misleading link.
    "prop_11_3": ("lean.free_energy.total_correlation", "lean/free_energy.py"),
    "roadmap_float_real_residual": (
        "manuscript.variables.build_float_real_residual",
        "manuscript/variables.py",
    ),
}

# Per-theorem test gate (relative to ``tests/``).
TEST_GATE: dict[str, str] = {
    "thm_4_1": "test_decomposition",
    "thm_4_2": "test_decomposition",
    "cor_4_2": "test_decomposition",
    "cor_4_3": "test_coupling",
    "cor_4_4": "test_free_energy",
    "thm_4_3": "test_witness_theorems",
    "prop_6_1": "test_geometry",
    "prop_6_2": "test_geometry",
    "prop_6_3": "test_free_energy",
    "thm_6_4": "test_coupling",
    "prop_6_5": "test_geometry",
    "prop_7_1": "test_spectral",
    "prop_7_2": "test_spectral",
    "thm_7_3": "test_witness_theorems",
    "thm_8_1": "test_heterogeneous",
    "cor_8_2": "test_heterogeneous",
    "prop_10_1": "test_bernoulli_toy",
    "thm_11_1": "test_witness_theorems",
    "prop_11_2": "test_witness_theorems",
    "prop_11_3": "test_free_energy",
    "roadmap_float_real_residual": "test_meta_files_and_float_residual",
}

# Per-theorem Mathlib4 discharge readiness. This table is intentionally
# hand-authored: it captures proof-engineering judgement rather than
# registry metadata. Keep labels exhaustive so new theorem rows force an
# explicit Mathlib integration decision.
MATHLIB_READINESS: dict[str, tuple[str, str, str]] = {
    "thm_4_1": (
        "High",
        "Finite KL / entropy chain rule",
        "Build the `ℝ` + finite-support PMF scaffold, then discharge the KL bookkeeping.",
    ),
    "cor_4_2": (
        "No current need",
        "Boundary algebra already proved",
        "Keep Mathlib out unless the surrounding scalar layer is specialized to `ℝ`.",
    ),
    "cor_4_3": (
        "No current need",
        "Zero-coupling algebra already proved",
        "Keep as a fast boundary theorem; reuse from the Mathlib layer if needed.",
    ),
    "cor_4_4": (
        "Medium",
        "Total-correlation non-negativity / strictness",
        "After KL is available, add the Mathlib proof of `I(q) ≥ 0` and equality cases.",
    ),
    "thm_4_2": (
        "Medium",
        "Closed log-partition identity",
        "Discharge once the finite exponential-family normalizers live over `ℝ`.",
    ),
    "thm_4_3": (
        "High",
        "Convexity of `F(λ)`",
        "Use Mathlib convex-analysis and second-derivative facts after scalar specialization.",
    ),
    "prop_6_1": (
        "No current need",
        "Definition-level e-flat boundary contract",
        "Only revisit if the Mathlib layer introduces a full manifold API.",
    ),
    "prop_6_2": (
        "Medium",
        "m-projection optimality",
        "Tie the boundary marginalization statement to the finite KL minimizer theorem.",
    ),
    "prop_6_3": (
        "High",
        "Total correlation as KL to m-projection",
        "First KL identity after the finite PMF scaffold is in place.",
    ),
    "thm_6_4": (
        "No current need",
        "Affine log-weight forwarder",
        "Reuse the existing boundary forwarder; no analytic discharge needed.",
    ),
    "prop_6_5": (
        "High",
        "KL Pythagorean identity",
        "Discharge from the finite KL chain rule and m-projection optimality.",
    ),
    "prop_7_1": (
        "Medium",
        "Rank-one matrix factorization",
        "Specialize the bipartite joint to Mathlib matrices over `ℝ`.",
    ),
    "prop_7_2": (
        "Medium",
        "Rank semicontinuity",
        "Use Mathlib topology/rank facts once matrix-valued joints are available.",
    ),
    "thm_7_3": (
        "Longer-term",
        "Tensor-train rank envelope",
        "Develop project-local TT rank lemmas on top of Mathlib tensor products.",
    ),
    "thm_8_1": (
        "Medium",
        "Bregman / quadratic coupling-tax envelope",
        "Add local Bregman Taylor lemmas on top of Mathlib Taylor/convexity tools.",
    ),
    "cor_8_2": (
        "Medium",
        "Small-λ tolerance",
        "Derive after the coupling-tax Taylor bound and continuity at zero are proved.",
    ),
    "prop_10_1": (
        "High",
        "Local Taylor concavity at zero",
        "A compact early Mathlib target after `F(λ)` is moved to `ℝ`.",
    ),
    "thm_11_1": (
        "Longer-term",
        "Hierarchical concentration as `λ → ∞`",
        "Use measure/tightness and filter convergence after finite-discrete proofs land.",
    ),
    "prop_11_2": (
        "Longer-term",
        "Sophisticated-inference embedding",
        "Requires project-local recursive-policy infrastructure; Mathlib is supporting substrate.",
    ),
    "prop_11_3": (
        "High",
        "Markov-blanket separation identity",
        "Good first visible discharge once entropy and real arithmetic are wired.",
    ),
    "roadmap_float_real_residual": (
        "Longer-term",
        "Verified Float↔ℝ residual bridge",
        "Flocq/interval formalization; currently bound by dashboard invariants and float_real_residual.json only.",
    ),
}


def _theorem_token(theorem) -> str:
    """Render the manuscript token for a theorem entry; both [[THMREF:]]
    and [[LEAN:]] when a Lean companion exists, [[THMREF:]] only otherwise.
    """
    base = f"`[[THMREF:{theorem.label}]]`"
    if theorem.has_lean_companion:
        return f"{base} / `[[LEAN:{theorem.label}]]`"
    return base


def _lean_link(theorem) -> str:
    """Render the Lean column. ``—`` when the theorem has no companion."""
    if not theorem.has_lean_companion:
        return "—"
    qualified = f"{theorem.lean_module}.{theorem.lean_name}"
    return f"[`{qualified}`](../../lean/ActinfPolicyEntanglement/{theorem.lean_module}.lean)"


def _python_link(label: str) -> str:
    if label not in PYTHON_COMPANION:
        # RedTeam 2026-05-19 R2 — honest marker rather than a misleading
        # link. A row reaches here when no Python function genuinely
        # exercises the Lean obligation's content (the witness Lean body
        # is a typed hypothesis-reexport; mapping it to a thematically
        # adjacent function over-claimed a content link that did not
        # exist — see `faithfulness: typed-witness` in labels.yaml).
        return "— *(typed contract; analytic content assumed — no content-bound Python witness)*"
    qualified, src = PYTHON_COMPANION[label]
    return f"[`{qualified}`](../../src/{src})"


def _test_link(label: str) -> str:
    if label not in TEST_GATE:
        return "—"
    name = TEST_GATE[label]
    return f"[`{name}`](../../tests/{name}.py)"


def _row(theorem) -> str:
    label = theorem.label
    name = theorem.name or theorem.kind
    return (
        f"| {theorem.number} "
        f"| {name} (`{label}`) "
        f"| {_theorem_token(theorem)} "
        f"| {_lean_link(theorem)} "
        f"| {_python_link(label)} "
        f"| {_test_link(label)} "
        f"| {theorem.status or '—'} |"
    )


def _mathlib_row(theorem) -> str:
    readiness, payload, first_action = MATHLIB_READINESS[theorem.label]
    return (
        f"| {theorem.number} | `{theorem.label}` | {theorem.status or '—'} | {readiness} | {payload} | {first_action} |"
    )


def render(refs_dir: Path) -> str:
    """Render the auto-generated theorem-map markdown.

    Args:
        refs_dir: Path to ``manuscript/refs/`` for registry loading.
    """
    registry = load_registry(refs_dir)
    theorems = registry.labels.theorems

    # Sort by manuscript number for stable output. Numbers like "4.1",
    # "11.2" are sorted by their (major, minor) tuple.
    def _key(label: str) -> tuple[int, float]:
        parts = theorems[label].number.split(".")
        major = int(parts[0])
        minor = float(parts[1]) if len(parts) > 1 else 0.0
        return (major, minor)

    ordered = sorted(theorems, key=_key)
    missing = sorted(set(ordered) - set(MATHLIB_READINESS))
    extra = sorted(set(MATHLIB_READINESS) - set(ordered))
    if missing or extra:
        raise RuntimeError(
            f"MATHLIB_READINESS must match labels.yaml::theorems exactly; missing={missing}, extra={extra}"
        )

    body: list[str] = [
        "# Per-theorem four-track wiring (auto-generated)",
        "",
        "**Do not hand-edit.** This file is auto-generated from "
        "[`../../manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml) "
        "by [`../../scripts/generate_theorem_map.py`](../../scripts/generate_theorem_map.py). "
        "Regenerate with:",
        "",
        "```bash",
        "uv run python scripts/generate_theorem_map.py",
        "```",
        "",
        "A CI test (`tests/test_theorem_map_generated.py`) asserts that "
        "re-running the generator produces no diff against this file — any "
        "new theorem, renamed Lean declaration, or changed Python / test "
        "companion is caught at validation time.",
        "",
        "For the full four-track contract see "
        "[`four_track_coherence.md`](four_track_coherence.md). For the "
        "section-by-section map see [`manuscript_map.md`](manuscript_map.md).",
        "",
        "| # | Theorem (registry label) | Manuscript token | Lean (`module.qualified_name`) | Python (numerical witness) | Test gate | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for label in ordered:
        body.append(_row(theorems[label]))
    body.append("")
    body.append(
        "**How to read this table.** Pick a row. The four columns to "
        "its right let you (a) verify the formal statement at the boundary "
        "fragment by clicking the Lean link, (b) inspect a concrete "
        "numerical witness by clicking the Python link, (c) reproduce "
        "the witness check by running the test file, (d) confirm the "
        "proof status. Every theorem in `labels.yaml::theorems` "
        "appears in exactly one row; no row points at vapor."
    )
    body.extend(
        [
            "",
            "## Mathlib4 Discharge Readiness",
            "",
            "This second table is a proof-engineering map, not a claim that "
            "Mathlib-backed proofs already exist. It identifies where a "
            "separate `lean/MathlibProofs/` package should supply witness "
            "structures from Mathlib4 lemmas while the current boundary "
            "fragment remains stock-Lean and fast to audit.",
            "",
            "| # | Label | Current status | Mathlib readiness | Analytic payload | First integration action |",
            "|---|---|---|---|---|---|",
        ]
    )
    for label in ordered:
        body.append(_mathlib_row(theorems[label]))
    body.append("")
    body.append(
        "**Recommended order.** Start with the high-readiness finite-KL and "
        "real-arithmetic rows (`prop_11_3`, `prop_6_3`, `thm_4_1`, "
        "`prop_6_5`), then convex/Taylor rows, then matrix-rank rows. "
        "Tensor-train and recursive sophisticated-inference embeddings are "
        "best treated as project-local developments that use Mathlib as a "
        "substrate rather than as drop-in lemmas."
    )
    body.append("")
    return "\n".join(body)


def write(project_root: Path) -> Path:
    """Render and write ``docs/reference/_theorem_map.md``; return path."""
    out_path = project_root / "docs" / "reference" / "_theorem_map.md"
    refs_dir = project_root / "manuscript" / "refs"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(refs_dir))
    return out_path


__all__ = [
    "PYTHON_COMPANION",
    "TEST_GATE",
    "MATHLIB_READINESS",
    "render",
    "write",
]
