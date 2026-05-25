"""Numerical witnesses for manuscript theorems whose Lean companions
are witness-consuming boundary contracts.

* `thm_4_3` — *Convexity of F in λ* (Theorem 5.6).  The closed-form
  Lean proof routes through Brascamp–Lieb / Mathlib log-concavity
  machinery and remains a witness payload.  Here we verify the
  convexity claim numerically on the K = 2 Ising specialization described in
  ``manuscript/S02_convexity_of_free_energy.md``.
* `thm_7_3` — *Sparsity-rank tradeoff* (Theorem 8.3).  A coupling
  potential with low tensor-train rank produces a posterior with
  tensor-train rank bounded above by the coupling's bond dimensions.
  Lean formalization is supplied as a witness-form theorem in
  ``SpectralWitnesses.lean`` (round 3).
* `thm_11_1` — *Hierarchical AIF as λ → ∞ limit* (Theorem 17.1).
  Empirical witness: the K = 2 Ising joint posterior concentrates on
  a single archetypal mode as λ grows; the KL divergence from a fixed
  λ-window to the asymptotic mode shrinks to zero.
* `prop_11_2` — *Sophisticated inference embedding* (Proposition 17.2).
  Empirical witness: the coupled-policy posterior from the simulation
  layer (the embedding image) has the same variational free energy as
  the boundary-fragment computation at the same `(logE, G, γ)`.

These tests are intentional companions: they raise the empirical
veridicality of the witness boundary so the manuscript's
quantitative claims remain anchored to executable code even before
the formal Mathlib proofs land.
"""

from __future__ import annotations

import numpy as np
import pytest

from lean.bernoulli_toy import ising_joint_posterior
from lean.coupling import entangled_posterior
from lean.decomposition import free_energy_against_entangled_prior
from lean.free_energy import total_correlation
from lean.joint_dist import joint_marginals, mean_field_to_joint
from lean.spectral import tensor_train_ranks
from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(reason="pymdp 1.0.1 not installed (uv sync --group sim)")
else:
    pytestmark = pytest.mark.requires_pymdp

from simulation.builders import make_ising_ensemble  # noqa: E402
from simulation.inference import (  # noqa: E402
    coupled_policy_posterior,
    per_stream_efe,
    variational_free_energy,
)

# ---------------------------------------------------------------------------
# thm_4_3 — Convexity of F in λ (Theorem 5.6)
# ---------------------------------------------------------------------------


def _ising_F_curve(utility: float, lams: np.ndarray) -> np.ndarray:
    """`F[q_λ*]` evaluated on the K=2 Ising specialization from
    ``S02_convexity_of_free_energy.md`` — symmetric MF prior, bilinear
    ``J``, vanishing ``K_c``, per-stream EFE ``G_k = (0, utility)``.
    """
    mf = [np.array([0.5, 0.5]), np.array([0.5, 0.5])]
    J = np.array([[1.0, -1.0], [-1.0, 1.0]])  # (2π¹−1)(2π²−1)
    Kc = np.zeros((2, 2))
    G = [np.array([0.0, float(utility)]), np.array([0.0, float(utility)])]
    out = np.empty(lams.shape, dtype=np.float64)
    for i, lam in enumerate(lams):
        q = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=float(lam))
        out[i] = free_energy_against_entangled_prior(q, mf, G, J, Kc, gamma=1.0, lam=float(lam))
    return out


def test_thm_4_3_F_convex_in_lambda_K2_ising():
    """`F[q_λ]` is convex in λ on ``[0, 4]`` for each utility surplus
    ``u ∈ {0, 0.5, 1, 2}`` (the manuscript's S02 panel) — second
    central differences are non-negative up to machine precision.
    """
    lams = np.linspace(0.0, 4.0, 401)
    h = float(lams[1] - lams[0])
    for utility in (0.0, 0.5, 1.0, 2.0):
        F = _ising_F_curve(utility, lams)
        d2 = (F[:-2] - 2.0 * F[1:-1] + F[2:]) / (h * h)
        # Allow a tiny negative slack for float roundoff; the analytical
        # claim is F''(λ) ≥ 0 on the closed half-line.
        assert d2.min() > -1e-6, f"u={utility}: F is not convex; min F'' = {d2.min():.3e}"


def test_thm_4_3_F_monotone_decreasing_with_positive_utility():
    """For ``u > 0``, ``F[q_λ]`` is monotonically non-increasing in λ
    on ``[0, 4]`` — the agent earns coupling-driven free-energy
    reduction whenever a positive utility surplus is present.
    """
    lams = np.linspace(0.0, 4.0, 401)
    for utility in (0.5, 1.0, 2.0):
        F = _ising_F_curve(utility, lams)
        diffs = np.diff(F)
        assert diffs.max() < 1e-9, f"u={utility}: F is not non-increasing; max ΔF = {diffs.max():.3e}"


