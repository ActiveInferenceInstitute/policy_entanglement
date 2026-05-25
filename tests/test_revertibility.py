"""Tests for the m-projection revertibility witness (T3).

The two algebraic identities being tested are:

  1. ``marginals(q_λ) == marginals(m(q_λ))``   (exact, by construction).
  2. ``KL(q_λ ‖ m(q_λ)) == I(q_λ)``           (Prop 7.3 / Theorem 5.1).

Both identities hold to floating-point tolerance on every λ.  Tests
exercise the pymdp-grounded path *and* the analytical Ising mirror
so the two routes agree.
"""

from __future__ import annotations

import numpy as np
import pytest

from lean.bernoulli_toy import ising_joint_posterior
from lean.free_energy import kl_divergence, total_correlation
from lean.joint_dist import joint_marginals, m_projection
from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(reason="pymdp 1.0.1 not installed (uv sync --group sim)")
else:
    pytestmark = pytest.mark.requires_pymdp


from simulation import hyperparameters as H  # noqa: E402
from simulation.revertibility import (  # noqa: E402
    RevertibilityRecord,
    m_projection_witness,
    revertibility_kl_equals_multiinformation_witness,
    revertibility_summary,
    revertibility_test,
)


@pytest.fixture(scope="module")
def records() -> list[RevertibilityRecord]:
    return revertibility_test(
        num_streams=int(H.PYMDP_ENSEMBLE_K),
        coupling_lambda_gen=float(H.PYMDP_ENSEMBLE_COUPLING_LAMBDA),
        gamma=float(H.PYMDP_ENSEMBLE_GAMMA),
        lambda_values=H.REVERTIBILITY_LAMBDAS,
        tolerance=float(H.REVERTIBILITY_TOLERANCE),
        kl_identity_tolerance=float(H.REVERTIBILITY_KL_IDENTITY_TOLERANCE),
    )


def test_revertibility_test_returns_one_record_per_lambda(
    records: list[RevertibilityRecord],
) -> None:
    assert len(records) == len(H.REVERTIBILITY_LAMBDAS)
    for r, lam in zip(records, H.REVERTIBILITY_LAMBDAS, strict=True):
        assert isinstance(r, RevertibilityRecord)
        assert r.lam == pytest.approx(float(lam))


def test_revertibility_marginals_match(records: list[RevertibilityRecord]) -> None:
    """Marginals of q_λ and m(q_λ) must coincide exactly (algebraic fact)."""
    for r in records:
        assert r.marginals_match, f"λ={r.lam}: max marginal diff = {r.marginal_max_abs_diff}"
        assert r.marginal_max_abs_diff <= float(H.REVERTIBILITY_TOLERANCE) + 1e-12


def test_revertibility_kl_equals_multiinformation(
    records: list[RevertibilityRecord],
) -> None:
    """``KL(q_λ ‖ m(q_λ)) == I(q_λ)`` to floating tolerance."""
    for r in records:
        assert r.kl_identity_holds, f"λ={r.lam}: residual = {r.kl_identity_residual}"
        assert r.kl_identity_residual <= float(H.REVERTIBILITY_KL_IDENTITY_TOLERANCE)


def test_revertibility_all_records_are_revertible(
    records: list[RevertibilityRecord],
) -> None:
    for r in records:
        assert r.revertible


def test_revertibility_test_validates_observations_length() -> None:
    with pytest.raises(ValueError, match="observations length"):
        revertibility_test(
            num_streams=2,
            coupling_lambda_gen=1.0,
            gamma=1.0,
            lambda_values=[0.0, 1.0],
            tolerance=1e-12,
            kl_identity_tolerance=1e-9,
            observations=[0],  # wrong length
        )


