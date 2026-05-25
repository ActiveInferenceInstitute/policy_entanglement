"""BTAI baseline worked-run plotting and orchestration.

Business logic for ``scripts/simulate_btai.py``. The script is a thin
wrapper that exposes ``DATA_DIR`` / ``FIG_DIR`` as patchable module-level
attributes for tests; this module reads them through call arguments so
no implicit module-global coupling is introduced.

Emits, when pymdp is available:

* ``<data_dir>/btai_baseline.json`` — scalar summary plus per-budget rows.
* ``<fig_dir>/btai_baseline.png`` — three-panel deterministic figure.

When pymdp is missing, writes a ``not-run`` sentinel JSON so downstream
gates fail honestly rather than silently.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lean.bernoulli_toy import ising_joint_posterior
from simulation import hyperparameters as H  # noqa: N812 — H = hyperparameters (manuscript convention).
from simulation.agents import pymdp_available
from simulation.btai_baseline import (
    BTAIScenario,
    kl_against_reference,
    run_btai_scenario,
    sample_complexity_exponent,
    total_correlation,
)
from visualizations._io import _save_with_metadata
from visualizations.metadata import figure_metadata
from visualizations.setup import PUBLICATION_STYLE, deterministic_setup, ensure_outdir

#: Canonical BTAI operating point — sourced from the single source of
#: truth (:mod:`simulation.hyperparameters`), never inlined here, so the
#: worked run cannot silently drift from the manuscript's declared knobs.
REFERENCE_LAMBDA: float = float(H.BTAI_REFERENCE_LAMBDA)
HORIZON: int = int(H.BTAI_HORIZON)


def _plot_btai(
    *,
    budgets: list[int],
    kl_curve: list[float],
    reference: np.ndarray,
    final_posterior: np.ndarray,
    exponent: float,
    out_path: Path,
) -> Path:
    """Three-panel BTAI worked-run figure (deterministic, canonical-seed)."""
    style = PUBLICATION_STYLE
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0))

    # (a) KL of the MCTS visitation posterior vs the soft analytic reference.
    ax = axes[0]
    ax.plot(budgets, kl_curve, marker="o", color="#0072B2", linewidth=2.0)
    ax.set_xscale("log")
    ax.set_xlabel("MCTS budget $B_{\\mathrm{MCTS}}$", fontsize=style.label_size)
    ax.set_ylabel("$D_{\\mathrm{KL}}$(visitation $\\|$ soft reference) [nats]", fontsize=style.label_size)
    ax.set_title(
        f"(a) Visitation vs soft reference\n(slope exponent {exponent:+.3f})",
        fontsize=style.title_size,
    )
    ax.tick_params(labelsize=style.tick_size)
    ax.grid(True, which="both", alpha=0.3)

    vmax = float(max(reference.max(), final_posterior.max()))
    for ax, mat, title in (
        (axes[1], reference, "(b) Closed-form reference $q_\\lambda$"),
        (axes[2], final_posterior, f"(c) BTAI visitation ($B={max(budgets):d}$)"),
    ):
        im = ax.imshow(mat, cmap="viridis", vmin=0.0, vmax=vmax)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["$\\pi^2=0$", "$\\pi^2=1$"], fontsize=style.tick_size)
        ax.set_yticklabels(["$\\pi^1=0$", "$\\pi^1=1$"], fontsize=style.tick_size)
        ax.set_title(title, fontsize=style.title_size)
        for (i, j), val in np.ndenumerate(mat):
            ax.text(
                j,
                i,
                f"{val:.2f}",
                ha="center",
                va="center",
                fontsize=style.annotation_size,
                color="white" if val < vmax * 0.6 else "black",
            )
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    return Path(
        _save_with_metadata(
            fig,
            out_path,
            metadata=figure_metadata(
                source_script="scripts/simulate_btai.py",
                source_function="_plot_btai",
                uncertainty_semantics="canonical_seed",
                hyperparameters={"mcts_budgets": budgets, "reference_lambda": REFERENCE_LAMBDA, "horizon": HORIZON},
                statistics={"kl_curve": kl_curve, "sample_complexity_exponent": exponent},
            ),
        )
    )


def _build_pymdp_efe():
    """Return a (joint_action_space, efe_fn) pair from real pymdp, or ``None``.

    Late import keeps this module importable without the ``sim`` group;
    returns ``None`` when pymdp is unavailable so the caller can skip
    honestly rather than fabricate an EFE landscape.
    """
    if not pymdp_available():
        return None
    from simulation.btai_baseline import pymdp_grounded_efe_fn
    from simulation.builders import make_ising_ensemble

    spec = make_ising_ensemble(
        coupling_amplitude=float(H.BTAI_ENSEMBLE_COUPLING_AMPLITUDE),
        preference_strength=float(H.BTAI_ENSEMBLE_PREFERENCE_STRENGTH),
        num_streams=int(H.BTAI_NUM_STREAMS),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
    )
    observations = tuple(0 for _ in range(spec.num_streams()))
    return spec.policy_shape(), pymdp_grounded_efe_fn(spec, observations)


def run(*, data_dir: Path, fig_dir: Path) -> int:
    """Run the BTAI baseline sweep; emit JSON sidecar and PNG figure.

    Honors the ``not-run`` sentinel when pymdp is unavailable. Prints
    each emitted path to stdout for downstream manifest collection.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    summary_path = data_dir / "btai_baseline.json"

    built = _build_pymdp_efe()
    if built is None:
        sentinel_payload: dict[str, object] = {
            "btai_status": "not-run",
            "btai_note": "pymdp/sim group not installed; BTAI baseline skipped (run `uv sync --group sim`).",
        }
        summary_path.write_text(json.dumps(sentinel_payload, indent=2, sort_keys=True) + "\n")
        print(f"[simulate_btai] sim group not installed — wrote sentinel {summary_path}")
        print(str(summary_path))
        return 0

    joint_action_space, efe_fn = built
    reference = np.asarray(ising_joint_posterior(REFERENCE_LAMBDA), dtype=np.float64)

    budgets = list(H.BTAI_DEFAULT_BUDGETS)
    seed = int(H.PYMDP_ROLLOUT_SEED)

    rows: list[dict[str, object]] = []
    kl_curve: list[float] = []
    for budget in budgets:
        scenario = BTAIScenario(
            horizon=HORIZON,
            mcts_budget=int(budget),
            seed=seed,
            lambda_value=REFERENCE_LAMBDA,
        )
        result = run_btai_scenario(
            scenario=scenario,
            joint_action_space=joint_action_space,
            expected_free_energy_fn=efe_fn,
            reference_posterior=reference,
        )
        posterior = np.asarray(result.final_posterior, dtype=np.float64)
        kl_value = kl_against_reference(posterior, reference)
        kl_curve.append(kl_value)
        rows.append(
            {
                "mcts_budget": int(budget),
                "kl_against_reference": float(kl_value),
                "total_correlation": float(total_correlation(posterior)),
                "joint_posterior": [[float(x) for x in r] for r in posterior],
            }
        )

    exponent = sample_complexity_exponent(budgets, kl_curve)
    # `posterior` holds the last (largest-budget) visitation posterior from
    # the loop above; keep typed locals rather than reading back object-typed
    # values out of the JSON-row dicts.
    final_posterior = posterior
    final_kl = kl_curve[-1]
    final_tc = float(total_correlation(final_posterior))

    deterministic_setup()
    ensure_outdir(fig_dir)
    fig_path = _plot_btai(
        budgets=budgets,
        kl_curve=kl_curve,
        reference=reference,
        final_posterior=final_posterior,
        exponent=exponent,
        out_path=fig_dir / "btai_baseline.png",
    )

    payload: dict[str, object] = {
        # scalar manuscript-variable mirror (top-level scalars become VARs) —
        "btai_num_budgets": float(len(budgets)),
        "btai_mcts_max_budget": float(max(budgets)),
        "btai_mcts_min_budget": float(min(budgets)),
        "btai_reference_lambda": float(REFERENCE_LAMBDA),
        "btai_kl_at_max_budget": float(final_kl),
        "btai_total_correlation_at_max_budget": final_tc,
        "btai_sample_complexity_exponent": float(exponent),
        "btai_status": "ok",
        # full per-budget observable rows (lists ignored by the scalar VAR loader) —
        "rows": rows,
    }
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for p in (summary_path, fig_path):
        print(str(p))
    return 0


__all__ = ["REFERENCE_LAMBDA", "HORIZON", "_plot_btai", "_build_pymdp_efe", "run"]
