"""Shared dashboard datatypes and the project dashboard builder."""

from dashboard_types.cli import parse_dashboard_args
from dashboard_types.types import Control, Invariant, Panel

__all__ = [
    "Control",
    "Invariant",
    "Panel",
    "build_dashboard",
    "build_dashboard_payload",
    "main",
    "parse_dashboard_args",
    "write_dashboard",
]


def __getattr__(name: str) -> object:
    if name in {"build_dashboard", "build_dashboard_payload", "main", "write_dashboard"}:
        from dashboard_types import dashboard as mod

        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