def test_m_projection_witness_on_analytical_ising_joint() -> None:
    """The analytical Ising joint should also satisfy the two identities.

    Decoupled witness — no pymdp call — so the test exercises the
    standalone :func:`m_projection_witness` helper.
    """
    for lam in (0.0, 0.5, 1.0, 2.0, 4.0):
        q = ising_joint_posterior(float(lam))
        record = m_projection_witness(
            q,
            tolerance=1e-12,
            kl_identity_tolerance=1e-9,
            lam=lam,
        )
        assert record.marginals_match
        assert record.kl_identity_holds
        # Cross-check the KL value directly.
        kl_direct = kl_divergence(q, m_projection(q))
        assert abs(record.kl_q_to_mproj - kl_direct) <= 1e-15
        # Cross-check the multi-information.
        I_direct = total_correlation(q)
        assert abs(record.multi_information - I_direct) <= 1e-12


def test_revertibility_summary_keys_and_shapes(
    records: list[RevertibilityRecord],
) -> None:
    summary = revertibility_summary(records)
    expected_keys = {
        "revertibility_num_lambdas",
        "revertibility_max_kl_residual",
        "revertibility_mean_kl_residual",
        "revertibility_max_marginal_diff",
        "revertibility_all_revertible",
        "revertibility_all_kl_identity_holds",
        "revertibility_all_marginals_match",
        "revertibility_multi_info_max",
        "revertibility_kl_to_mproj_max",
    }
    assert expected_keys.issubset(summary.keys())
    assert summary["revertibility_num_lambdas"] == float(len(records))
    assert summary["revertibility_all_revertible"] == 1.0


def test_revertibility_summary_rejects_empty() -> None:
    with pytest.raises(ValueError):
        revertibility_summary([])


def test_revertibility_kl_equals_multiinformation_witness_shape(
    records: list[RevertibilityRecord],
) -> None:
    witness = revertibility_kl_equals_multiinformation_witness(records)
    assert witness["name"] == "revertibility_kl_equals_multiinformation"
    assert witness["kind"] == "equal"
    assert witness["expected"] == 0.0
    assert isinstance(witness["actual"], float)


def test_revertibility_marginals_identity_pure_numpy() -> None:
    """Pure-NumPy reproduction of the marginals identity.

    The marginals of an m-projection are *defined* to equal the
    marginals of the original distribution (linearity of summation).
    This regression guard pins the property at the joint_dist layer.
    """
    rng = np.random.default_rng(42)
    for _ in range(5):
        q = rng.uniform(0.1, 1.0, size=(2, 2, 2))
        q /= q.sum()
        mp = m_projection(q)
        for m_orig, m_proj in zip(joint_marginals(q), joint_marginals(mp), strict=True):
            assert np.max(np.abs(m_orig - m_proj)) <= 1e-15


def test_revertibility_pipeline_write_artifacts(tmp_path) -> None:
    """CSV/JSON writers are pure I/O over witness records (no pymdp)."""
    from simulation.revertibility import RevertibilityRecord
    from simulation.revertibility_pipeline import write_revertibility_csv, write_revertibility_summary

    records = [
        RevertibilityRecord(
            lam=0.0,
            multi_information=0.0,
            kl_q_to_mproj=0.0,
            kl_identity_residual=0.0,
            marginal_max_abs_diff=0.0,
            marginals_match=True,
            kl_identity_holds=True,
            revertible=True,
        ),
        RevertibilityRecord(
            lam=1.0,
            multi_information=0.05,
            kl_q_to_mproj=0.05,
            kl_identity_residual=1e-16,
            marginal_max_abs_diff=1e-15,
            marginals_match=True,
            kl_identity_holds=True,
            revertible=True,
        ),
    ]
    csv_path = tmp_path / "pymdp_revertibility.csv"
    write_revertibility_csv(csv_path, records)
    assert csv_path.exists()
    text = csv_path.read_text()
    assert "multi_information" in text
    assert "0.000000" in text

    summary_path = tmp_path / "revertibility_summary.json"
    summary = write_revertibility_summary(summary_path, records)
    assert summary_path.exists()
    assert summary["revertibility_num_lambdas"] == 2.0
    assert summary["revertibility_all_revertible"] == 1.0
