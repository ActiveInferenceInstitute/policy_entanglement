"""Manuscript paths excluded from body prose, equation discovery, and VAR scans."""

from __future__ import annotations

MANUSCRIPT_NON_BODY_MD: frozenset[str] = frozenset(
    {
        "README.md",
        "AGENTS.md",
        "INDEX.md",
        "SYNTAX.md",
        "preamble.md",
        # Release-workflow symlink to ``0A_abstract.md``; keep one canonical abstract file.
        "00_abstract.md",
    }
)

__all__ = ["MANUSCRIPT_NON_BODY_MD"]
