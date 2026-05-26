"""Closed-form and analytical manuscript-variable producers."""

from __future__ import annotations

import numpy as np

from lean.bernoulli_toy import ising_joint_posterior, ising_mutual_information, optimal_lambda
from lean.coupling import entangled_posterior
from lean.spectral import entanglement_entropy, schmidt_rank, tensor_train_ranks
from simulation import hyperparameters as H  # noqa: N812
from simulation.builders import ising_coupling_tensor


def format_lambda_key(lam: float) -> str:
    """Stable JSON key fragment for a sentinel ``λ``."""
    if lam == int(lam):
        return f"{int(lam)}"
    s = f"{lam:g}"
    if s.startswith("0."):
        return "0" + s[2:].replace(".", "_")
    return s.replace(".", "_")


def bernoulli_facts() -> dict[str, float]:
    out: dict[str, float] = {}
    for lam in H.ISING_MI_SENTINEL_LAMBDAS:
        out[f"ising_mi_at_lam_{format_lambda_key(lam)}"] = ising_mutual_information(float(lam))
    out["ising_mi_saturation"] = ising_mutual_information(float(H.ISING_MI_SATURATION_LAMBDA))
    for delta in H.OPTIMAL_LAMBDA_SENTINEL_DELTAS:
        key = format_lambda_key(delta)
        out[f"lambda_star_delta_{key}"] = optimal_lambda(float(delta))
    return out


def spectral_facts() -> dict[str, float]:
    out: dict[str, float] = {}
    for lam in H.SPECTRAL_SENTINEL_LAMBDAS:
        key = format_lambda_key(lam)
        out[f"ising_S_E_at_lam_{key}"] = float(entanglement_entropy(ising_joint_posterior(float(lam))))
    for lam in (0.0, 1.0):
        key = format_lambda_key(lam)
        out[f"ising_schmidt_rank_at_lam_{key}"] = float(
            schmidt_rank(
                ising_joint_posterior(float(lam)),
                atol=float(H.SPECTRAL_RANK_ATOL),
            )
        )
    return out


def alignment_and_phase_facts() -> dict[str, float]:
    out: dict[str, float] = {}
    for lam in H.ISING_ALIGNMENT_SENTINEL_LAMBDAS:
        key = format_lambda_key(lam)
        out[f"ising_alignment_at_lam_{key}"] = float(np.tanh(float(lam) / 2.0))
    out["phase_lambda_c1"] = float(H.PHASE_LAMBDA_C1)
    out["phase_lambda_c2"] = float(H.PHASE_LAMBDA_C2)
    return out


def motor_attention_facts() -> dict[str, float]:
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.4, 0.0]), np.array([0.5, 0.0])]  # noqa: N806
    J = np.array([[0.7, -0.7], [-0.7, 0.7]])  # noqa: N806
    Kc = np.array([[0.0, 0.2], [0.2, 0.0]])  # noqa: N806
    out: dict[str, float] = {}
    for lam in H.MOTOR_ATTENTION_SENTINEL_LAMBDAS:
        q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=float(lam))
        out[f"motor_attention_aligned_prob_lam_{int(lam)}"] = float(q[0, 0] + q[1, 1])
    return out


def coupling_tax_curvature() -> dict[str, float]:
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


def tensor_train_facts() -> dict[str, list[int]]:
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


def format_lambda_list(values: tuple[float, ...]) -> str:
    out: list[str] = []
    for v in values:
        out.append(f"{int(v)}" if float(v).is_integer() else f"{v:g}")
    return ", ".join(out)


def sentinel_list_facts() -> dict[str, str | int | float]:
    return {
        "ising_mi_sentinel_lambdas": format_lambda_list(H.ISING_MI_SENTINEL_LAMBDAS),
        "ising_mi_sentinel_lambdas_count": int(len(H.ISING_MI_SENTINEL_LAMBDAS)),
        "ising_mi_saturation_lambda": float(H.ISING_MI_SATURATION_LAMBDA),
        "spectral_sentinel_lambdas": format_lambda_list(H.SPECTRAL_SENTINEL_LAMBDAS),
        "ising_alignment_sentinel_lambdas": format_lambda_list(H.ISING_ALIGNMENT_SENTINEL_LAMBDAS),
        "motor_attention_sentinel_lambdas": format_lambda_list(H.MOTOR_ATTENTION_SENTINEL_LAMBDAS),
        "optimal_lambda_sentinel_deltas": format_lambda_list(H.OPTIMAL_LAMBDA_SENTINEL_DELTAS),
        "tt_rank_stream_counts": format_lambda_list(tuple(float(k) for k in H.TT_RANK_STREAM_COUNTS)),
        "multi_k_values_list": format_lambda_list(tuple(float(k) for k in H.MULTI_K_VALUES)),
        "pymdp_total_correlation_sentinel_lambdas": format_lambda_list(H.PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS),
        "pymdp_total_correlation_sentinel_lambdas_count": int(len(H.PYMDP_TOTAL_CORRELATION_SENTINEL_LAMBDAS)),
        "bernoulli_verification_lambdas": format_lambda_list(H.BERNOULLI_VERIFICATION_LAMBDAS),
        "bernoulli_verification_lambdas_count": int(len(H.BERNOULLI_VERIFICATION_LAMBDAS)),
        "long_horizon_replicate_seeds_list": format_lambda_list(
            tuple(float(seed) for seed in H.LONG_HORIZON_REPLICATE_SEEDS)
        ),
        "long_horizon_diagnostic_thresholds_list": format_lambda_list(H.LONG_HORIZON_DIAGNOSTIC_THRESHOLDS),
        "coupling_ablation_variants_list": ", ".join(str(v).replace("_", " ") for v in H.COUPLING_ABLATION_VARIANTS),
        "robustness_interaction_families_list": ", ".join(
            str(v).replace("_x_", " × ").replace("_", " ") for v in H.ROBUSTNESS_INTERACTION_FAMILIES
        ),
    }


__all__ = [
    "alignment_and_phase_facts",
    "bernoulli_facts",
    "coupling_tax_curvature",
    "format_lambda_key",
    "format_lambda_list",
    "motor_attention_facts",
    "sentinel_list_facts",
    "spectral_facts",
    "tensor_train_facts",
]
