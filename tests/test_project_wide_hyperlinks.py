"""Project-wide hyperlink audit.

The existing ``manuscript.validation`` validator only walks
``manuscript/``.  This regression test extends the no-dangling-link
invariant to **every** markdown file in the project: docs/, README,
AGENTS, CONTRIBUTING, src/*/README, tests/README, and so on.

Catches drift like ``output/manuscript_rendered/`` (an obsolete
directory name) that the manuscript-only validator would miss.

Skips:
- External URLs (http, https, mailto, ftp, javascript)
- Anchor-only links (``#section-id``)
- Data URIs
- Paths under any ``output/`` tree (regenerated, may be absent in CI)
- Files inside generated dependency/cache trees such as ``.venv``,
  ``.git``, and ``.lake``
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent

LINK_RE = re.compile(r"!?\[(?P<text>[^\]]*)\]\((?P<href>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_FENCE_RE = re.compile(r"(```|~~~).*?\1", re.DOTALL)
EXCLUDED_PARTS = {
    ".git",
    ".lake",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "output",
}


def _is_external(href: str) -> bool:
    return href.startswith(("http://", "https://", "mailto:", "ftp:", "javascript:", "data:"))


def _is_generated(target_path: str) -> bool:
    """Skip paths under any ``output/`` tree — produced by later
    pipeline stages, not required at test time.
    """
    parts = target_path.split("/")
    return "output" in parts


def _candidate_files() -> list[Path]:
    """Every project-internal markdown file, excluding caches/venv/git
    and the generated ``output/`` subtree.
    """
    out: list[Path] = []
    for p in PROJECT.rglob("*.md"):
        if set(p.relative_to(PROJECT).parts) & EXCLUDED_PARTS:
            continue
        out.append(p)
    return sorted(out)


def _broken_links_in(md_path: Path) -> list[str]:
    text = CODE_FENCE_RE.sub("", md_path.read_text())
    broken: list[str] = []
    for m in LINK_RE.finditer(text):
        href = m.group("href").strip()
        if not href or _is_external(href) or href.startswith("#"):
            continue
        # Drop URL fragment
        target_path = href.split("#", 1)[0]
        if not target_path or target_path.startswith("[["):
            # Token placeholders — substituted at render time.
            continue
        if _is_generated(target_path):
            continue
        resolved = (md_path.parent / target_path).resolve()
        if not resolved.exists():
            broken.append(href)
    return broken


def test_no_broken_relative_links_anywhere_in_project() -> None:
    """Every relative `[…](path)` link in every project markdown file
    resolves to an existing file on disk.
    """
    failures: dict[str, list[str]] = {}
    for md in _candidate_files():
        broken = _broken_links_in(md)
        if broken:
            failures[str(md.relative_to(PROJECT))] = broken
    if failures:
        lines = ["Broken relative links found:"]
        for fp, bad in sorted(failures.items()):
            lines.append(f"  {fp}:")
            for href in bad:
                lines.append(f"    → {href}")
        pytest.fail("\n".join(lines))