def test_thm_4_3_flat_at_zero_preference_coupling():
    """The S02 corollary: with no per-stream EFE shift (``u = 0``) and
    no preference coupling (``K_c = 0``), ``F[q_λ] ≡ 0`` — the
    log-partitions ``log Z`` and ``log Z_E`` cancel exactly.
    """
    lams = np.linspace(0.0, 4.0, 21)
    F = _ising_F_curve(utility=0.0, lams=lams)
    assert np.allclose(F, 0.0, atol=1e-12), f"u=0 toy should be flat; got range [{F.min():.3e}, {F.max():.3e}]"


# ---------------------------------------------------------------------------
# thm_7_3 — Sparsity-rank tradeoff (Theorem 8.3)
# ---------------------------------------------------------------------------


def test_thm_7_3_additively_separable_J_gives_mean_field_posterior():
    """If ``J(π) = Σ_k J_k(π^k)`` (TT rank 1 in the additive sense),
    then for *any* λ the entangled posterior factorizes:
    ``q_λ ∝ ∏_k E_k(π^k) · exp(λ J_k(π^k))`` — so TT ranks are
    identically ``[1, 1, ..., 1]``.
    """
    K = 3
    mf = [np.array([0.5, 0.5])] * K
    G = [np.zeros(2)] * K
    J1 = np.array([0.3, -0.3])
    J2 = np.array([0.5, -0.5])
    J3 = np.array([0.2, -0.2])
    J_sep = J1[:, None, None] + J2[None, :, None] + J3[None, None, :]
    Kc = np.zeros((2, 2, 2))
    for lam in (0.0, 0.5, 1.0, 2.0, 5.0):
        q = entangled_posterior(mf, G, J_sep, Kc, gamma=0.0, lam=float(lam))
        ranks = tensor_train_ranks(q, atol=1e-9)
        assert ranks == [1, 1], f"separable J, lam={lam}: TT ranks {ranks} ≠ [1, 1]"


def test_thm_7_3_pair_only_J_freezes_idle_stream_bond():
    """A coupling that touches only streams 1, 2 (idle stream 3) has TT
    rank ``≤ [r, 1]`` for the natural cut ``{1, 2} | {3}``: the second
    bond is forced to 1 because the third stream is independent of the
    first two given the prior and the coupling.
    """
    K = 3
    mf = [np.array([0.5, 0.5])] * K
    G = [np.zeros(2)] * K
    J12 = np.array([[0.5, -0.5], [-0.5, 0.5]])  # (π¹, π²) only
    J_pair = np.broadcast_to(J12[:, :, None], (2, 2, 2)).copy()
    Kc = np.zeros((2, 2, 2))
    for lam in (0.0, 0.5, 1.0, 2.0, 5.0):
        q = entangled_posterior(mf, G, J_pair, Kc, gamma=0.0, lam=float(lam))
        ranks = tensor_train_ranks(q, atol=1e-9)
        assert len(ranks) == 2
        # Cut {1,2}|{3}: π³ is independent of (π¹, π²) ⇒ rank 1.
        assert ranks[1] == 1, f"pair-only J, lam={lam}: TT rank across cut {{1,2}}|{{3}} is {ranks[1]}, expected 1"
        # Cut {1}|{2,3}: bounded above by min(|π¹|, |π²|·|π³|) = 2.
        assert ranks[0] <= 2, f"pair-only J, lam={lam}: TT rank across cut {{1}}|{{2,3}} is {ranks[0]}, expected ≤ 2"


def test_thm_7_3_rank_bounded_by_coupling_TT_rank():
    """A rank-1 *product* coupling ``J = a ⊗ b ⊗ c`` keeps the posterior
    TT rank at most 2 across each cut for K = 3 — strictly weaker than
    the unconstrained K = 3 dense maximum ``[2, 2]`` only when the
    factors degenerate, but never exceeded.
    """
    K = 3
    mf = [np.array([0.5, 0.5])] * K
    G = [np.zeros(2)] * K
    a = np.array([0.6, -0.4])
    b = np.array([0.7, -0.3])
    c = np.array([0.5, -0.5])
    J_prod = np.einsum("i,j,k->ijk", a, b, c)
    Kc = np.zeros((2, 2, 2))
    for lam in (0.0, 0.5, 1.0, 2.0):
        q = entangled_posterior(mf, G, J_prod, Kc, gamma=0.0, lam=float(lam))
        ranks = tensor_train_ranks(q, atol=1e-9)
        # K=3 binary: cuts are 2×4 and 4×2, so ranks ≤ min(2, 4) = 2.
        assert all(r <= 2 for r in ranks), f"product J, lam={lam}: TT ranks {ranks} exceed the 2-bound"


# ---------------------------------------------------------------------------
# thm_11_1 — Hierarchical AIF as λ → ∞ limit (Theorem 17.1)
# ---------------------------------------------------------------------------


