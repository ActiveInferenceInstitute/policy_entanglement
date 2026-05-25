"""Single source of truth for closed-form manuscript variable ranges.

Analytical range pins shared by ``validation_cli.EXPECTED_RANGES`` and
the overlapping keys in ``output_gates.constants.REQUIRED_VARIABLES``.
Gate-specific structural pins (hyperparameter grid counts, robustness
scenario counts, etc.) stay in ``constants.py`` and merge via
:func:`merge_required_variables`.
"""

from __future__ import annotations

from simulation import hyperparameters as H  # noqa: N812


def merge_required_variables(
    *extensions: dict[str, tuple[float, float]],
) -> dict[str, tuple[float, float]]:
    """Merge range dicts left-to-right; later keys override on collision."""
    merged: dict[str, tuple[float, float]] = {}
    for ext in extensions:
        merged.update(ext)
    return merged


# Closed-form Bernoulli / Ising / spectral / alignment / phase / GNN pins
# consumed by the manuscript validator CLI.
ANALYTICAL_VARIABLE_RANGES: dict[str, tuple[float, float]] = {
    "ising_mi_at_lam_05": (0.0, 0.05),
    "ising_mi_at_lam_1": (0.05, 0.20),
    "ising_mi_at_lam_2": (0.20, 0.45),
    "ising_mi_saturation": (0.69, 0.70),
    "lambda_star_delta_05": (1.0, 1.2),
    "lambda_star_delta_09": (2.8, 3.1),
    "ising_S_E_at_lam_0": (-1e-9, 1e-9),
    "ising_S_E_at_lam_1": (0.0, 0.5),
    "ising_S_E_at_lam_3": (0.0, 0.7),
    "ising_schmidt_rank_at_lam_0": (1.0, 1.0),
    "ising_schmidt_rank_at_lam_1": (2.0, 2.0),
    "ising_alignment_at_lam_05": (0.0, 0.30),
    "ising_alignment_at_lam_1": (0.40, 0.55),
    "ising_alignment_at_lam_2": (0.70, 0.80),
    "ising_alignment_at_lam_3": (0.85, 0.95),
    "phase_lambda_c1": (0.5, 0.5),
    "phase_lambda_c2": (2.5, 2.5),
    "motor_attention_aligned_prob_lam_0": (0.0, 1.0),
    "motor_attention_aligned_prob_lam_1": (0.0, 1.0),
    "motor_attention_aligned_prob_lam_2": (0.0, 1.0),
    "coupling_tax_curvature_C": (0.0, 1.0),
    "gnn_roundtrip_max_residual": (0.0, float(H.BERNOULLI_VERIFICATION_TOLERANCE)),
    "gnn_negative_control_max_residual": (0.1, 0.7),
    "gnn_round_trip_lambda_points": (
        float(H.PARAMETER_SWEEP_LAMBDAS.num),
        float(H.PARAMETER_SWEEP_LAMBDAS.num),
    ),
    "gnn_num_streams": (2.0, 2.0),
}
