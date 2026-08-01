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


def test_interactive_dashboard_fallback_vendors_plotly_when_provided(tmp_path: Path) -> None:
    """A vendored payload is inlined for an offline-capable page; None falls
    back to the CDN tag.  The renderer never performs network I/O
    (RedTeam C7, 2026-08-01)."""
    from reporting._interactive_dashboard_fallback import (
        _plotly_script_tag,
        render_interactive_dashboard_html,
    )

    # Isolated unit check: pure tag builder.
    assert "cdn.plot.ly" in _plotly_script_tag(None)
    inline = _plotly_script_tag(b"window.Plotly = {};")
    assert "cdn.plot.ly" not in inline
    assert "window.Plotly" in inline

    render_kwargs: dict[str, object] = {
        "title": "V",
        "subtitle": "",
        "project_name": "actinf",
        "repo_root": tmp_path,
        "panel_count": 0,
        "control_count": 0,
        "invariant_count": 0,
        "bundle_json": "{}",
    }
    # Render with a vendored payload -> no CDN reference, no external <script src>.
    html = render_interactive_dashboard_html(**render_kwargs, plotly_js=b"window.Plotly = {};")  # type: ignore[arg-type]
    assert "cdn.plot.ly" not in html
    assert "window.Plotly" in html

    # Render without a payload -> documented CDN fallback remains.
    html_cdn = render_interactive_dashboard_html(**render_kwargs)  # type: ignore[arg-type]
    assert "cdn.plot.ly" in html_cdn


class _FakeUrl:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self) -> _FakeUrl:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self, _n: int = -1) -> bytes:
        return self._payload


class _FakeRaisingUrl:
    def __enter__(self) -> _FakeRaisingUrl:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self, _n: int = -1) -> bytes:
        raise OSError("network down")


def test_plotly_vendored_fetch_deterministic_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The opt-in vendoring fetch must cover success, HTML-page, oversize,
    and failure branches deterministically without real network I/O."""
    from reporting import _interactive_dashboard_fallback as fb

    monkeypatch.setenv("REPORTING_VENDOR_PLOTLY", "1")

    # Success: payload inlined.
    monkeypatch.setattr(fb, "_PLOTLY_CACHE_SET", False)
    monkeypatch.setattr(fb.urllib.request, "urlopen", lambda _url, timeout=None: _FakeUrl(b"window.Plotly={};"))
    assert fb.vendored_plotly_js() == b"window.Plotly={};"

    # Oversize payload -> None (CDN fallback).
    monkeypatch.setattr(fb, "_PLOTLY_CACHE_SET", False)
    monkeypatch.setattr(
        fb.urllib.request, "urlopen", lambda _url, timeout=None: _FakeUrl(b"x" * (fb._PLOTLY_MAX_BYTES + 1))
    )
    assert fb.vendored_plotly_js() is None

    # HTML error page -> None.
    monkeypatch.setattr(fb, "_PLOTLY_CACHE_SET", False)
    monkeypatch.setattr(fb.urllib.request, "urlopen", lambda _url, timeout=None: _FakeUrl(b"<html>oops</html>"))
    assert fb.vendored_plotly_js() is None

    # Network failure (raises on read) -> None.
    monkeypatch.setattr(fb, "_PLOTLY_CACHE_SET", False)
    monkeypatch.setattr(fb.urllib.request, "urlopen", lambda _url, timeout=None: _FakeRaisingUrl())
    assert fb.vendored_plotly_js() is None

    # urlopen itself raising URLError (connect failure) -> None.
    monkeypatch.setattr(fb, "_PLOTLY_CACHE_SET", False)
    monkeypatch.setattr(
        fb.urllib.request,
        "urlopen",
        lambda _url, timeout=None: (_ for _ in ()).throw(OSError("connect")),
    )
    assert fb.vendored_plotly_js() is None

    # Retry-success: first attempt fails, second succeeds.
    attempts: list[int] = []

    def _flaky_urlopen(_url: str, timeout: float | None = None) -> object:
        attempts.append(1)
        if len(attempts) == 1:
            return (_ for _ in ()).throw(OSError("transient"))
        return _FakeUrl(b"window.Plotly={};")

    monkeypatch.setattr(fb, "_PLOTLY_CACHE_SET", False)
    monkeypatch.setattr(fb.urllib.request, "urlopen", _flaky_urlopen)
    assert fb.vendored_plotly_js() == b"window.Plotly={};"
    assert len(attempts) >= 2

    # Cache-hit path: once the cache flag is set, later calls return the cached
    # payload without touching the network again.
    urlopen_calls: list[int] = []
    monkeypatch.setattr(
        fb.urllib.request,
        "urlopen",
        lambda _url, timeout=None: urlopen_calls.append(1) or _FakeUrl(b"window.Plotly={};"),
    )
    fb._PLOTLY_CACHE_SET = False
    fb._PLOTLY_CACHE = b"window.Plotly={};"
    assert fb.vendored_plotly_js() == b"window.Plotly={};"  # cache now set
    n_after_first = len(urlopen_calls)
    assert fb.vendored_plotly_js() == b"window.Plotly={};"
    assert len(urlopen_calls) == n_after_first  # hit the cache, no new urlopen

    # Non-UTF-8 payload -> CDN fallback tag (UnicodeDecodeError branch).
    bad = b"\xff\xfe\x00invalid"
    tag = fb._plotly_script_tag(bad)
    assert "cdn.plot.ly" in tag

    # Opt-in disabled -> None without touching the network.
    monkeypatch.setenv("REPORTING_VENDOR_PLOTLY", "")
    monkeypatch.setattr(fb, "_PLOTLY_CACHE_SET", False)
    assert fb.vendored_plotly_js() is None


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
