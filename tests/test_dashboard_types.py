"""Tests for :mod:`dashboard_types.dashboard` builder API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboard_types.dashboard import (
    build_dashboard,
    build_dashboard_payload,
    parse_dashboard_args,
    write_dashboard,
)


def test_parse_dashboard_args_defaults() -> None:
    args = parse_dashboard_args([])
    assert args.num == 121
    assert args.lam_min == pytest.approx(0.0)
    assert args.lam_max == pytest.approx(6.0)
    assert args.utilities == [0.0, 1.0, 2.0]


def test_parse_dashboard_args_rejects_invalid_grid() -> None:
    with pytest.raises(SystemExit):
        parse_dashboard_args(["--num", "1"])
    with pytest.raises(SystemExit):
        parse_dashboard_args(["--lam-min", "3", "--lam-max", "1"])


def test_build_dashboard_payload_shape() -> None:
    args = parse_dashboard_args(["--num", "11", "--lam-min", "0", "--lam-max", "2"])
    payload = build_dashboard_payload(args)
    assert len(payload["lambdas"]) == 11
    assert len(payload["mi_closed"]) == 11
    assert len(payload["mi_empirical"]) == 11
    assert len(payload["tc"]) == 11
    assert "fe_curves" in payload
    assert "joint_snapshots" in payload


def test_write_dashboard_emits_four_artifacts(tmp_path: Path) -> None:
    html = tmp_path / "dashboard.html"
    js = tmp_path / "payload.json"
    inv = tmp_path / "invariants.txt"
    summary = tmp_path / "summary.txt"
    args = parse_dashboard_args(
        [
            "--num",
            "21",
            "--html-out",
            str(html),
            "--json-out",
            str(js),
            "--invariants-out",
            str(inv),
            "--summary-out",
            str(summary),
        ]
    )
    paths = write_dashboard(args)
    assert paths["html"] == html
    assert html.exists() and html.stat().st_size > 500
    bundle = json.loads(js.read_text(encoding="utf-8"))
    assert bundle["hyperparameters"]["num"] == 21
    assert inv.read_text().count("[PASS]") >= 5
    assert summary.exists()

    dashboard = build_dashboard(args, build_dashboard_payload(args))
    assert len(dashboard.to_json()["panels"]) >= 4
