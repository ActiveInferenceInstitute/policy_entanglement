#!/usr/bin/env python3
"""Compute the manuscript-substituted variables.

Bernoulli closed-form numbers, Schmidt entropies of the K=2 Ising
joint at sentinel λ values, K-stream tensor-train rank summaries, and
(when the ``sim`` group is installed) pymdp-grounded total-correlation
values from the coupled-policy harness.

Thin orchestrator: imports analytical helpers from ``src/lean/``,
ensemble builders + sweeps from ``src/simulation/``, and writes a
single JSON file consumable by both the rendering pipeline and the
manuscript validator.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
for _sub in ("", "lean", "simulation", "visualizations"):
    sys.path.insert(0, str(SRC_DIR / _sub if _sub else SRC_DIR))

import numpy as np  # noqa: E402

from bernoulli_toy import (  # noqa: E402
    ising_joint_posterior,
    ising_mutual_information,
    optimal_lambda,
)
from coupling import entangled_posterior  # noqa: E402
from spectral import (  # noqa: E402
    entanglement_entropy,
    schmidt_rank,
    tensor_train_ranks,
)


def _bernoulli_facts() -> dict[str, float]:
    return {
        "ising_mi_at_lam_05": ising_mutual_information(0.5),
        "ising_mi_at_lam_1": ising_mutual_information(1.0),
        "ising_mi_at_lam_2": ising_mutual_information(2.0),
        "ising_mi_saturation": ising_mutual_information(50.0),
        "lambda_star_delta_05": optimal_lambda(0.5),
        "lambda_star_delta_09": optimal_lambda(0.9),
    }


def _spectral_facts() -> dict[str, float]:
    """Schmidt-entropy and rank facts for the K=2 Ising joint."""
    return {
        "ising_S_E_at_lam_0": float(entanglement_entropy(ising_joint_posterior(0.0))),
        "ising_S_E_at_lam_1": float(entanglement_entropy(ising_joint_posterior(1.0))),
        "ising_S_E_at_lam_3": float(entanglement_entropy(ising_joint_posterior(3.0))),
        "ising_schmidt_rank_at_lam_0": float(
            schmidt_rank(ising_joint_posterior(0.0), atol=1e-9)
        ),
        "ising_schmidt_rank_at_lam_1": float(
            schmidt_rank(ising_joint_posterior(1.0), atol=1e-9)
        ),
    }


def _alignment_and_phase_facts() -> dict[str, float]:
    """K=2 Ising alignment $\\alpha(\\lambda) = \\tanh(\\lambda/2)$ at sentinel
    $\\lambda$ values, plus the illustrative phase thresholds used in §9.
    """
    return {
        "ising_alignment_at_lam_05": float(np.tanh(0.5 / 2.0)),
        "ising_alignment_at_lam_1": float(np.tanh(1.0 / 2.0)),
        "ising_alignment_at_lam_2": float(np.tanh(2.0 / 2.0)),
        "ising_alignment_at_lam_3": float(np.tanh(3.0 / 2.0)),
        "phase_lambda_c1": 0.5,
        "phase_lambda_c2": 2.5,
    }


def _motor_attention_facts() -> dict[str, float]:
    """Numerics for the motor+attention worked example in §5.

    Two binary streams (motor: reach-L / reach-R; attention: look-L /
    look-R) with strong-aligned habit coupling, mild simultaneous-novelty
    penalty, and asymmetric per-stream EFEs that prefer the right-hand
    target.
    """
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.4, 0.0]), np.array([0.5, 0.0])]
    J = np.array([[0.7, -0.7], [-0.7, 0.7]])
    Kc = np.array([[0.0, 0.2], [0.2, 0.0]])
    out: dict[str, float] = {}
    for lam in (0.0, 1.0, 2.0):
        from coupling import entangled_posterior  # noqa: WPS433

        q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=lam)
        # P(aligned) = q(0,0) + q(1,1).
        out[f"motor_attention_aligned_prob_lam_{int(lam)}"] = float(q[0, 0] + q[1, 1])
    return out


def _coupling_tax_curvature() -> dict[str, float]:
    """Empirical $O(\\lambda^2)$ curvature constant fitted from a
    heterogeneous K=2 ensemble at a small probe $\\lambda$.  Mirrors
    the C value that
    [`scripts/generate_figures.py::figure_coupling_tax_quadratic`](../scripts/generate_figures.py)
    annotates on the dashed envelope.
    """
    from heterogeneous import InferenceMode, coupling_tax  # noqa: WPS433

    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    G = [np.array([0.0, 0.5]), np.array([0.0, 0.5])]
    J = np.array([[0.5, -0.5], [-0.5, 0.5]])
    Kc = np.array([[0.2, -0.1], [-0.1, 0.2]])
    modes = [InferenceMode.VFE, InferenceMode.EFE]
    lam_probe = 0.05
    tax = coupling_tax(mf, G, J, Kc, gamma=1.0, lam=lam_probe, modes=modes)
    C = tax / (lam_probe * lam_probe) if lam_probe > 0 else 0.0
    return {"coupling_tax_curvature_C": float(C)}


def _tensor_train_facts() -> dict[str, list[int]]:
    """TT-rank profiles across K=2..5 for the symmetric Ising coupling."""
    from builders import ising_coupling_tensor

    out: dict[str, list[int]] = {}
    for K in (2, 3, 4, 5):
        shape = tuple(2 for _ in range(K))
        J = ising_coupling_tensor(shape, scale=1.0)
        mf = [np.array([0.5, 0.5]) for _ in range(K)]
        G = [np.zeros(2) for _ in range(K)]
        Kc = np.zeros(shape)
        q = entangled_posterior(mf, G, J, Kc, gamma=0.0, lam=2.0)
        out[f"tt_ranks_K{K}"] = list(map(int, tensor_train_ranks(q, atol=1e-9)))
    return out


def _pymdp_facts() -> dict[str, float] | dict[str, str]:
    """pymdp-grounded total-correlation values at sentinel λ.

    Returns a string-valued sentinel dict when the ``sim`` group is not
    installed so the JSON consumer can detect the missing-deps case
    rather than treating it as numeric zeros.
    """
    try:
        from agents import pymdp_available  # noqa: WPS433
    except Exception:  # pragma: no cover - import shape only
        return {"pymdp": "import-failed"}
    if not pymdp_available():
        return {"pymdp": "not-installed"}

    from builders import make_ising_ensemble  # noqa: WPS433
    from inference import coupled_policy_posterior  # noqa: WPS433
    from free_energy import total_correlation  # noqa: WPS433

    spec = make_ising_ensemble(K=2, gamma=1.0, coupling_lambda=1.0)
    facts: dict[str, float] = {}
    for lam in (0.0, 1.0, 2.0, 4.0):
        q = coupled_policy_posterior(spec, observations=[0, 0], lam=lam)
        facts[f"pymdp_total_correlation_lam_{lam:g}".replace(".", "_")] = float(
            total_correlation(q)
        )
    return facts


def main() -> None:
    facts: dict[str, object] = {}
    facts.update(_bernoulli_facts())
    facts.update(_spectral_facts())
    facts.update(_alignment_and_phase_facts())
    facts.update(_motor_attention_facts())
    facts.update(_coupling_tax_curvature())
    facts.update(_tensor_train_facts())
    facts.update(_pymdp_facts())

    out = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
    print(out)


if __name__ == "__main__":
    main()
