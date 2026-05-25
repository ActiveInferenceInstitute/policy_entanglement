"""Edge-case tests for `scripts/manuscript_variables.py::_format_lambda_key`.

The function builds JSON keys like ``ising_mi_at_lam_05`` that the
manuscript renderer references through ``[[VAR:...]]`` tokens.  A
typo or ambiguity in the formatter would silently break the manuscript
substitution map, so this file pins both the historical contract
(integers and ``0.X`` short-form) and the recently-fixed latent bug
(values like ``10.5`` no longer collide with ``105``).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# Load `scripts/manuscript_variables.py` directly so the test does not
# depend on `scripts` being a package.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
_SRC = Path(__file__).resolve().parent.parent / "src"
for _sub in ("", "lean", "simulation", "visualizations"):
    p = _SRC / _sub if _sub else _SRC
    sys.path.insert(0, str(p))

_spec = importlib.util.spec_from_file_location("manuscript_variables", _SCRIPTS / "manuscript_variables.py")
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_format_lambda_key = _mod._format_lambda_key  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "lam,expected",
    [
        # Integer-valued — drop the ".0" suffix.
        (0.0, "0"),
        (1.0, "1"),
        (2.0, "2"),
        (3.0, "3"),
        (50.0, "50"),
        (-1.0, "-1"),
        # Leading 0. — compact short form (the historical contract).
        (0.5, "05"),
        (0.9, "09"),
        # Non-leading-zero decimals — underscore-escape.
        (1.5, "1_5"),
        (2.5, "2_5"),
        # Regression: 10.5 must not collapse to "105" (would alias 105).
        (10.5, "10_5"),
        (20.5, "20_5"),
        (100.5, "100_5"),
    ],
)
def test_format_lambda_key_stable_outputs(lam: float, expected: str) -> None:
    assert _format_lambda_key(lam) == expected


def test_format_lambda_key_injective_on_distinct_lambdas() -> None:
    """The formatter must be injective on all sentinel λ values used by
    the manuscript pipeline so that JSON keys never collide.
    """
    candidates = [
        0.0,
        0.25,
        0.5,
        0.9,
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
        4.0,
        10.5,
        20.5,
        50.0,
        100.5,
    ]
    keys = [_format_lambda_key(x) for x in candidates]
    assert len(set(keys)) == len(keys), f"_format_lambda_key produced duplicate keys: {keys}"
