"""Gate reporting helpers."""

from __future__ import annotations

import sys


def fail(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")
