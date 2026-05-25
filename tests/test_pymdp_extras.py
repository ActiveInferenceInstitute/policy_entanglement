"""Tests for the new pymdp statistics + visualization extras +
PNG metadata embedding contract.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from simulation.agents import pymdp_available

if not pymdp_available():
    pytestmark = pytest.mark.skip(reason="pymdp 1.0.1 not installed")


from simulation.builders import make_ising_ensemble
from simulation.inference import free_energy_curve
from simulation.statistics import (
    BundleSummary,
    pymdp_summary_statistics,
    summary_to_var_dict,
)
from visualizations.metadata import (
    figure_metadata,
    has_project_metadata,
    read_figure_metadata,
)
from visualizations.pymdp_extras import (
    plot_action_entropy_curve,
    plot_kl_to_lambda_zero,
    plot_marginal_entropy_per_stream,
    plot_pymdp_summary_panel,
)

PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _assert_png(p: Path) -> None:
    assert p.exists()
    with p.open("rb") as fh:
        assert fh.read(8) == PNG_HEADER


@pytest.fixture(scope="module")
def bundles():
    spec = make_ising_ensemble(num_streams=2, gamma=1.0, coupling_amplitude=1.0)
    lams = np.linspace(0.0, 3.0, 9)
    return free_energy_curve(spec, [0, 0], lams)


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------


def test_summary_returns_dataclass(bundles) -> None:
    s = pymdp_summary_statistics(bundles)
    assert isinstance(s, BundleSummary)
    assert s.n_lambda_points == 9
    assert s.tc_min >= -1e-9
    assert s.tc_max >= s.tc_min


def test_summary_half_saturation_within_range(bundles) -> None:
    s = pymdp_summary_statistics(bundles)
    if s.tc_max > 0:
        assert s.lambda_min <= s.lambda_at_half_saturation <= s.lambda_max


def test_summary_aligned_mass_in_unit_interval(bundles) -> None:
    s = pymdp_summary_statistics(bundles)
    for v in (s.aligned_mass_min, s.aligned_mass_max, s.aligned_mass_at_lambda_max):
        assert 0.0 - 1e-9 <= v <= 1.0 + 1e-9


def test_summary_kl_to_lambda_zero_min_is_zero(bundles) -> None:
    """KL of q_λ to q_0 is identically 0 at λ = 0 by construction."""
    s = pymdp_summary_statistics(bundles)
    assert abs(s.kl_to_lambda_zero_min) < 1e-9


def test_summary_action_mode_prob_in_unit_interval(bundles) -> None:
    s = pymdp_summary_statistics(bundles)
    assert 0.0 - 1e-9 <= s.action_mode_prob_at_lambda_max <= 1.0 + 1e-9


def test_summary_to_var_dict_returns_flat_floats(bundles) -> None:
    s = pymdp_summary_statistics(bundles)
    d = summary_to_var_dict(s)
    assert isinstance(d, dict)
    assert all(isinstance(k, str) for k in d)
    assert all(isinstance(v, float) for v in d.values())
    assert all(k.startswith("pymdp_summary_") for k in d)


def test_summary_requires_at_least_two_bundles() -> None:
    spec = make_ising_ensemble(num_streams=2)
    bs = free_energy_curve(spec, [0, 0], [0.0])
    with pytest.raises(ValueError):
        pymdp_summary_statistics(bs)


# ---------------------------------------------------------------------------
# Visualization helpers
# ---------------------------------------------------------------------------


def test_plot_action_entropy_curve(bundles, tmp_path: Path) -> None:
    p = plot_action_entropy_curve(bundles, out_path=tmp_path / "ae.png")
    _assert_png(p)


def test_plot_kl_to_lambda_zero(bundles, tmp_path: Path) -> None:
    p = plot_kl_to_lambda_zero(bundles, out_path=tmp_path / "kl.png")
    _assert_png(p)


def test_plot_marginal_entropy_per_stream(bundles, tmp_path: Path) -> None:
    p = plot_marginal_entropy_per_stream(bundles, out_path=tmp_path / "Hk.png")
    _assert_png(p)


def test_plot_pymdp_summary_panel(bundles, tmp_path: Path) -> None:
    s = pymdp_summary_statistics(bundles)
    p = plot_pymdp_summary_panel(
        bundles,
        summary=s,
        out_path=tmp_path / "panel.png",
    )
    _assert_png(p)


# ---------------------------------------------------------------------------
# Metadata embedding contract
# ---------------------------------------------------------------------------


def test_figure_metadata_returns_required_keys() -> None:
    md = figure_metadata(
        source_script="scripts/x.py",
        source_function="figure_x",
        hyperparameters={"a": 1, "b": 2.0},
    )
    assert md["project.source_script"] == "scripts/x.py"
    assert md["project.source_function"] == "figure_x"
    assert "project.git_revision" in md
    assert "project.timestamp" in md
    payload = json.loads(md["project.hyperparameters"])
    assert payload == {"a": 1, "b": 2.0}


def test_metadata_round_trips_through_png(bundles, tmp_path: Path) -> None:
    md = figure_metadata(
        source_script="scripts/test.py",
        source_function="figure_test",
        hyperparameters={"K": 2, "lam": 1.0},
    )
    p = plot_action_entropy_curve(
        bundles,
        out_path=tmp_path / "with_md.png",
        metadata=md,
    )
    info = read_figure_metadata(p)
    assert info.get("project.source_script") == "scripts/test.py"
    assert info.get("project.source_function") == "figure_test"
    assert "project.git_revision" in info
    assert "project.timestamp" in info
    assert "project.figure_statistics" in info
    payload = json.loads(info["project.hyperparameters"])
    assert payload == {"K": 2, "lam": 1.0}
    stats = json.loads(info["project.figure_statistics"])
    assert stats["axes_count"] >= 1


def test_has_project_metadata_returns_true(bundles, tmp_path: Path) -> None:
    p = plot_action_entropy_curve(
        bundles,
        out_path=tmp_path / "y.png",
        metadata=figure_metadata(
            source_script="x",
            source_function="y",
            hyperparameters={},
        ),
    )
    assert has_project_metadata(p)


def test_plot_helper_adds_statistics_metadata_without_user_metadata(
    bundles,
    tmp_path: Path,
) -> None:
    p = plot_action_entropy_curve(bundles, out_path=tmp_path / "z.png")
    assert has_project_metadata(p)
    info = read_figure_metadata(p)
    assert "project.figure_statistics" in info


def test_emitted_pymdp_pngs_carry_project_metadata() -> None:
    """Every PNG produced by the pipeline must carry our `project.*`
    reproducibility tEXt — covers analytical (`generate_figures.py`)
    and pymdp-grounded (`simulate_pymdp.py`) figures alike.
    """
    project_root = Path(__file__).resolve().parent.parent
    fig_dir = project_root / "output" / "figures"
    pngs = sorted(fig_dir.glob("*.png"))
    if not pngs:
        pytest.skip("no figure outputs present yet")
    missing = [p.name for p in pngs if not has_project_metadata(p)]
    assert not missing, f"PNGs without project.* tEXt: {missing}"


# ---------------------------------------------------------------------------
# Hardcoded numeric literal detector
# ---------------------------------------------------------------------------


def test_hardcoded_grid_literal_detector_flags_examples() -> None:
    from manuscript.validation import find_hardcoded_numeric_literals

    text = "We use a 121-point grid here."
    out = find_hardcoded_numeric_literals(text)
    assert any("121-point" in s for s in out)


def test_hardcoded_grid_literal_detector_skips_var_token() -> None:
    from manuscript.validation import find_hardcoded_numeric_literals

    text = "We use a [[VAR:param_sweep_grid_points]]-point grid here."
    out = find_hardcoded_numeric_literals(text)
    assert out == []


def test_hardcoded_seed_detector() -> None:
    from manuscript.validation import find_hardcoded_numeric_literals

    text = "We use seed = 42 throughout."
    out = find_hardcoded_numeric_literals(text)
    assert any("seed" in s.lower() for s in out)


def test_hardcoded_t_steps_detector() -> None:
    from manuscript.validation import find_hardcoded_numeric_literals

    text = "We run T = 10 steps total."
    out = find_hardcoded_numeric_literals(text)
    assert out and "T = 10 steps" in out[0]


def test_hardcoded_math_t_steps_detector() -> None:
    from manuscript.validation import find_hardcoded_numeric_literals

    text = "The short rollout ($T=10$) and long rollout ($T=100$) are compared."
    out = find_hardcoded_numeric_literals(text)
    assert any("T=10" in s for s in out)
    assert any("T=100" in s for s in out)


def test_hardcoded_linspace_detector() -> None:
    from manuscript.validation import find_hardcoded_numeric_literals

    text = "The run uses linspace(0, 4, 21) in prose."
    out = find_hardcoded_numeric_literals(text)
    assert any("linspace" in s for s in out)


def test_real_manuscript_has_no_hardcoded_numeric_literals() -> None:
    """Production manuscript should be free of grid / seed / T literals."""
    from manuscript.validation import find_hardcoded_numeric_literals

    project_root = Path(__file__).resolve().parent.parent
    offenses: dict[str, list[str]] = {}
    for src in sorted((project_root / "manuscript").glob("*.md")):
        if src.name in {"README.md", "AGENTS.md", "INDEX.md"}:
            continue
        out = find_hardcoded_numeric_literals(src.read_text())
        if out:
            offenses[src.name] = out
    assert not offenses, f"hardcoded numeric literals: {offenses}"