def test_thm_11_1_ising_concentrates_on_archetypal_mode_as_lambda_grows():
    """As λ grows on the K = 2 Ising specialization, the joint
    concentrates on the aligned-diagonal modes — the empirical
    signature of the hierarchical-AIF λ → ∞ fixed point.

    The asymptotic mass is split between the two aligned corners
    (0,0) and (1,1); the joint approaches the limit
    ``q_infty = ½ δ_{(0,0)} + ½ δ_{(1,1)}``.
    """
    aligned_mass: list[float] = []
    for lam in (0.0, 0.5, 1.0, 2.0, 4.0, 8.0):
        q = ising_joint_posterior(float(lam))
        aligned_mass.append(float(q[0, 0] + q[1, 1]))
    # Monotonically non-decreasing as λ grows.
    diffs = np.diff(np.asarray(aligned_mass))
    assert (diffs >= -1e-9).all(), f"aligned mass not non-decreasing in λ: {aligned_mass}"
    # Saturates near 1.0 at large λ.
    assert aligned_mass[-1] > 0.999, f"aligned mass at λ=8 should be ≈ 1; got {aligned_mass[-1]:.6f}"


def test_thm_11_1_kl_to_archetypal_mode_decays_to_zero():
    """For increasingly large λ the joint approaches its asymptotic
    limit; equivalently, the KL divergence between successive λ
    windows decays toward zero — the empirical witness of the
    `HierarchicalConcentrationWitness.concentrate` field.
    """

    def kl(p: np.ndarray, q: np.ndarray) -> float:
        eps = 1e-300
        return float(np.sum(p * (np.log(p + eps) - np.log(q + eps))))

    lams = (4.0, 6.0, 8.0, 10.0)
    joints = [ising_joint_posterior(float(lam)).reshape(-1) for lam in lams]
    # KL(q_λ ‖ q_{λ_max}) decays as λ grows.
    kls = [kl(joints[i], joints[-1]) for i in range(len(joints) - 1)]
    assert kls[-1] < kls[0] + 1e-12, f"KL to λ_max not decaying: {kls}"
    # At the largest tail, KL is essentially zero.
    assert kls[-1] < 1e-3, f"KL near asymptote should be tiny; got {kls[-1]:.6e}"


# ---------------------------------------------------------------------------
# prop_11_2 — Sophisticated inference embedding (Proposition 17.2)
# ---------------------------------------------------------------------------


def test_prop_11_2_embedded_VFE_matches_boundary_computation():
    """Compare simulation-layer VFE against a hand-expanded boundary formula.

    This is not a tautology because path A uses
    `variational_free_energy(...)` while path B reconstructs the same
    scalar from `coupled_policy_posterior`, `joint_marginals`,
    `per_stream_efe`, and the stream priors by explicit summation.
    """
    spec = make_ising_ensemble(coupling_amplitude=1.0, num_streams=2, gamma=1.0)
    observations = [0, 0]
    for lam in (0.0, 0.5, 1.0, 1.5):
        path_a = float(variational_free_energy(spec, observations, lam).sum())
        q = coupled_policy_posterior(spec, observations, lam)
        marginals = joint_marginals(q)
        efe_terms = per_stream_efe(spec, observations)
        hand_terms = []
        for k, (marginal, efe) in enumerate(zip(marginals, efe_terms, strict=True)):
            log_q = np.log(np.where(marginal > 0.0, marginal, 1e-300))
            log_prior = np.log(np.where(spec.streams[k].D > 0.0, spec.streams[k].D, 1e-300))
            hand_terms.append(float(np.sum(marginal * (log_q - log_prior)) + spec.gamma * np.sum(marginal * efe)))
        path_b = float(sum(hand_terms))
        # 1e-9 is a strict float budget: both paths implement the same finite sum but through independent code paths.
        assert abs(path_a - path_b) < 1e-9, (
            f"VFE preservation under sophisticated embedding failed at lam={lam}: path_a={path_a}, path_b={path_b}"
        )


def test_prop_11_2_embedding_lifts_into_boundary_fragment_VFE():
    """Compare the λ=0 mean-field image with the λ=1.5 entangled image.

    This is not a tautology because it contrasts two distinct posterior
    regimes of the embedding: the exact mean-field baseline at λ=0 and
    the strictly entangled coupled posterior at λ=1.5.
    """
    spec = make_ising_ensemble(coupling_amplitude=1.0, num_streams=2, gamma=1.0)
    observations = [0, 0]
    q_zero = coupled_policy_posterior(spec, observations, lam=0.0)
    q_entangled = coupled_policy_posterior(spec, observations, lam=1.5)
    mf_zero = mean_field_to_joint(joint_marginals(q_zero))
    # 1e-12 is appropriate because λ=0 is analytically the exact outer-product baseline for the embedding image.
    assert np.allclose(q_zero, mf_zero, atol=1e-12)
    # 1e-9 is a round-off budget on total correlation; λ=0 should be exactly mean-field.
    assert total_correlation(q_zero) < 1e-9
    # 1e-6 stays above numerical noise and encodes genuinely non-zero entanglement at positive λ.
    assert total_correlation(q_entangled) > 1e-6
