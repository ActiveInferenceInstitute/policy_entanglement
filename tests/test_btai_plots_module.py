"""In-process tests for :mod:`visualizations.btai_plots`."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from simulation.agents import pymdp_available
from visualizations.btai_plots import _plot_btai, run
from visualizations.metadata import read_figure_metadata


def test_plot_btai_writes_png_with_metadata(tmp_path: Path) -> None:
    reference = np.array([[0.55, 0.05], [0.05, 0.35]], dtype=np.float64)
    final = np.array([[0.45, 0.15], [0.15, 0.25]], dtype=np.float64)
    out = tmp_path / "btai_baseline.png"
    written = _plot_btai(
        budgets=[10, 100, 1000],
        kl_curve=[0.42, 0.18, 0.07],
        reference=reference,
        final_posterior=final,
        exponent=-0.25,
        out_path=out,
    )
    assert written == out
    assert out.exists() and out.stat().st_size > 0
    info = read_figure_metadata(out)
    assert info["project.source_function"] == "_plot_btai"
    assert info["project.uncertainty_semantics"] == "canonical_seed"


def test_run_writes_not_run_sentinel_when_pymdp_unavailable(tmp_path: Path) -> None:
    if pymdp_available():
        pytest.skip("pymdp installed — sentinel path covered by import guard only when sim group absent")
    rc = run(data_dir=tmp_path, fig_dir=tmp_path)
    assert rc == 0
    payload = json.loads((tmp_path / "btai_baseline.json").read_text(encoding="utf-8"))
    assert payload["btai_status"] == "not-run"


def test_run_writes_build_failure_sentinel(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import visualizations.btai_plots as mod

    monkeypatch.setattr(mod, "_build_pymdp_efe", lambda: None)
    rc = run(data_dir=tmp_path, fig_dir=tmp_path)
    assert rc == 0
    payload = json.loads((tmp_path / "btai_baseline.json").read_text(encoding="utf-8"))
    assert payload["btai_status"] == "not-run"
    assert "sim group" in str(payload["btai_note"])
