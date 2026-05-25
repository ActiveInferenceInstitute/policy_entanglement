"""Tests for the configurable simulation invariants and dashboard builder."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from lean.invariants import (
    SweepGrid,
    affine_log_weight_invariants,
    all_invariants,
    coupling_pays_invariants,
    decomposition_invariants,
    free_energy_invariants,
    ising_invariants,
    marginal_invariants,
    optimal_lambda_invariants,
    phase_invariants,
)
from reporting.interactive_dashboard import InteractiveDashboard, Invariant, Panel

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent


# ---------------------------------------------------------------------------
# Invariant module
# ---------------------------------------------------------------------------


class TestSweepGrid:
    def test_values_shape(self):
        g = SweepGrid(0.0, 6.0, 121)
        v = g.values()
        assert v.shape == (121,)
        assert v[0] == 0.0
        assert v[-1] == 6.0

    def test_values_monotone(self):
        g = SweepGrid(-2.0, 5.0, 33)
        v = g.values()
        assert np.all(np.diff(v) > 0)


class TestIsingInvariants:
    @pytest.fixture
    def grid(self):
        return SweepGrid(0.0, 6.0, 41)

    def test_count(self, grid):
        invs = ising_invariants(grid)
        names = {i.name for i in invs}
        assert names == {
            "ising_tc_at_zero",
            "ising_mean_field_at_zero",
            "ising_mi_agreement",
            "ising_mi_monotone_in_lambda",
            "ising_mi_below_log2",
            "ising_tc_kl_equivalence_at_probe",
        }

    def test_all_pass(self, grid):
        invs = ising_invariants(grid)
        for inv in invs:
            ok, witness = inv.evaluate()
            assert ok, f"{inv.name} failed: {witness}"

    def test_agreement_tol_respected(self, grid):
        invs = ising_invariants(grid, agreement_tol=1e-15)
        # Floating residual ≈ 7.7e-16 — should still pass at 1e-15 tol.
        agreement = next(i for i in invs if i.name == "ising_mi_agreement")
        ok, _ = agreement.evaluate()
        assert ok

    def test_agreement_fail_when_tol_zero(self, grid):
        invs = ising_invariants(grid, agreement_tol=0.0)
        agreement = next(i for i in invs if i.name == "ising_mi_agreement")
        ok, witness = agreement.evaluate()
        # numerical noise > 0 — must fail
        assert not ok
        assert "tol=0.0e+00" in witness


class TestFreeEnergyInvariants:
    def test_default_utilities(self):
        g = SweepGrid(0.0, 6.0, 41)
        invs = free_energy_invariants(g)
        # 4 default utilities
        assert len(invs) == 4
        for inv in invs:
            ok, w = inv.evaluate()
            assert ok, f"{inv.name}: {w}"

    def test_custom_utilities(self):
        g = SweepGrid(0.0, 6.0, 41)
        invs = free_energy_invariants(g, utilities=(0.0, 0.5, 3.0))
        assert {i.name for i in invs} == {
            "free_energy_monotone_decreasing_u=0",
            "free_energy_monotone_decreasing_u=0.5",
            "free_energy_monotone_decreasing_u=3",
        }


class TestOptimalLambdaInvariants:
    def test_zero_anchor(self):
        invs = optimal_lambda_invariants()
        zero = next(i for i in invs if i.name == "optimal_lambda_at_zero")
        ok, _ = zero.evaluate()
        assert ok

    def test_monotone(self):
        invs = optimal_lambda_invariants(deltas=(0.0, 0.2, 0.5, 0.9))
        mono = next(i for i in invs if i.name == "optimal_lambda_monotone_in_delta")
        ok, _ = mono.evaluate()
        assert ok


class TestPhaseInvariants:
    def test_default_thresholds(self):
        for inv in phase_invariants():
            ok, _ = inv.evaluate()
            assert ok

    def test_custom_thresholds(self):
        for inv in phase_invariants(lam_c1=1.0, lam_c2=4.0):
            ok, w = inv.evaluate()
            assert ok, f"{inv.name}: {w}"


class TestMarginalInvariants:
    def test_tc_nonneg_and_bounded(self):
        g = SweepGrid(0.0, 6.0, 41)
        for inv in marginal_invariants(g):
            ok, w = inv.evaluate()
            assert ok, f"{inv.name}: {w}"


class TestDecompositionInvariants:
    def test_all_pass(self):
        g = SweepGrid(0.0, 4.0, 21)
        invs = decomposition_invariants(g)
        names = {i.name for i in invs}
        assert "decomposition_lhs_eq_rhs_max_residual" in names
        assert "decomposition_lhs_eq_rhs_array_close" in names
        assert "decomposition_lhs_finite" in names
        for inv in invs:
            ok, w = inv.evaluate()
            assert ok, f"{inv.name}: {w}"

    def test_residual_below_floating_tolerance(self):
        g = SweepGrid(0.0, 4.0, 21)
        invs = decomposition_invariants(g)
        residual = next(i for i in invs if i.name == "decomposition_lhs_eq_rhs_max_residual")
        ok, w = residual.evaluate()
        assert ok
        # The actual residual should be much smaller than the tolerance
        assert float(residual.actual) < 1e-12, w


class TestCouplingPaysInvariants:
    def test_default_threshold_passes(self):
        g = SweepGrid(0.0, 4.0, 21)
        invs = coupling_pays_invariants(g)
        assert len(invs) == 1
        ok, w = invs[0].evaluate()
        assert ok, w

    def test_no_invariants_when_grid_below_threshold(self):
        g = SweepGrid(0.0, 0.05, 5)  # all λ ≤ default threshold 0.1
        assert coupling_pays_invariants(g) == []

    def test_threshold_propagates(self):
        g = SweepGrid(0.0, 4.0, 21)
        invs = coupling_pays_invariants(g, lam_threshold=1.0)
        assert any("lambda=1" in i.name for i in invs)


class TestAffineLogWeightInvariants:
    def test_count(self):
        invs = affine_log_weight_invariants()
        # 3 gammas × 4 pi indices × 2 invariants (a=0 and slope) = 24
        assert len(invs) == 24

    def test_all_pass(self):
        for inv in affine_log_weight_invariants():
            ok, w = inv.evaluate()
            assert ok, f"{inv.name}: {w}"

    def test_a_zero_invariants_have_zero_actual(self):
        invs = affine_log_weight_invariants()
        for inv in invs:
            if inv.name.startswith("affine_a_zero_"):
                assert float(inv.actual) == 0.0


class TestAllInvariants:
    def test_default_grid(self):
        g = SweepGrid(0.0, 6.0, 41)
        invs = all_invariants(g)
        # 6 ising + 4 fe + 2 optimal + 5 phase + 2 marginal
        # + 3 decomposition + 1 coupling_pays + 24 affine = 47
        assert len(invs) == 47
        passed = [i for i in invs if i.evaluate()[0]]
        assert len(passed) == len(invs)

    def test_custom_thresholds_propagate(self):
        g = SweepGrid(0.0, 6.0, 41)
        invs = all_invariants(g, lam_c1=1.0, lam_c2=4.0)
        # Phase classifier samples must all pass with the new thresholds
        for inv in invs:
            if inv.name.startswith("phase_classifier_"):
                ok, _ = inv.evaluate()
                assert ok


# ---------------------------------------------------------------------------
# Dashboard builder
# ---------------------------------------------------------------------------


class TestInteractiveDashboard:
    def test_set_payload_jsonable(self):
        d = InteractiveDashboard(title="T")
        d.set_payload({"x": np.linspace(0, 1, 5)})
        # numpy arrays must be converted to lists (so JSON dumps cleanly)
        assert isinstance(d.payload["x"], list)
        assert len(d.payload["x"]) == 5

    def test_duplicate_panel_id_rejected(self):
        d = InteractiveDashboard(title="T")
        d.add_panel(Panel(panel_id="p", title="A", traces=[]))
        with pytest.raises(ValueError, match="duplicate panel_id"):
            d.add_panel(Panel(panel_id="p", title="B", traces=[]))

    def test_duplicate_control_id_rejected(self):
        d = InteractiveDashboard(title="T")
        d.add_slider("c", "C", min=0, max=1, step=0.1, default=0.5)
        with pytest.raises(ValueError, match="duplicate control_id"):
            d.add_slider("c", "C", min=0, max=1, step=0.1, default=0.5)

    def test_invariant_witness_format(self):
        d = InteractiveDashboard(title="T")
        d.add_invariant(Invariant("a", actual=1.0, expected=1.0, tol=1e-9))
        results = d.evaluate_invariants()
        assert results[0]["passed"]
        assert "1" in results[0]["witness"]

    def test_render_invariants_text(self, tmp_path):
        d = InteractiveDashboard(title="T", project_name="proj_x")
        d.add_invariant(Invariant("ok", actual=1.0, expected=1.0, tol=1e-9))
        d.add_invariant(Invariant("bad", actual=2.0, expected=1.0, tol=1e-9))
        text = d.render_invariants_text()
        assert "1/2 passed" in text
        assert "PASS] ok" in text
        assert "FAIL] bad" in text

    def test_write_round_trip(self, tmp_path):
        d = InteractiveDashboard(title="T", project_name="proj_x")
        d.set_payload({"x": [1, 2, 3], "y": [4, 5, 6]})
        d.add_slider("s", "S", min=0, max=1, step=0.1, default=0.5)
        d.add_panel(
            Panel(
                panel_id="p1",
                title="Panel 1",
                traces=[{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}],
            )
        )
        d.add_invariant(Invariant("nonneg_x", actual=[1, 2, 3], kind="nonneg", tol=0.0))
        outs = d.write(
            html_path=tmp_path / "dash.html",
            json_path=tmp_path / "dash.json",
            invariants_path=tmp_path / "inv.txt",
            txt_path=tmp_path / "sum.txt",
        )
        for k in ("html", "json", "invariants", "summary"):
            assert outs[k].exists() and outs[k].stat().st_size > 0
        bundle = json.loads(outs["json"].read_text())
        assert bundle["panels"][0]["panel_id"] == "p1"
        assert bundle["controls"][0]["control_id"] == "s"
        assert bundle["invariants"][0]["passed"]
        # HTML must embed plotly CDN and the bundle JSON
        html = outs["html"].read_text()
        assert "cdn.plot.ly" in html
        assert "Panel 1" in html

    def test_invariant_kinds(self):
        # equal
        ok, _ = Invariant("e", actual=0.5, expected=0.5, tol=1e-12).evaluate()
        assert ok
        # le
        ok, _ = Invariant("l", actual=0.5, expected=1.0, tol=0, kind="le").evaluate()
        assert ok
        ok, _ = Invariant("l2", actual=2.0, expected=1.0, tol=0, kind="le").evaluate()
        assert not ok
        # ge
        ok, _ = Invariant("g", actual=2.0, expected=1.0, tol=0, kind="ge").evaluate()
        assert ok
        # in_range
        ok, _ = Invariant("r", actual=0.5, expected=(0.0, 1.0), tol=0, kind="in_range").evaluate()
        assert ok
        # monotone_increasing
        ok, _ = Invariant("m", actual=[1, 2, 3, 3], tol=1e-12, kind="monotone_increasing").evaluate()
        assert ok
        ok, _ = Invariant("m2", actual=[1, 0, 3], tol=1e-12, kind="monotone_increasing").evaluate()
        assert not ok
        # monotone_decreasing
        ok, _ = Invariant("md", actual=[5, 4, 3], tol=1e-12, kind="monotone_decreasing").evaluate()
        assert ok
        # finite
        ok, _ = Invariant("f", actual=1.0, kind="finite").evaluate()
        assert ok
        ok, _ = Invariant("f2", actual=float("inf"), kind="finite").evaluate()
        assert not ok
        ok, _ = Invariant("f3", actual=[1.0, 2.0, 3.0], kind="finite").evaluate()
        assert ok
        # nonneg
        ok, _ = Invariant("n", actual=[0, 1, 2], kind="nonneg", tol=0).evaluate()
        assert ok
        ok, _ = Invariant("n2", actual=[-0.1, 1, 2], kind="nonneg", tol=0).evaluate()
        assert not ok


# ---------------------------------------------------------------------------
# build_dashboard CLI smoke test
# ---------------------------------------------------------------------------


class TestBuildDashboardCLI:
    def test_default_run(self, tmp_path):
        html = tmp_path / "d.html"
        js = tmp_path / "d.json"
        inv = tmp_path / "inv.txt"
        sm = tmp_path / "sum.txt"
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "build_dashboard.py"),
                "--num",
                "31",
                "--html-out",
                str(html),
                "--json-out",
                str(js),
                "--invariants-out",
                str(inv),
                "--summary-out",
                str(sm),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"stderr:\n{result.stderr}"
        assert html.exists() and html.stat().st_size > 1000
        bundle = json.loads(js.read_text())
        # Configurable knobs propagated:
        assert bundle["hyperparameters"]["num"] == 31
        # Every invariant must have evaluated and passed:
        n_pass = sum(1 for i in bundle["invariants"] if i["passed"])
        assert n_pass == len(bundle["invariants"]) > 10
        # Plaintext invariants file: every line either PASS or FAIL marker
        text = inv.read_text()
        assert "0 failed" in text
        assert text.count("[PASS]") >= 10

    def test_custom_thresholds(self, tmp_path):
        html = tmp_path / "d.html"
        js = tmp_path / "d.json"
        inv = tmp_path / "inv.txt"
        sm = tmp_path / "sum.txt"
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "build_dashboard.py"),
                "--num",
                "21",
                "--lam-min",
                "0",
                "--lam-max",
                "8",
                "--utilities",
                "0",
                "0.5",
                "3",
                "--lam-c1",
                "1.0",
                "--lam-c2",
                "4.0",
                "--html-out",
                str(html),
                "--json-out",
                str(js),
                "--invariants-out",
                str(inv),
                "--summary-out",
                str(sm),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"stderr:\n{result.stderr}"
        bundle = json.loads(js.read_text())
        hp = bundle["hyperparameters"]
        assert hp["num"] == 21
        assert hp["lam_max"] == 8.0
        assert hp["lam_c1"] == 1.0
        assert hp["lam_c2"] == 4.0
        assert hp["utilities"] == [0.0, 0.5, 3.0]

    def test_rejects_invalid_grid(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "build_dashboard.py"),
                "--lam-min",
                "5",
                "--lam-max",
                "2",
                "--num",
                "10",
                "--html-out",
                str(tmp_path / "x.html"),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0
        assert "lam-max" in (result.stderr + result.stdout)


# ---------------------------------------------------------------------------
# parameter_sweep CLI smoke test
# ---------------------------------------------------------------------------


class TestParameterSweepCLI:
    def test_custom_grid(self, tmp_path):
        out = tmp_path / "sweep.csv"
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "parameter_sweep.py"),
                "--num",
                "11",
                "--lam-min",
                "0",
                "--lam-max",
                "2",
                "--utilities",
                "0",
                "1",
                "--output",
                str(out),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"stderr:\n{result.stderr}"
        assert out.exists()
        rows = out.read_text().strip().splitlines()
        # header + 11 grid rows = 12
        assert len(rows) == 12
        # Custom utility columns produced (and only those):
        header = rows[0].split(",")
        assert "free_energy_u0" in header
        assert "free_energy_u1" in header
        assert "free_energy_u2" not in header

    def test_rejects_invalid_grid(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "parameter_sweep.py"),
                "--num",
                "1",
                "--output",
                str(tmp_path / "x.csv"),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0


# ---------------------------------------------------------------------------
# simulate_pymdp CLI smoke tests (pymdp-skip-aware)
# ---------------------------------------------------------------------------


class TestSimulatePymdpCLI:
    """The pymdp simulation harness now has a CLI override layer.

    pymdp is an optional ``[sim]`` group dependency, so we only verify the
    argument-parsing surface — every flag must round-trip through
    ``--help``, validation errors must fire on bad input, and the
    pymdp-absent skip path must still print the canonical message.
    """

    def test_help_renders_without_pymdp(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "simulate_pymdp.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        out = result.stdout
        # Every override flag is documented.
        for flag in (
            "--ensemble-K",
            "--gamma",
            "--coupling-lambda",
            "--sweep-lambda-min",
            "--sweep-lambda-max",
            "--sweep-num",
            "--rollout-steps",
            "--rollout-lambda",
            "--rollout-seed",
            "--observations",
            "--figure-seed",
        ):
            assert flag in out, f"{flag} missing from --help"

    def test_rejects_ensemble_k_below_two(self):
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "simulate_pymdp.py"),
                "--ensemble-K",
                "1",
                "--observations",
                "0",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0
        assert "ensemble-K" in (result.stderr + result.stdout)

    def test_rejects_observations_length_mismatch(self):
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "simulate_pymdp.py"),
                "--observations",
                "0",
            ],  # K defaults to 2 → length mismatch
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0
        assert "observations" in (result.stderr + result.stdout)

    def test_rejects_inverted_sweep_range(self):
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "simulate_pymdp.py"),
                "--sweep-lambda-min",
                "5",
                "--sweep-lambda-max",
                "2",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0
        assert "sweep-lambda-max" in (result.stderr + result.stdout)

    def test_default_invocation_skips_cleanly_without_pymdp(self):
        """When pymdp is absent the default run prints a stable skip
        message and exits 0 (so CI / run_all.py keep going).

        Two execution paths:

        * **pymdp installed** (the standard development environment): the
          subprocess-based test of the no-pymdp branch cannot be
          exercised because the import succeeds. Instead, verify
          structurally that the script's source still contains the
          no-pymdp guard and the stable skip message a CI / pipeline
          consumer relies on. This passes when the guard is present and
          fails if a future edit silently removes it.
        * **pymdp absent**: invoke the script and assert it exits 0 with
          the stable skip message on stdout.
        """
        script_path = PROJECT_ROOT / "scripts" / "simulate_pymdp.py"
        try:
            import pymdp  # noqa: F401
        except ImportError:
            # pymdp absent: exercise the real no-pymdp path via subprocess.
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert result.returncode == 0
            assert "pymdp not installed" in result.stdout
            return
        # pymdp installed: subprocess cannot exercise the no-pymdp branch
        # from within this interpreter. Verify structurally that the script
        # still carries the no-pymdp guard (a graceful skip handler) — the
        # honest invariant the CI / pipeline consumer relies on.
        source = script_path.read_text(encoding="utf-8")
        assert "pymdp not installed" in source, (
            "scripts/simulate_pymdp.py must carry the stable "
            "'pymdp not installed' skip message so CI / run_all.py "
            "keep going gracefully when the optional dependency is absent."
        )
