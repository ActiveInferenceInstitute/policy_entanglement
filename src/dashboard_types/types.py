"""Shared dashboard datatypes for interactive simulation dashboards."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, cast


def _is_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _as_float(value: object) -> float:
    return float(cast(Any, value))


def _as_float_sequence(value: object) -> list[float]:
    if _is_sequence(value):
        return [_as_float(v) for v in cast(Sequence[object], value)]
    return [_as_float(value)]


@dataclass
class Panel:
    """One Plotly figure on the dashboard."""

    panel_id: str
    title: str
    traces: list[dict[str, Any]]
    layout: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    driven_by: list[str] = field(default_factory=list)
    update_fn: str = ""
    preview_rows: int = 10


@dataclass
class Control:
    """One interactive control."""

    control_id: str
    label: str
    kind: Literal["slider", "dropdown", "toggle", "number"] = "slider"
    min: float | None = None
    max: float | None = None
    step: float | None = None
    default: Any = 0.0
    options: list[Any] = field(default_factory=list)
    option_labels: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class Invariant:
    """A single numerical invariant to validate."""

    name: str
    actual: float | Sequence[float]
    expected: float | tuple[float, float] | Sequence[float] | None = None
    tol: float = 1e-9
    kind: Literal[
        "equal",
        "le",
        "ge",
        "in_range",
        "monotone_increasing",
        "monotone_decreasing",
        "finite",
        "nonneg",
        "array_close",
    ] = "equal"
    description: str = ""

    def evaluate(self) -> tuple[bool, str]:
        """Return ``(passed, witness)``."""
        try:
            if self.kind == "equal":
                a = _as_float(self.actual)
                e = _as_float(self.expected)
                diff = abs(a - e)
                return diff <= self.tol, f"|{a:.6g} - {e:.6g}| = {diff:.3e} (tol={self.tol:.1e})"
            if self.kind == "le":
                a = _as_float(self.actual)
                e = _as_float(self.expected)
                return a <= e + self.tol, f"{a:.6g} <= {e:.6g} + {self.tol:.1e}"
            if self.kind == "ge":
                a = _as_float(self.actual)
                e = _as_float(self.expected)
                return a >= e - self.tol, f"{a:.6g} >= {e:.6g} - {self.tol:.1e}"
            if self.kind == "in_range":
                a = _as_float(self.actual)
                lo, hi = _as_float_sequence(self.expected)[:2]
                ok = (lo - self.tol) <= a <= (hi + self.tol)
                return ok, f"{lo:.6g} <= {a:.6g} <= {hi:.6g} (tol={self.tol:.1e})"
            if self.kind in ("monotone_increasing", "monotone_decreasing"):
                seq = _as_float_sequence(self.actual)
                worst = 0.0
                inc = self.kind == "monotone_increasing"
                for x, y in zip(seq, seq[1:], strict=False):
                    delta = (y - x) if inc else (x - y)
                    if delta < -self.tol:
                        worst = min(worst, delta)
                ok = worst >= -self.tol
                arrow = "<=" if inc else ">="
                return ok, (
                    f"worst out-of-order step = {worst:.3e} (tol={self.tol:.1e}, "
                    f"sequence length {len(seq)}, expect a_i {arrow} a_{{i+1}})"
                )
            if self.kind == "finite":
                if _is_sequence(self.actual):
                    vals = _as_float_sequence(self.actual)
                    bad = [i for i, v in enumerate(vals) if not math.isfinite(v)]
                    ok = not bad
                    return (
                        ok,
                        (
                            f"all finite ({len(vals)} values)"
                            if ok
                            else f"non-finite at indices {bad[:8]}{'...' if len(bad) > 8 else ''}"
                        ),
                    )
                a = _as_float(self.actual)
                ok = math.isfinite(a)
                return ok, f"value = {a!r}"
            if self.kind == "nonneg":
                if _is_sequence(self.actual):
                    vals = _as_float_sequence(self.actual)
                    worst = min(vals) if vals else 0.0
                    ok = worst >= -self.tol
                    return ok, f"min = {worst:.6g} (tol={self.tol:.1e})"
                a = _as_float(self.actual)
                return a >= -self.tol, f"value = {a:.6g} (tol={self.tol:.1e})"
            if self.kind == "array_close":
                actual_values = _as_float_sequence(self.actual)
                expected_values = _as_float_sequence(self.expected)
                if len(actual_values) != len(expected_values):
                    return False, f"length mismatch: actual={len(actual_values)}, expected={len(expected_values)}"
                worst = 0.0
                bad_idx = -1
                for i, (av, ev) in enumerate(zip(actual_values, expected_values, strict=True)):
                    d = abs(av - ev)
                    if d > worst:
                        worst, bad_idx = d, i
                return worst <= self.tol, (
                    f"max |delta| = {worst:.3e} at index {bad_idx} (tol={self.tol:.1e}, length {len(actual_values)})"
                )
        except Exception as exc:  # pragma: no cover - defensive
            return False, f"evaluation error: {exc!r}"
        return False, f"unknown kind {self.kind!r}"

__all__ = ["Control", "Invariant", "Panel"]
