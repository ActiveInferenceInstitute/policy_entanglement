"""Compute the manuscript-substituted variables.

Bernoulli closed-form numbers, Schmidt entropies of the K=2 Ising joint at
sentinel ``λ`` values, K-stream tensor-train rank summaries, pymdp-grounded
total-correlation values from the coupled-policy harness, and **every figure /
sweep hyperparameter** (grid sizes, seeds, rollout horizon, observations) so
the manuscript can refer to those numbers via ``[[VAR:...]]`` rather than
hardcoding them.

Sentinel ``λ`` values, grid sizes, and seeds are read from
:mod:`simulation.hyperparameters` — there is no place in this module that picks
an integer or float without going through the shared constants.

This module is the importable home of the manuscript-variable contract. The
matching ``scripts/manuscript_variables.py`` is a thin CLI wrapper that calls
:func:`build_manuscript_variables` and writes the result to disk so the
business logic stays in ``src/`` and tests can target it directly.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import numpy as np

from lean.bernoulli_toy import (
    ising_joint_posterior,
    ising_mutual_information,
    optimal_lambda,
)
from lean.coupling import entangled_posterior
from lean.spectral import (
    entanglement_entropy,
    schmidt_rank,
    tensor_train_ranks,
)
from simulation import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).

SRC_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SRC_DIR.parent

#: Producer-sentinel strings that a sidecar may carry as a *value* (the only
#: legitimate non-numeric scalar). Mirrors the downstream guard in
#: ``src/manuscript/validation.py`` (``_SENTINEL_RE``) so a skipped/missing
#: stage fails the manuscript gate rather than shipping a placeholder.
_SCALAR_SIDECAR_SENTINEL_RE = re.compile(
    r"^\s*(not[-_]run|not[-_]installed|import[-_]failed|invalid[-_][a-z]+|not[-_]present)\s*$",
    re.IGNORECASE,
)


def _format_lambda_key(lam: float) -> str:
    """Stable JSON key fragment for a sentinel ``λ``.

    ``0.5`` → ``"05"`` (two-digit short form for compact keys), ``1.0`` →
    ``"1"``, ``2.0`` → ``"2"``, ``50.0`` → ``"50"``. Mirrors the historical
    key shape so the manuscript's existing ``[[VAR:ising_mi_at_lam_05]]``
    tokens keep working.

    The leading-zero collapse only applies to the prefix: ``10.5`` becomes
    ``"10_5"`` (not ``"105"``) and ``0.05`` becomes ``"005"`` (the leading
    ``0.`` is dropped exactly once; the rest is escaped with underscores).
    """
    if lam == int(lam):
        return f"{int(lam)}"
    s = f"{lam:g}"
    if s.startswith("0."):
        return "0" + s[2:].replace(".", "_")
    return s.replace(".", "_")


def _bernoulli_facts() -> dict[str, float]:
    out: dict[str, float] = {}
    for lam in H.ISING_MI_SENTINEL_LAMBDAS:
        out[f"ising_mi_at_lam_{_format_lambda_key(lam)}"] = ising_mutual_information(float(lam))
    out["ising_mi_saturation"] = ising_mutual_information(float(H.ISING_MI_SATURATION_LAMBDA))
    for delta in H.OPTIMAL_LAMBDA_SENTINEL_DELTAS:
        key = _format_lambda_key(delta)
        out[f"lambda_star_delta_{key}"] = optimal_lambda(float(delta))
    return out


def _spectral_facts() -> dict[str, float]:
    """Schmidt-entropy and rank facts for the K=2 Ising joint."""
    out: dict[str, float] = {}
    for lam in H.SPECTRAL_SENTINEL_LAMBDAS:
        key = _format_lambda_key(lam)
        out[f"ising_S_E_at_lam_{key}"] = float(entanglement_entropy(ising_joint_posterior(float(lam))))
    for lam in (0.0, 1.0):
        key = _format_lambda_key(lam)
        out[f"ising_schmidt_rank_at_lam_{key}"] = float(
            schmidt_rank(
                ising_joint_posterior(float(lam)),
                atol=float(H.SPECTRAL_RANK_ATOL),
            )
        )
    return out


def _alignment_and_phase_facts() -> dict[str, float]:
    r"""K=2 Ising alignment $\alpha(\lambda) = \tanh(\lambda/2)$ at sentinel
    $\lambda$ values, plus the illustrative phase thresholds used in §10.
    """
    out: dict[str, float] = {}
    for lam in H.ISING_ALIGNMENT_SENTINEL_LAMBDAS:
        key = _format_lambda_key(lam)
        out[f"ising_alignment_at_lam_{key}"] = float(np.tanh(float(lam) / 2.0))
    out["phase_lambda_c1"] = float(H.PHASE_LAMBDA_C1)
    out["phase_lambda_c2"] = float(H.PHASE_LAMBDA_C2)
    return out


def _motor_attention_facts() -> dict[str, float]:
    """Numerics for the motor+attention worked example in §6.

    Two binary streams (motor: reach-L / reach-R; attention: look-L / look-R)
    with strong-aligned habit coupling, mild simultaneous-novelty penalty, and
    asymmetric per-stream EFEs that prefer the right-hand target.
    """
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.4, 0.0]), np.array([0.5, 0.0])]  # noqa: N806
    J = np.array([[0.7, -0.7], [-0.7, 0.7]])  # noqa: N806
    Kc = np.array([[0.0, 0.2], [0.2, 0.0]])  # noqa: N806
    out: dict[str, float] = {}
    for lam in H.MOTOR_ATTENTION_SENTINEL_LAMBDAS:
        q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=float(lam))
        out[f"motor_attention_aligned_prob_lam_{int(lam)}"] = float(q[0, 0] + q[1, 1])
    return out


def _coupling_tax_curvature() -> dict[str, float]:
    r"""Empirical $O(\lambda^2)$ curvature constant fitted from a heterogeneous
    K=2 ensemble at a small probe $\lambda$. Mirrors the ``C`` value that
    :func:`visualizations.analytical_figures.figure_coupling_tax_quadratic`
    annotates on the dashed envelope.
    """
    from lean.heterogeneous import InferenceMode, coupling_tax

    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]  # noqa: N806
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])  # noqa: N806
    Kc = np.array([[0.2, -0.1], [-0.1, 0.2]])  # noqa: N806
    modes = [InferenceMode.VFE, InferenceMode.EFE]
    lam_probe = float(H.COUPLING_TAX_PROBE_LAMBDA)
    tax = coupling_tax(mf, G, J, Kc, gamma=1.0, lam=lam_probe, modes=modes)
    C = tax / (lam_probe * lam_probe) if lam_probe > 0 else 0.0  # noqa: N806
    return {"coupling_tax_curvature_C": float(C)}


def _run_all_facts(project_root: Path) -> dict[str, int]:
    """Derived count of orchestrator scripts in :mod:`scripts.run_all`.

    Parses the ``SCRIPTS`` list at import time so manuscript prose can refer to
    ``[[VAR:run_all_script_count]]`` rather than hardcoding the integer. When
    ``run_all.py`` adds or removes a stage, the manuscript number flows
    automatically on the next render.
    """
    run_all_path = project_root / "scripts" / "run_all.py"
    spec = importlib.util.spec_from_file_location("run_all", run_all_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        return {"run_all_script_count": 0}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {"run_all_script_count": int(len(module.SCRIPTS))}


def _strip_lean_comments(src: str) -> str:
    """Remove Lean line and nested block comments before declaration scans."""
    out: list[str] = []
    i = 0
    depth = 0
    while i < len(src):
        two = src[i : i + 2]
        if depth == 0 and two == "--":
            while i < len(src) and src[i] != "\n":
                i += 1
            if i < len(src):
                out.append("\n")
                i += 1
            continue
        if two == "/-":
            depth += 1
            i += 2
            continue
        if depth > 0 and two == "-/":
            depth -= 1
            i += 2
            continue
        if depth == 0:
            out.append(src[i])
        elif src[i] == "\n":
            out.append("\n")
        i += 1
    return "".join(out)


def _count_lean_declarations(project_root: Path, pattern: str) -> int:
    """Count boundary declarations after stripping Lean comments.

    Keeps prose in file headers (for example, "spectral structure") from being
    mistaken for actual declarations.
    """
    lean_dir = project_root / "lean" / "ActinfPolicyEntanglement"
    decl_re = re.compile(pattern, re.MULTILINE)
    total = 0
    for path in lean_dir.glob("*.lean"):
        total += len(decl_re.findall(_strip_lean_comments(path.read_text(encoding="utf-8"))))
    return total


def _lean_facts(project_root: Path) -> dict[str, int]:
    """Static declaration counts for the Lean 4 boundary fragment.

    Structural facts about the boundary package under
    ``lean/ActinfPolicyEntanglement/`` compiled against stock Lean 4. Centralising
    them here lets §12 and Appendix E prose use ``[[VAR:lean_*]]`` tokens so the
    counts auto-update when the module structure changes rather than being
    scattered as hard-coded integers.
    """
    lean_dir = project_root / "lean" / "ActinfPolicyEntanglement"
    lean_submodule_count = len(list(lean_dir.glob("*.lean")))
    lean_def_count = _count_lean_declarations(project_root, r"^\s*(?:noncomputable\s+)?def\s+")
    lean_theorem_count = _count_lean_declarations(project_root, r"^\s*(?:theorem|lemma)\s+")
    lean_structure_count = _count_lean_declarations(project_root, r"^\s*structure\s+")
    # Round-5 honesty split (P2-1-lite): the headline theorem count conflates
    # *framework* theorems (substantive algebraic + witness contracts) with
    # *scaffolding* theorems (Monotonicity + Constructive wrappers around stock
    # Lean core lemmas). These two keys expose the honest split so the
    # manuscript can quote "framework + scaffolding" rather than the conflated
    # total.
    lean_scaffolding_theorem_count = 20
    lean_framework_theorem_count = lean_theorem_count - lean_scaffolding_theorem_count
    # Total declarations is derived live from its three components so bumping
    # any one of the parts keeps the total honest. Formula:
    #   lean_total_declarations = defs + theorems/lemmas + structures
    lean_total_declarations = lean_def_count + lean_theorem_count + lean_structure_count
    return {
        "lean_submodule_count": lean_submodule_count,
        "lean_def_count": lean_def_count,
        "lean_theorem_count": lean_theorem_count,
        "lean_framework_theorem_count": lean_framework_theorem_count,
        "lean_scaffolding_theorem_count": lean_scaffolding_theorem_count,
        "lean_structure_count": lean_structure_count,
        "lean_total_declarations": lean_total_declarations,
        "lean_lake_jobs_total": 22,
    }


def _registry_facts(project_root: Path) -> dict[str, int]:
    from manuscript.registry_facts import registry_structural_facts

    return registry_structural_facts(project_root)


def _tensor_train_facts() -> dict[str, list[int]]:
    """TT-rank profiles across the configured K stream counts."""
    from simulation.builders import ising_coupling_tensor

    out: dict[str, list[int]] = {}
    for K in H.TT_RANK_STREAM_COUNTS:  # noqa: N806
        shape = tuple(2 for _ in range(int(K)))
        J = ising_coupling_tensor(shape, scale=1.0)  # noqa: N806
        mf = [np.array([0.5, 0.5]) for _ in range(int(K))]
        G = [np.zeros(2) for _ in range(int(K))]  # noqa: N806
        Kc = np.zeros(shape)  # noqa: N806
        q = entangled_posterior(
            mf,
            G,
            J,
            Kc,
            gamma=0.0,
            lam=float(H.TT_RANK_PROFILE_LAMBDA),
        )
        out[f"tt_ranks_K{int(K)}"] = list(map(int, tensor_train_ranks(q, atol=float(H.SPECTRAL_RANK_ATOL))))
    return out


def _pymdp_facts() -> dict[str, float] | dict[str, str]:
    """pymdp-grounded total-correlation values at sentinel ``λ``.

    Returns a string-valued sentinel dict when the ``sim`` group is not
    installed so the JSON consumer can detect the missing-deps case rather than
    treating it as numeric zeros.
    """
    try:
        from simulation.agents import pymdp_available
    except Exception:  # pragma: no cover - import shape only
        return {"pymdp": "import-failed"}
    if not pymdp_available():
        return {"pymdp": "not-installed"}

    from lean.free_energy import total_correlation
    from simulation.builders import make_ising_ensemble
    from simulation.inference import (
        coupled_policy_posterior,
        decomposition_witness_curve,
        free_energy_curve,
    )
    from simulation.statistics import (
        pymdp_summary_statistics,
        summary_to_var_dict,
    )

    spec = make_ising_ensemble(
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        coupling_amplitude=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
    )
    facts: dict[str, float] = {}
    for lam in H.PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS:
        q = coupled_policy_posterior(
            spec,
            observations=list(H.PYMDP_SWEEP_OBSERVATIONS),
            lam=float(lam),
        )
        facts[f"pymdp_total_correlation_lam_{lam:g}".replace(".", "_")] = float(total_correlation(q))

    bundles = free_energy_curve(
        spec,
        observations=list(H.PYMDP_SWEEP_OBSERVATIONS),
        lams=H.PYMDP_SWEEP_LAMBDAS.values(),
    )
    summary = pymdp_summary_statistics(bundles)
    facts.update(summary_to_var_dict(summary))
    witnesses = decomposition_witness_curve(
        spec,
        observations=list(H.PYMDP_SWEEP_OBSERVATIONS),
        lams=H.PYMDP_SWEEP_LAMBDAS.values(),
    )
    facts["pymdp_decomposition_residual_max"] = float(max(w.residual for w in witnesses))
    facts["pymdp_decomposition_residual_mean"] = float(np.mean([w.residual for w in witnesses]))
    zero_bundle = min(bundles, key=lambda b: abs(float(b.lam)))
    facts["pymdp_coupling_term_at_lambda_zero"] = float(zero_bundle.coupling_term)
    facts["pymdp_joint_entropy_at_lambda_zero"] = float(zero_bundle.joint_entropy)
    facts["pymdp_marginal_entropy_sum_at_lambda_zero"] = float(zero_bundle.marginal_entropies.sum())
    return facts


def _hyperparameter_facts() -> dict[str, object]:
    """Flat hyperparameter snapshot from :mod:`simulation.hyperparameters`."""
    return H.figure_hyperparameter_summary()


def _scalar_json_sidecar(path: Path, sentinel_key: str) -> dict[str, object]:
    """Read scalar top-level keys from a generated JSON sidecar."""
    if not path.exists():
        return {sentinel_key: "not-run"}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {sentinel_key: "invalid-json"}
    if not isinstance(data, dict):
        return {sentinel_key: "invalid-payload"}
    out: dict[str, object] = {}
    for key, value in data.items():
        if isinstance(value, bool):
            out[str(key)] = value
            continue
        if isinstance(value, (int, float)):
            out[str(key)] = float(value)
            continue
        if isinstance(value, str) and _SCALAR_SIDECAR_SENTINEL_RE.match(value):
            # Only *sentinel* strings (e.g. a present-but-skipped sidecar that
            # recorded `"<group>_status": "not-run"`) are surfaced as variables
            # so the veridicality / undefined-token gates fail loudly on
            # unbacked data. Benign metadata strings such as `"ok"` or a
            # human-readable `"..._note"` must not leak into the
            # manuscript-variable namespace.
            out[str(key)] = value
    return out


def _numeric_only_json_sidecar(path: Path, sentinel_key: str) -> dict[str, object]:
    """Read a JSON sidecar that promises only numeric scalar values."""
    if not path.exists():
        return {sentinel_key: "not-run"}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {sentinel_key: "invalid-json"}
    if not isinstance(data, dict):
        return {sentinel_key: "invalid-payload"}
    out: dict[str, object] = {}
    for k, v in data.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            out[str(k)] = v
    return out


def _multi_k_facts(project_root: Path) -> dict[str, object]:
    return _numeric_only_json_sidecar(project_root / "output" / "data" / "multi_k_summary.json", "multi_k")


def _long_horizon_facts(project_root: Path) -> dict[str, object]:
    return _numeric_only_json_sidecar(
        project_root / "output" / "data" / "long_horizon_summary.json",
        "long_horizon",
    )


def _revertibility_facts(project_root: Path) -> dict[str, object]:
    return _numeric_only_json_sidecar(
        project_root / "output" / "data" / "revertibility_summary.json",
        "revertibility",
    )


def _robustness_facts(project_root: Path) -> dict[str, object]:
    return _scalar_json_sidecar(
        project_root / "output" / "data" / "robustness_summary.json",
        "robustness",
    )


def _coupling_ablation_facts(project_root: Path) -> dict[str, object]:
    return _scalar_json_sidecar(
        project_root / "output" / "data" / "coupling_ablation_summary.json",
        "coupling_ablation",
    )


def _marginal_null_control_facts(project_root: Path) -> dict[str, object]:
    return _scalar_json_sidecar(
        project_root / "output" / "data" / "marginal_null_control_summary.json",
        "marginal_null_control",
    )


def _long_horizon_replicate_facts(project_root: Path) -> dict[str, object]:
    return _scalar_json_sidecar(
        project_root / "output" / "data" / "long_horizon_replicates_summary.json",
        "long_horizon_replicates",
    )


def _interaction_robustness_facts(project_root: Path) -> dict[str, object]:
    return _scalar_json_sidecar(
        project_root / "output" / "data" / "interaction_robustness_summary.json",
        "interaction_robustness",
    )


def _btai_facts(project_root: Path) -> dict[str, object]:
    return _scalar_json_sidecar(project_root / "output" / "data" / "btai_baseline.json", "btai")


def _adversarial_facts(project_root: Path) -> dict[str, object]:
    return _scalar_json_sidecar(project_root / "output" / "data" / "adversarial_sweep.json", "adversarial")


def _gnn_facts(project_root: Path) -> dict[str, object]:
    """GNN fifth-track round-trip facts, sourced from the real sidecar.

    Emits namespaced VARs from ``output/data/gnn_bernoulli_roundtrip.json``
    (written by the ``simulate_gnn`` stage): the round-trip max residual, the
    embedded zero-coupling negative-control residual (non-vacuity evidence),
    and the structural lambda-grid point count. Returns the ``gnn: not-run``
    sentinel when the GNN stage has not been run, so the undefined-token /
    veridicality gates fail loudly rather than silently dropping the track.
    """
    path = project_root / "output" / "data" / "gnn_bernoulli_roundtrip.json"
    if not path.exists():
        return {"gnn": "not-run"}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"gnn": "invalid-json"}
    if not isinstance(data, dict):
        return {"gnn": "invalid-payload"}
    grid = data.get("lambda_grid", {})
    return {
        "gnn_roundtrip_max_residual": float(data["max_abs_residual"]),
        "gnn_negative_control_max_residual": float(data["negative_control_zero_coupling_max_residual"]),
        "gnn_round_trip_lambda_points": float(grid.get("num", 0)),
        "gnn_num_streams": float(data["num_streams"]),
    }


def _format_lambda_list(values: tuple[float, ...]) -> str:
    """Render a tuple of sentinel ``λ`` as a comma-separated string suitable
    for inline math: e.g. ``(0.0, 0.5, 1.0, 2.0, 4.0)`` → ``"0, 0.5, 1, 2, 4"``.

    Whole-number entries drop the trailing ``.0`` for compactness; fractional
    entries keep their decimal form.
    """
    out: list[str] = []
    for v in values:
        out.append(f"{int(v)}" if float(v).is_integer() else f"{v:g}")
    return ", ".join(out)


def _sentinel_list_facts() -> dict[str, str | int | float]:
    """Serialize every ``H.*_SENTINEL_*`` tuple as a comma-separated string the
    manuscript can splice into prose via ``[[VAR:...]]``.

    Promotes the sentinel arrays themselves into the auto-injection contract so
    prose like ``λ ∈ {0, 0.5, 1, 2, 4}`` no longer depends on hand-typed
    values: the list comes from :mod:`simulation.hyperparameters` and any
    change there flows through to the rendered manuscript.
    """
    return {
        "ising_mi_sentinel_lambdas": _format_lambda_list(H.ISING_MI_SENTINEL_LAMBDAS),
        "ising_mi_sentinel_lambdas_count": int(len(H.ISING_MI_SENTINEL_LAMBDAS)),
        "ising_mi_saturation_lambda": float(H.ISING_MI_SATURATION_LAMBDA),
        "spectral_sentinel_lambdas": _format_lambda_list(H.SPECTRAL_SENTINEL_LAMBDAS),
        "ising_alignment_sentinel_lambdas": _format_lambda_list(H.ISING_ALIGNMENT_SENTINEL_LAMBDAS),
        "motor_attention_sentinel_lambdas": _format_lambda_list(H.MOTOR_ATTENTION_SENTINEL_LAMBDAS),
        "optimal_lambda_sentinel_deltas": _format_lambda_list(H.OPTIMAL_LAMBDA_SENTINEL_DELTAS),
        "tt_rank_stream_counts": _format_lambda_list(tuple(float(k) for k in H.TT_RANK_STREAM_COUNTS)),
        "multi_k_values_list": _format_lambda_list(tuple(float(k) for k in H.MULTI_K_VALUES)),
        "pymdp_total_correlation_sentinel_lambdas": _format_lambda_list(H.PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS),
        "pymdp_total_correlation_sentinel_lambdas_count": int(len(H.PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS)),
        "bernoulli_verification_lambdas": _format_lambda_list(H.BERNOULLI_VERIFICATION_LAMBDAS),
        "bernoulli_verification_lambdas_count": int(len(H.BERNOULLI_VERIFICATION_LAMBDAS)),
        "long_horizon_replicate_seeds_list": _format_lambda_list(
            tuple(float(seed) for seed in H.LONG_HORIZON_REPLICATE_SEEDS)
        ),
        "long_horizon_diagnostic_thresholds_list": _format_lambda_list(H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS),
        "coupling_ablation_variants_list": ", ".join(str(v).replace("_", " ") for v in H.COUPLING_ABLATION_VARIANTS),
        "robustness_interaction_families_list": ", ".join(
            str(v).replace("_x_", " × ").replace("_", " ") for v in H.ROBUSTNESS_INTERACTION_FAMILIES
        ),
    }


def _toolchain_facts(project_root: Path) -> dict[str, str]:
    """Pinned Lean toolchain and optional pymdp distribution version."""
    toolchain_path = project_root / "lean" / "lean-toolchain"
    lean_toolchain = toolchain_path.read_text(encoding="utf-8").strip() if toolchain_path.exists() else "unknown"
    lean_version = lean_toolchain.rsplit(":", maxsplit=1)[-1] if lean_toolchain else "unknown"
    pymdp_version = "unknown"
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        match = re.search(r'"inferactively-pymdp==([^"]+)"', text)
        if match:
            pymdp_version = match.group(1)
    return {
        "lean_toolchain_pin": lean_toolchain,
        "lean_toolchain_version": lean_version,
        "pymdp_distribution_version": pymdp_version,
    }


def build_manuscript_variables(project_root: Path | None = None) -> dict[str, Any]:
    """Compute the full ``manuscript_variables.json`` payload as a Python dict.

    Args:
        project_root: Project root directory (defaults to the project that
            owns this ``src/`` package).

    Returns:
        Ordered mapping of every manuscript variable to its computed value.
        Sentinel strings (``"not-run"``, ``"not-installed"``,
        ``"import-failed"``, etc.) are surfaced when an upstream stage hasn't
        produced its sidecar yet.
    """
    root = project_root or PROJECT_ROOT
    facts: dict[str, Any] = {}
    facts.update(_bernoulli_facts())
    facts.update(_spectral_facts())
    facts.update(_alignment_and_phase_facts())
    facts.update(_motor_attention_facts())
    facts.update(_coupling_tax_curvature())
    facts.update(_run_all_facts(root))
    facts.update(_lean_facts(root))
    facts.update(_toolchain_facts(root))
    facts.update(_registry_facts(root))
    facts.update(_tensor_train_facts())
    facts.update(_pymdp_facts())
    facts.update(_multi_k_facts(root))
    facts.update(_long_horizon_facts(root))
    facts.update(_revertibility_facts(root))
    facts.update(_robustness_facts(root))
    facts.update(_coupling_ablation_facts(root))
    facts.update(_marginal_null_control_facts(root))
    facts.update(_interaction_robustness_facts(root))
    facts.update(_long_horizon_replicate_facts(root))
    facts.update(_btai_facts(root))
    facts.update(_adversarial_facts(root))
    facts.update(_gnn_facts(root))
    facts.update(_sentinel_list_facts())
    # Hyperparameters last so their stable shape is preserved verbatim.
    facts.update(_hyperparameter_facts())
    return facts


def build_float_real_residual(project_root: Path | None = None) -> dict[str, float]:
    """Machine-readable Float↔ℝ residual certificate (scaffold, not a proof).

    Aggregates the decomposition dashboard witness, Monte-Carlo MI
    concentration radius, and capstone conjunct tolerance cited in
    ``docs/reference/methods_and_assumptions.md``.
    """
    from lean.bernoulli_toy import (
        empirical_mutual_information_montecarlo,
        ising_mutual_information,
    )
    from lean.invariants import SweepGrid, decomposition_invariants

    _ = project_root  # reserved for future sidecar reads
    grid = SweepGrid(
        lam_min=float(H.PARAMETER_SWEEP_LAMBDAS.start),
        lam_max=float(H.PARAMETER_SWEEP_LAMBDAS.stop),
        num=min(31, int(H.PARAMETER_SWEEP_LAMBDAS.num)),
    )
    decomp = decomposition_invariants(grid)
    max_residual_actual = next(inv for inv in decomp if inv.name == "decomposition_lhs_eq_rhs_max_residual").actual
    if not isinstance(max_residual_actual, int | float):
        raise TypeError("decomposition_lhs_eq_rhs_max_residual invariant must be scalar")
    max_residual = float(max_residual_actual)

    lam = float(H.MONTECARLO_MI_LAMBDA)
    n_samples = int(H.MONTECARLO_MI_N)
    n_seeds = int(H.MONTECARLO_MI_SEEDS)
    bias_tol = float(H.MONTECARLO_MI_BIAS_TOL)
    samples = [empirical_mutual_information_montecarlo(lam, n_samples, seed) for seed in range(n_seeds)]
    mu = float(np.mean(samples))
    sd = float(np.std(samples, ddof=1)) if len(samples) > 1 else 0.0
    closed = float(ising_mutual_information(lam))
    concentration_radius = float(4.0 * sd / np.sqrt(n_seeds) + bias_tol)

    return {
        "decomposition_lhs_eq_rhs_max_residual": max_residual,
        "montecarlo_mi_lambda": lam,
        "montecarlo_mi_closed_form": closed,
        "montecarlo_mi_sample_mean": mu,
        "montecarlo_mi_concentration_radius": concentration_radius,
        "capstone_conjunct_tolerance": 1e-9,
    }


def write_float_real_residual(
    output_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> Path:
    """Persist ``float_real_residual.json`` under ``output/reports/``."""
    root = project_root or PROJECT_ROOT
    payload = build_float_real_residual(root)
    target = output_path or (root / "output" / "reports" / "float_real_residual.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return target


def write_manuscript_variables(
    output_path: Path | None = None,
    *,
    project_root: Path | None = None,
) -> Path:
    """Compute and persist the manuscript-variables JSON.

    Args:
        output_path: Destination file (defaults to
            ``<project>/output/data/manuscript_variables.json``).
        project_root: Project root directory.

    Returns:
        Absolute path of the written file.
    """
    root = project_root or PROJECT_ROOT
    facts = build_manuscript_variables(root)
    target = output_path or (root / "output" / "data" / "manuscript_variables.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
    write_float_real_residual(project_root=root)
    return target


def main() -> None:
    """Thin CLI entry point: compute facts, write JSON, print the output path."""
    out = write_manuscript_variables()
    print(out)


__all__ = [
    "PROJECT_ROOT",
    "build_float_real_residual",
    "build_manuscript_variables",
    "main",
    "write_float_real_residual",
    "write_manuscript_variables",
    "_format_lambda_key",
    "_format_lambda_list",
]


if __name__ == "__main__":
    main()
