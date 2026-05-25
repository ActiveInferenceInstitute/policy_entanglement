"""Tests for the GNN round-trip runner/script and the Lean emitter.

No mocks — runs the real runner against the shipped GNN sources into ``tmp_path``
and parses the emitted artifacts. Determinism is asserted by a byte-identical
re-run of the JSON sidecar.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnn.lean_emit import _bool_arg, _lean_float, emit_lean_structure
from gnn.parser import parse_gnn_file
from gnn.runner import FIGURE_NAME, LEAN_NAME, SIDECAR_NAME, run

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GNN_DIR = PROJECT_ROOT / "gnn"
TOY = GNN_DIR / "bernoulli_toy.gnn.md"


def test_runner_emits_sidecar_figure_and_lean(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    fig_dir = tmp_path / "figures"
    lean_out = tmp_path / "BernoulliToyGnn.lean"
    rc = run(data_dir=data_dir, fig_dir=fig_dir, gnn_dir=GNN_DIR, lean_out=lean_out)
    assert rc == 0
    assert (data_dir / SIDECAR_NAME).is_file()
    assert (fig_dir / FIGURE_NAME).is_file()
    assert lean_out.is_file()
    payload = json.loads((data_dir / SIDECAR_NAME).read_text())
    assert payload["round_trip_passes"] is True
    assert payload["negative_control_discriminates"] is True


def test_runner_sidecar_is_byte_identical_on_rerun(tmp_path: Path) -> None:
    d1, f1 = tmp_path / "d1", tmp_path / "f1"
    d2, f2 = tmp_path / "d2", tmp_path / "f2"
    run(data_dir=d1, fig_dir=f1, gnn_dir=GNN_DIR, lean_out=tmp_path / "a.lean")
    run(data_dir=d2, fig_dir=f2, gnn_dir=GNN_DIR, lean_out=tmp_path / "b.lean")
    assert (d1 / SIDECAR_NAME).read_bytes() == (d2 / SIDECAR_NAME).read_bytes()


def test_emitted_lean_is_a_typed_contract_not_a_proof() -> None:
    src = emit_lean_structure(parse_gnn_file(TOY))
    assert "structure PolicyEntanglementK2" in src
    assert "TYPED CONTRACT, not a proof" in src
    # Faithful to the parsed coupling: aligned 0.5, anti-aligned (-0.5).
    assert "(-0.5)" in src and "0.5" in src
    # Honest non-claim: it must NOT assert it proves anything.
    assert "proof" in src.lower()  # the word appears only in the non-claim
    assert "sorry" not in src and "axiom " not in src


def test_emit_lean_rejects_non_k2_model() -> None:
    model = parse_gnn_file(GNN_DIR / "k_stream_ensemble.gnn.md")
    with pytest.raises(ValueError, match="K=2 binary contract"):
        emit_lean_structure(model)


def test_lean_float_and_bool_formatting() -> None:
    assert _lean_float(0.5) == "0.5"
    assert _lean_float(-0.5) == "(-0.5)"
    assert _lean_float(0.0) == "0.0"
    assert _lean_float(2.0) == "2.0"
    assert _bool_arg(0) == "false"
    assert _bool_arg(1) == "true"


def test_script_main_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The thin orchestrator script's main() runs end-to-end."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_simulate_gnn_under_test", PROJECT_ROOT / "scripts" / "simulate_gnn.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(mod, "FIG_DIR", tmp_path / "figures")
    assert mod.main() == 0
    assert (tmp_path / "data" / SIDECAR_NAME).is_file()
