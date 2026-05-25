"""Shared stale theorem/figure reference patterns for release gates."""

from __future__ import annotations

import re

STALE_FIGURE_REFERENCE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(?:Theorem|Thm)\s+6\.4\b"), "Theorem 7.4"),
    (re.compile(r"\b(?:Theorem|Thm)\s+8\.1\b"), "Theorem 9.1"),
    (re.compile(r"\b(?:Corollary|Cor)\s+8\.2\b"), "Corollary 9.2"),
    (re.compile(r"\bProp(?:osition)?\s+6\.3\b"), "Proposition 7.3"),
    (re.compile(r"\bProp(?:osition)?\s+8\.3\b"), "Proposition 7.3"),
    (re.compile(r"\bProp(?:osition)?\s+9\.1\b"), "Proposition 8.1"),
)

STALE_FIGURE_REFERENCE_REGEXES: tuple[re.Pattern[str], ...] = tuple(
    pattern for pattern, _replacement in STALE_FIGURE_REFERENCE_PATTERNS
)

__all__ = [
    "STALE_FIGURE_REFERENCE_PATTERNS",
    "STALE_FIGURE_REFERENCE_REGEXES",
]
