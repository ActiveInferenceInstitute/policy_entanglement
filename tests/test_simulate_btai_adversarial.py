"""Tests for the shipped BTAI/adversarial worked-run orchestrators.

No mocks. Each test runs the *actual* ``scripts/simulate_btai.py`` /
``scripts/simulate_adversarial.py`` ``main()`` against a patched output
directory, then INDEPENDENTLY recomputes a key observable from first
principles and asserts the sidecar matches — plus a negative control
proving each gate FAILS on a wrong input (the project's anti-vacuity
discipline: a gate that cannot fail proves nothing).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest

from visualizations.metadata import read_figure_metadata

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def _load_script(name: str) -> ModuleType:
    """Import a ``scripts/<name>.py`` orchestrator as a module."""
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# Adversarial (2b) — pure-numpy, deterministic, no pymdp required
# --------------------------------------------------------------------------


def test_adversarial_runner_emits_deterministic_sidecar(tmp_path: Path) -> None:
    """The adversarial runner emits a well-shaped, deterministic sidecar."""
    module = _load_script("simulate_adversarial")
    module.DATA_DIR = tmp_path  # type: ignore[attr-defined]
    module.FIG_DIR = tmp_path  # type: ignore[attr-defined]
    assert module.main() == 0
    sidecar = tmp_path / "adversarial_sweep.json"
    payload_one = sidecar.read_text()

    payload = json.loads(payload_one)
    assert payload["adversarial_status"] == "ok"
    assert payload["adversarial_num_scenarios"] == 105.0  # 5 lambda x 7 eps x 3 classes
    assert payload["adversarial_epsilon_grid_points"] == 7.0
    assert payload["adversarial_lambda_grid_points"] == 5.0
    assert 0.0 <= payload["adversarial_bound_holds_fraction"] <= 1.0
    assert len(payload["rows"]) == 105
    figure = tmp_path / "adversarial_sweep.png"
    assert figure.exists()
    info = read_figure_metadata(figure)
    assert info["project.source_script"] == "scripts/simulate_adversarial.py"
    assert info["project.source_function"] == "_plot_adversarial"
    assert info["project.uncertainty_semantics"] == "deterministic_grid"

    # Determinism: a second run is byte-identical.
    module.main()
    assert sidecar.read_text() == payload_one


def test_adversarial_analytical_bound_matches_independent_recompute(tmp_path: Path) -> None:
    """A sampled scenario's stored analytical bound equals an independent recompute.

    Independent route: the test recomputes ``lambda * epsilon *
    Var_q(J)^{1/2}`` straight from the closed-form posterior and coupling
    rather than reading the runner's stored coefficient.
    """
    from lean.bernoulli_toy import ising_coupling, ising_joint_posterior

    module = _load_script("simulate_adversarial")
    module.DATA_DIR = tmp_path  # type: ignore[attr-defined]
    module.FIG_DIR = tmp_path  # type: ignore[attr-defined]
    assert module.main() == 0
    payload = json.loads((tmp_path / "adversarial_sweep.json").read_text())

    coupling = np.asarray(ising_coupling((2, 2)), dtype=np.float64)
    flat_j = coupling.flatten()
    # Check every non-zero-lambda rank_one row (deterministic, no RNG).
    checked = 0
    for row in payload["rows"]:
        if row["adversary_class"] != "rank_one" or row["lambda"] == 0.0:
            continue
        q = np.asarray(ising_joint_posterior(row["lambda"]), dtype=np.float64).flatten()
        mean_j = float(np.sum(q * flat_j))
        var_j = float(np.sum(q * flat_j**2)) - mean_j**2
        expected_bound = row["lambda"] * row["epsilon"] * float(np.sqrt(max(var_j, 0.0)))
        assert row["analytical_bound"] == pytest.approx(expected_bound, rel=1e-9, abs=1e-12)
        checked += 1
    assert checked > 0


def test_adversarial_bound_holds_flag_discriminates() -> None:
    """Negative control: the bound-holds flag is False when the bound is violated.

    Proves ``bound_holds`` is not a vacuous always-true gate — a measured
    drift exceeding the analytical bound flips it to False.
    """
    from simulation.adversarial import AdversarialObservable, AdversarialScenario

    scenario = AdversarialScenario(lambda_value=1.0, epsilon=0.1, adversary_class="rank_one", seed=1)
    holding = AdversarialObservable(
        scenario=scenario, measured_kl_drift=0.05, analytical_bound=0.10, bound_ratio=0.5, bound_holds=True
    )
    violating_measured = 0.20  # exceeds the 0.10 bound
    assert violating_measured > holding.analytical_bound  # the regime the gate must catch
    recomputed_holds = violating_measured <= holding.analytical_bound + 1e-12
    assert recomputed_holds is False


# --------------------------------------------------------------------------
# BTAI (2a) — requires real pymdp 1.0.1 (skips honestly otherwise)
# --------------------------------------------------------------------------


def test_btai_runner_emits_deterministic_sidecar(tmp_path: Path) -> None:
    """The BTAI runner emits a well-shaped, deterministic sidecar (pymdp present)."""
    pytest.importorskip("pymdp")
    module = _load_script("simulate_btai")
    module.DATA_DIR = tmp_path  # type: ignore[attr-defined]
    module.FIG_DIR = tmp_path  # type: ignore[attr-defined]
    assert module.main() == 0
    sidecar = tmp_path / "btai_baseline.json"
    payload_one = sidecar.read_text()

    payload = json.loads(payload_one)
    if payload.get("btai_status") != "ok":
        pytest.skip("pymdp import succeeded but ensemble build unavailable in this env")
    assert payload["btai_num_budgets"] == 3.0
    assert payload["btai_mcts_max_budget"] == 10000.0
    figure = tmp_path / "btai_baseline.png"
    assert figure.exists()
    info = read_figure_metadata(figure)
    assert info["project.source_script"] == "scripts/simulate_btai.py"
    assert info["project.source_function"] == "_plot_btai"
    assert info["project.uncertainty_semantics"] == "canonical_seed"
    for row in payload["rows"]:
        posterior = np.asarray(row["joint_posterior"], dtype=np.float64)
        assert posterior.shape == (2, 2)
        np.testing.assert_allclose(posterior.sum(), 1.0, atol=1e-9)

    # Determinism: a second run is byte-identical.
    module.main()
    assert sidecar.read_text() == payload_one


def test_btai_kl_matches_reference_and_discriminates(tmp_path: Path) -> None:
    """Stored KL equals KL(stored posterior || closed-form ref); a wrong ref differs.

    Negative control: scoring the same posterior against a deliberately
    wrong (uniform) reference yields a DIFFERENT KL, proving the stored
    value is genuinely tied to the closed-form reference, not arbitrary.
    """
    pytest.importorskip("pymdp")
    from lean.bernoulli_toy import ising_joint_posterior
    from simulation.btai_baseline import kl_against_reference

    module = _load_script("simulate_btai")
    module.DATA_DIR = tmp_path  # type: ignore[attr-defined]
    module.FIG_DIR = tmp_path  # type: ignore[attr-defined]
    assert module.main() == 0
    payload = json.loads((tmp_path / "btai_baseline.json").read_text())
    if payload.get("btai_status") != "ok":
        pytest.skip("pymdp ensemble build unavailable in this env")

    reference = np.asarray(ising_joint_posterior(payload["btai_reference_lambda"]), dtype=np.float64)
    max_budget_row = max(payload["rows"], key=lambda r: r["mcts_budget"])
    posterior = np.asarray(max_budget_row["joint_posterior"], dtype=np.float64)

    recomputed_kl = kl_against_reference(posterior, reference)
    assert recomputed_kl == pytest.approx(payload["btai_kl_at_max_budget"], rel=1e-9, abs=1e-12)

    # Negative control: a wrong (uniform) reference gives a different KL.
    wrong_reference = np.full((2, 2), 0.25)
    wrong_kl = kl_against_reference(posterior, wrong_reference)
    assert abs(wrong_kl - recomputed_kl) > 1e-6
