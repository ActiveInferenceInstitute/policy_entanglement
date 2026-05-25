"""Manuscript paths excluded from body prose, equation discovery, and VAR scans."""

from __future__ import annotations

MANUSCRIPT_NON_BODY_MD: frozenset[str] = frozenset(
    {
        "README.md",
        "AGENTS.md",
        "INDEX.md",
        "SYNTAX.md",
        "preamble.md",
    }
)

__all__ = ["MANUSCRIPT_NON_BODY_MD"]
