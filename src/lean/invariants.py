"""Numerical invariants for the policy-entanglement simulation suite.

These are pure-compute checks (no I/O, no plotting, no pymdp) executed
against the analytical / numerical mirrors of the Lean boundary fragment.
They expose the *witnesses* of the manuscript theorems so that:

- the simulation dashboard can show pass/fail badges with concrete witnesses,
- a plaintext ``invariants.txt`` can be diff-checked in CI,
- the test suite can pin specific tolerances on the same checks.

Each function returns one or more :class:`reporting.interactive_dashboard.Invariant`
instances and is *configurable* — callers pass the same hyperparameters that
drive the figures (so changing the sweep grid here flows through to dashboard,
plaintext report, and tests in lockstep).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from dashboard_types.dashboard import Invariant

from .bernoulli_toy import (
    coupling_phase_at,
    empirical_mutual_information,
    ising_coupling,
    ising_free_energy_curve,
    ising_joint_posterior,
    ising_mutual_information,
    optimal_lambda,
    symmetric_mean_field_prior,
)
from .coupling import coupling_log_weight, entangled_log_weight_affine_in_lambda
from .decomposition import (
    coupling_pays_for_itself,
    entanglement_decomposition_rhs,
    free_energy_against_entangled_prior,
)
from .free_energy import (
    joint_entropy,
    shannon_entropy,
    total_correlation,
    total_correlation_via_kl,
)
from .joint_dist import is_mean_field, joint_marginals

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class SweepGrid:
    """Configurable λ-grid driving every invariant family."""

    lam_min: float
    lam_max: float
    num: int

    def values(self) -> ArrayF:
        return np.linspace(self.lam_min, self.lam_max, self.num)


# ---------------------------------------------------------------------------
# Per-family invariant builders
# ---------------------------------------------------------------------------


def ising_invariants(grid: SweepGrid, agreement_tol: float = 1e-9) -> list[Invariant]:
    """Closed-form vs empirical agreement, MI saturation bound, and monotonicity.

    Witnesses:
      - ``ising_tc_at_zero``: total correlation of the λ=0 Ising joint is zero
      - ``ising_mf_at_zero``: λ=0 joint is mean-field
      - ``ising_mi_agreement``: ``max |I(λ) - TC(q_λ)|`` over the grid
      - ``ising_mi_monotone_in_|λ|``: ``I(|λ|)`` is monotone-increasing
      - ``ising_mi_below_log2``: every grid sample obeys ``I(λ) < log 2``
      - ``ising_kl_tc_equivalence``: ``I(q) == KL(q ‖ ∏_k q^k)``
    """
    lams = grid.values()
    q0 = ising_joint_posterior(0.0)
    out: list[Invariant] = []

    out.append(
        Invariant(
            name="ising_tc_at_zero",
            actual=float(total_correlation(q0)),
            expected=0.0,
            tol=1e-12,
            kind="equal",
            description="Total correlation of the λ=0 Ising joint must be exactly 0",
        )
    )
    out.append(
        Invariant(
            name="ising_mean_field_at_zero",
            actual=1.0 if is_mean_field(q0, atol=1e-12) else 0.0,
            expected=1.0,
            tol=0.0,
            kind="equal",
            description="λ=0 joint is bit-exact mean-field (Lean: bernoulli_toy)",
        )
    )

    closed = np.array([ising_mutual_information(float(lam)) for lam in lams])
    empirical = np.array([empirical_mutual_information(float(lam)) for lam in lams])
    residual = float(np.max(np.abs(closed - empirical)))
    out.append(
        Invariant(
            name="ising_mi_agreement",
            actual=residual,
            expected=0.0,
            tol=agreement_tol,
            kind="equal",
            description=(
                "Closed-form I(λ) = log 2 - H_b(σ(λ)) agrees with the empirical "
                "total correlation of the lambda-entangled joint to floating tol"
            ),
        )
    )

    # |λ|-symmetric monotone: pick non-negative half and check increasing
    nonneg = lams[lams >= 0]
    closed_nonneg = np.array([ising_mutual_information(float(lam)) for lam in nonneg])
    out.append(
        Invariant(
            name="ising_mi_monotone_in_lambda",
            actual=closed_nonneg.tolist(),
            tol=1e-12,
            kind="monotone_increasing",
            description="I(λ) is monotone-increasing on λ ≥ 0",
        )
    )

    out.append(
        Invariant(
            name="ising_mi_below_log2",
            actual=float(np.max(closed)),
            expected=float(np.log(2.0)),
            tol=1e-12,
            kind="le",
            description="Closed-form I(λ) < log 2 for every grid sample",
        )
    )

    # KL ≡ TC equivalence at a probe λ
    probe = float(grid.lam_min + 0.5 * (grid.lam_max - grid.lam_min))
    q_probe = ising_joint_posterior(probe)
    out.append(
        Invariant(
            name="ising_tc_kl_equivalence_at_probe",
            actual=float(abs(total_correlation(q_probe) - total_correlation_via_kl(q_probe))),
            expected=0.0,
            tol=1e-12,
            kind="equal",
            description=(f"At λ={probe:.4g}: I(q) computed two ways agrees (direct TC vs KL(q ‖ ∏ q^k))"),
        )
    )

    return out


def free_energy_invariants(
    grid: SweepGrid,
    utilities: Sequence[float] = (0.0, 0.5, 1.0, 2.0),
) -> list[Invariant]:
    """Free-energy curve must be monotone-decreasing in |λ| for any utility ≥ 0
    (the U-shape collapses to monotone whenever the utility surplus is real-valued).
    """
    lams = grid.values()
    out: list[Invariant] = []
    for u in utilities:
        nonneg = lams[lams >= 0]
        F = np.array([ising_free_energy_curve(float(lam), float(u)) for lam in nonneg])
        out.append(
            Invariant(
                name=f"free_energy_monotone_decreasing_u={u:g}",
                actual=F.tolist(),
                tol=1e-9,
                kind="monotone_decreasing",
                description=f"F(λ; u={u:g}) is monotone-decreasing on λ ≥ 0",
            )
        )
    return out


def optimal_lambda_invariants(
    deltas: Sequence[float] = (0.0, 0.1, 0.5, 0.9),
    delta_max: float = 1.0,
) -> list[Invariant]:
    """``optimal_lambda(0) = 0`` and ``optimal_lambda`` is monotone in δ."""
    out: list[Invariant] = []
    out.append(
        Invariant(
            name="optimal_lambda_at_zero",
            actual=optimal_lambda(0.0, delta_max=delta_max),
            expected=0.0,
            tol=1e-15,
            kind="equal",
            description="optimal_lambda(δ=0) = 0",
        )
    )
    seq = [optimal_lambda(float(d), delta_max=delta_max) for d in sorted(deltas)]
    out.append(
        Invariant(
            name="optimal_lambda_monotone_in_delta",
            actual=seq,
            tol=1e-12,
            kind="monotone_increasing",
            description="λ*(δ) is monotone-increasing in δ on [0, δ_max)",
        )
    )
    return out


def phase_invariants(
    lam_c1: float = 0.5,
    lam_c2: float = 2.5,
) -> list[Invariant]:
    """Coupling phase classifier: covers all three regions and respects ordering."""
    out: list[Invariant] = []
    samples = {
        "disordered": lam_c1 - 0.1,
        "mixed_low": lam_c1 + 0.1,
        "mixed_mid": 0.5 * (lam_c1 + lam_c2),
        "mixed_high": lam_c2 - 0.1,
        "frozen": lam_c2 + 0.1,
    }
    expected_phase = {
        "disordered": "disordered",
        "mixed_low": "mixed",
        "mixed_mid": "mixed",
        "mixed_high": "mixed",
        "frozen": "frozen",
    }
    for tag, lam in samples.items():
        actual = coupling_phase_at(float(lam), lam_c1=lam_c1, lam_c2=lam_c2)
        out.append(
            Invariant(
                name=f"phase_classifier_{tag}",
                actual=1.0 if actual == expected_phase[tag] else 0.0,
                expected=1.0,
                tol=0.0,
                kind="equal",
                description=(f"phase(λ={lam:.4g} | {lam_c1}, {lam_c2}) == {expected_phase[tag]!r} (got {actual!r})"),
            )
        )
    return out


def marginal_invariants(grid: SweepGrid) -> list[Invariant]:
    """Marginal-entropy and joint-entropy bounds over the entire λ-sweep.

    For any joint q over a finite alphabet of size M:

      - 0 ≤ H(q) ≤ log M
      - 0 ≤ H(q^k) ≤ log |X_k|
      - H(q) ≤ Σ_k H(q^k)  (equivalent to TC ≥ 0)
    """
    lams = grid.values()
    out: list[Invariant] = []
    H_joint: list[float] = []
    H_marg_sum: list[float] = []
    for lam in lams:
        q = ising_joint_posterior(float(lam))
        Hj = joint_entropy(q)
        H_joint.append(Hj)
        margs = joint_marginals(q)
        H_marg_sum.append(sum(shannon_entropy(m) for m in margs))
    out.append(
        Invariant(
            name="joint_entropy_below_log_size",
            actual=float(max(H_joint)),
            expected=float(np.log(4.0)),  # K=2, two-state per stream → 4 outcomes
            tol=1e-12,
            kind="le",
            description="H(q) ≤ log 4 over the entire λ-sweep",
        )
    )
    out.append(
        Invariant(
            name="tc_nonneg_over_sweep",
            actual=[Hm - Hj for Hj, Hm in zip(H_joint, H_marg_sum, strict=True)],
            tol=1e-12,
            kind="nonneg",
            description="Σ H(q^k) - H(q) = TC ≥ 0 at every grid point",
        )
    )
    return out


@dataclass(frozen=True)
class DecompositionSweepPoint:
    """One grid point of the K=2 decomposition residual sweep."""

    lam: float
    residual: float
    lhs: float
    rhs_total: float


def decomposition_sweep_points(grid: SweepGrid) -> list[DecompositionSweepPoint]:
    """Evaluate decomposition LHS/RHS residuals at every ``grid`` point."""
    mf = list(symmetric_mean_field_prior())
    ja = ising_coupling()
    kc = np.zeros_like(ja)
    gs = [np.zeros(2, dtype=np.float64), np.zeros(2, dtype=np.float64)]
    gamma = 1.0
    points: list[DecompositionSweepPoint] = []
    for lam in grid.values():
        lam_f = float(lam)
        q = ising_joint_posterior(lam_f)
        rhs = entanglement_decomposition_rhs(q, mf, gs, ja, kc, gamma, lam_f)
        lhs_v = free_energy_against_entangled_prior(q, mf, gs, ja, kc, gamma, lam_f)
        points.append(
            DecompositionSweepPoint(
                lam=lam_f,
                residual=float(abs(lhs_v - rhs.total)),
                lhs=float(lhs_v),
                rhs_total=float(rhs.total),
            )
        )
    return points


def decomposition_invariants_from_points(
    points: Sequence[DecompositionSweepPoint],
) -> list[Invariant]:
    """Theorem 5.1 numerical witness from a precomputed decomposition sweep."""
    if not points:
        raise ValueError("decomposition_invariants_from_points requires at least one sweep point")
    residuals = [point.residual for point in points]
    lhs = [point.lhs for point in points]
    totals = [point.rhs_total for point in points]
    return [
        Invariant(
            name="decomposition_lhs_eq_rhs_max_residual",
            actual=float(max(residuals)),
            expected=0.0,
            tol=1e-9,
            kind="equal",
            description=(
                "max |F[q_λ] − Σ RHS_terms| over the sweep is below 1e-9; "
                "Theorem 5.1 numerical witness on the K=2 Ising toy"
            ),
        ),
        Invariant(
            name="decomposition_lhs_eq_rhs_array_close",
            actual=lhs,
            expected=totals,
            tol=1e-9,
            kind="array_close",
            description=("Pointwise F[q_λ] ≈ entanglement_decomposition_rhs(...).total across the entire sweep grid"),
        ),
        Invariant(
            name="decomposition_lhs_finite",
            actual=lhs,
            kind="finite",
            description="LHS F[q_λ] is finite at every grid point",
        ),
    ]


def decomposition_invariants(grid: SweepGrid) -> list[Invariant]:
    """Theorem 5.1 numerical witness: ``F[q_λ]`` (Gibbs LHS) equals the
    sum of the four RHS bookkeeping terms produced by
    :func:`entanglement_decomposition_rhs` to floating tolerance.

    The K=2 Ising toy at zero per-stream EFE makes this exact (the
    ``coupling_prior_term`` and ``coupling_cost_term`` are non-trivial,
    ``sum_marginal_free_energies`` carries the marginal split, and
    ``multi_information_term`` carries ``I(q_λ)``).
    """
    return decomposition_invariants_from_points(decomposition_sweep_points(grid))


def coupling_pays_invariants(
    grid: SweepGrid,
    lam_threshold: float = 0.1,
) -> list[Invariant]:
    """Coupling-pays-for-itself: for every λ above ``lam_threshold`` the
    λ-entangled joint has strictly higher total correlation than the
    λ=0 baseline. Mirrors ``CouplingVerdict.pays`` in the Lean fragment.
    """
    lams = grid.values()
    q_zero = ising_joint_posterior(0.0)
    pays = []
    fail_lams = []
    for lam in lams:
        lam_f = float(lam)
        if lam_f <= lam_threshold:
            continue
        q_lam = ising_joint_posterior(lam_f)
        verdict = coupling_pays_for_itself(q_lam, q_zero, atol=1e-12)
        pays.append(1.0 if verdict else 0.0)
        if not verdict:
            fail_lams.append(lam_f)
    if not pays:
        return []
    return [
        Invariant(
            name=f"coupling_pays_above_lambda={lam_threshold:g}",
            actual=float(min(pays)),
            expected=1.0,
            tol=0.0,
            kind="equal",
            description=(
                f"Every λ > {lam_threshold:g} produces TC(q_λ) > TC(q_0); failures at λ = {fail_lams or '[]'}"
            ),
        )
    ]


def affine_log_weight_invariants(
    lam_grid: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0),
) -> list[Invariant]:
    """Theorem 7.4 (e-geodesic): the log-weight of the entangled prior is
    affine in λ: ``log E_λ(π)·exp(−γλK_c) = a + b·λ`` with ``a=0`` and
    ``b = J(π) − γK_c(π)``.

    **Honest scope (do not over-read):** ``coupling_log_weight`` is affine
    in λ *by construction*, so this is a CONSISTENCY guard, not an
    independent validation of the e-geodesic property — it confirms a
    two-point linear fit of the canonical pointwise weight (across the
    ``lam_grid`` endpoints) agrees with the closed-form decomposition
    ``(a, b)`` from ``entangled_log_weight_affine_in_lambda``. It catches a
    typo/desync between those two presentations or a λ-independent term
    creeping into the weight; it cannot detect an error in the shared
    closed form itself. The genuinely independent numerical probe (routing
    through the normalized posterior) lives in
    ``tests/test_geometry.py::test_e_geodesic_slope_via_normalized_posterior``.
    """
    Ja = ising_coupling()
    Kc = np.zeros_like(Ja)
    lam_lo, lam_hi = float(lam_grid[0]), float(lam_grid[-1])
    out: list[Invariant] = []
    for gamma in (0.0, 0.5, 1.0):
        for pi in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            # CLAIM: the closed-form affine decomposition `a + b·λ`.
            a_claim, b_claim = entangled_log_weight_affine_in_lambda(Ja, Kc, gamma, pi)
            # Two-point linear fit of the canonical weight across the grid.
            w_lo = float(coupling_log_weight(Ja, Kc, gamma, lam_lo)[pi])
            w_hi = float(coupling_log_weight(Ja, Kc, gamma, lam_hi)[pi])
            measured_slope = (w_hi - w_lo) / (lam_hi - lam_lo)
            measured_intercept = w_lo - measured_slope * lam_lo
            out.append(
                Invariant(
                    name=f"affine_a_zero_gamma={gamma:g}_pi={pi[0]}{pi[1]}",
                    actual=measured_intercept,
                    expected=a_claim,
                    tol=1e-12,
                    kind="equal",
                    description=(
                        f"Theorem 7.4 consistency: canonical-weight intercept = a (=0) at γ={gamma:g}, π={pi}"
                    ),
                )
            )
            out.append(
                Invariant(
                    name=f"affine_slope_correct_gamma={gamma:g}_pi={pi[0]}{pi[1]}",
                    actual=measured_slope,
                    expected=b_claim,
                    tol=1e-12,
                    kind="equal",
                    description=(
                        f"Theorem 7.4 consistency: canonical-weight slope = b = J(π) − γ·K_c(π) at γ={gamma:g}, π={pi}"
                    ),
                )
            )
    return out


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def all_invariants(
    grid: SweepGrid,
    *,
    utilities: Sequence[float] = (0.0, 0.5, 1.0, 2.0),
    optimal_deltas: Sequence[float] = (0.0, 0.1, 0.5, 0.9),
    optimal_delta_max: float = 1.0,
    lam_c1: float = 0.5,
    lam_c2: float = 2.5,
    agreement_tol: float = 1e-9,
    coupling_pays_threshold: float = 0.1,
) -> list[Invariant]:
    """Return every invariant the dashboard / plaintext report should display."""
    out: list[Invariant] = []
    out.extend(ising_invariants(grid, agreement_tol=agreement_tol))
    out.extend(free_energy_invariants(grid, utilities=utilities))
    out.extend(optimal_lambda_invariants(deltas=optimal_deltas, delta_max=optimal_delta_max))
    out.extend(phase_invariants(lam_c1=lam_c1, lam_c2=lam_c2))
    out.extend(marginal_invariants(grid))
    out.extend(decomposition_invariants(grid))
    out.extend(coupling_pays_invariants(grid, lam_threshold=coupling_pays_threshold))
    out.extend(affine_log_weight_invariants())
    return out


__all__ = [
    "DecompositionSweepPoint",
    "SweepGrid",
    "affine_log_weight_invariants",
    "all_invariants",
    "coupling_pays_invariants",
    "decomposition_invariants",
    "decomposition_invariants_from_points",
    "decomposition_sweep_points",
    "free_energy_invariants",
    "ising_invariants",
    "marginal_invariants",
    "optimal_lambda_invariants",
    "phase_invariants",
]
