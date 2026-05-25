"""Domain-scoped coverage meta-tests: dashboard_types and interactive dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboard_types import dashboard as dash_mod
from reporting import _interactive_dashboard_local as idash

PROJECT = Path(__file__).resolve().parent.parent.parent


def test_interactive_dashboard_local_json_helpers(tmp_path: Path) -> None:
    assert idash._git_rev(tmp_path / "not_a_git_repo") == "unknown"
    assert idash._git_dirty(tmp_path / "not_a_git_repo") is False

    class _NumpyLike:
        __module__ = "numpy.ndarray"

        def tolist(self) -> list[int]:
            return [1, 2]

    assert idash._to_jsonable(_NumpyLike()) == [1, 2]

    class _Scalar:
        __module__ = "numpy.float64"

        def item(self) -> float:
            return 3.5

    assert idash._to_jsonable(_Scalar()) == pytest.approx(3.5)
    assert idash._to_jsonable(float("inf")) is None
    assert idash._to_jsonable({Path("/a"): 1}) == {"/a": 1}


def test_interactive_dashboard_local_full_render_bundle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(idash, "_git_rev", lambda repo_root=None: "abc123")
    monkeypatch.setattr(idash, "_git_dirty", lambda repo_root=None: True)

    dash = idash.InteractiveDashboard(
        title="Local dashboard",
        subtitle="fallback renderer",
        project_name="actinf",
        repo_root=tmp_path,
    )
    dash.set_payload({"path": tmp_path / "source", "nan": float("nan"), "items": {2, 1}})
    dash.set_hyperparameters({"long": list(range(8)), "short": [1, 2]})
    dash.set_meta(answer=Path("meta.json"), value=float("-inf"))
    dash.add_dropdown(
        "choice",
        "Choice",
        options=[1, "two"],
        default="two",
        option_labels=["one", "two"],
        description="select one",
    )
    dash.add_toggle("flag", "Flag", default=True, description="binary switch")
    dash.add_panel(
        idash.Panel(
            panel_id="p",
            title="Panel",
            description="Panel description",
            traces=[{"x": [1, 2], "y": [3, 4], "type": "scatter"}],
            layout={"title": "Plot"},
            driven_by=["choice"],
            update_fn="return Plotly.relayout(panelId, {title: String(controls.choice)});",
            preview_rows=3,
        )
    )
    dash.add_invariant(idash.Invariant("ok", actual=1.0, expected=1.0, description="passes"))
    dash.add_invariant(idash.Invariant("bad", actual=2.0, expected=1.0, description="fails"))
    dash.add_table("rows", [{"path": tmp_path / "row", "value": float("nan")}])
    dash.add_note("rendered locally")

    invariant_text = dash.render_invariants_text()
    assert "git status:   dirty" in invariant_text
    assert "PASS] ok" in invariant_text
    assert "FAIL] bad" in invariant_text

    summary = dash.render_summary_text()
    assert "[0 ... 7] (len=8)" in summary
    assert "rendered locally" in summary

    bundle = dash.to_json()
    assert bundle["git_dirty"] is True
    assert bundle["panels"][0]["preview_rows"] == 3
    assert bundle["invariants"][1]["passed"] is False

    paths = dash.write(
        html_path=tmp_path / "dashboard.html",
        json_path=tmp_path / "dashboard.json",
        txt_path=tmp_path / "summary.txt",
        invariants_path=tmp_path / "invariants.txt",
    )
    assert set(paths) == {"html", "json", "summary", "invariants"}
    html = paths["html"].read_text(encoding="utf-8")
    assert "cdn.plot.ly" in html
    assert 'data-tab="raw"' in html
    assert "CONTROL_VALUES" in html

    written = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert written["payload"]["nan"] is None
    assert written["tables"]["rows"][0]["value"] is None


def test_interactive_dashboard_fallback_render_path(tmp_path: Path) -> None:
    """Standalone fallback HTML path when infrastructure is not importable."""
    from reporting._interactive_dashboard_fallback import render_interactive_dashboard_html

    html = render_interactive_dashboard_html(
        title="Fallback",
        subtitle="",
        project_name="actinf",
        repo_root=tmp_path,
        panel_count=0,
        control_count=0,
        invariant_count=0,
        bundle_json='{"controls":[],"panels":[],"invariants":[],"payload":{}}',
    )
    assert "cdn.plot.ly" in html
    assert "controls-root" in html


def test_dashboard_types_main_success_and_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    html = tmp_path / "d.html"
    js = tmp_path / "d.json"
    inv = tmp_path / "inv.txt"
    summary = tmp_path / "sum.txt"
    argv = [
        "--num",
        "11",
        "--html-out",
        str(html),
        "--json-out",
        str(js),
        "--invariants-out",
        str(inv),
        "--summary-out",
        str(summary),
    ]
    dash_mod.main(argv)

    class _Dash:
        def write(self, **kwargs: object) -> dict[str, Path]:
            return {"html": html, "json": js, "invariants": inv, "summary": summary}

        def evaluate_invariants(self) -> list[dict[str, object]]:
            return [{"name": "bad", "passed": False}]

    monkeypatch.setattr(dash_mod, "build_dashboard_payload", lambda args: {})
    monkeypatch.setattr(dash_mod, "build_dashboard", lambda args, payload: _Dash())
    with pytest.raises(SystemExit) as exc:
        dash_mod.main(argv)
    assert exc.value.code == 1
