"""Folder-level AGENTS/README drift guard."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DOC_NAMES = {"AGENTS.md", "README.md"}
REQUIRED_DOCUMENTED_DIRS = (
    PROJECT,
    PROJECT / "docs",
    PROJECT / "docs" / "_audit",
    PROJECT / "docs" / "guides",
    PROJECT / "docs" / "guides" / "styleguide",
    PROJECT / "docs" / "modules",
    PROJECT / "docs" / "reference",
    PROJECT / "docs" / "simulation",
    PROJECT / "lean",
    PROJECT / "lean" / "ActinfPolicyEntanglement",
    PROJECT / "lean" / "FepSketches",
    PROJECT / "lean" / "MathlibProofs",
    PROJECT / "manuscript",
    PROJECT / "manuscript" / "refs",
    PROJECT / "scripts",
    PROJECT / "src",
    PROJECT / "src" / "lean",
    PROJECT / "src" / "manuscript",
    PROJECT / "src" / "simulation",
    PROJECT / "src" / "gnn",
    PROJECT / "src" / "reporting",
    PROJECT / "src" / "visualizations",
    PROJECT / "tests",
    PROJECT / "tests" / "lean",
)
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

FORBIDDEN_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\|\s*Tests collected\s*\|\s*\d+\s*\|", re.IGNORECASE), "stale test-count table"),
    (re.compile(r"\|\s*Passing\s*\|\s*\d+\s+passed", re.IGNORECASE), "stale pass/skip table"),
    (re.compile(r"\|\s*Coverage on `src/`\s*\|\s*\d", re.IGNORECASE), "stale coverage table"),
    (re.compile(r"MathlibProofs Layer \(future\)", re.IGNORECASE), "future MathlibProofs heading"),
    (re.compile(r"\b830\s+collected\b", re.IGNORECASE), "old pytest collection note"),
    (re.compile(r"\b853\b"), "old pytest collection literal"),
    (re.compile(r"\b852\s+passed\b", re.IGNORECASE), "old pytest pass literal"),
    (re.compile(r"\b97\.69\s*%"), "old coverage literal"),
    (re.compile(r"\b137\s+pages\b", re.IGNORECASE), "old PDF page literal"),
    (re.compile(r"\b5\.37\s+MB\b", re.IGNORECASE), "old PDF size literal"),
    (re.compile(r"\b6\.91\s+MB\b", re.IGNORECASE), "old PDF size literal"),
    (re.compile(r"\b40\s+(?:PNGs?|figures)\b", re.IGNORECASE), "old figure-count literal"),
    (re.compile(r"\bv0_1\b|\bv0\.1\b", re.IGNORECASE), "old MathlibProofs version label"),
    (
        re.compile(
            r"\b(behaviour|behaviours|centralise|centralised|centralises|colour|colours|"
            r"factorised|formalised|initialise|initialised|normalised|normaliser|"
            r"optimise|optimised|optimising|organisation|organised|synchronised)\b",
            re.IGNORECASE,
        ),
        "non-American spelling",
    ),
    (
        re.compile(
            r"\b(?:Theorem|Thm)\s+6\.4\b|\b(?:Proposition|Prop)\s+8\.3\b|"
            r"\b(?:Proposition|Prop)\s+9\.1\b|\bTheorem\s+8\.1\b|\bCorollary\s+8\.2\b"
        ),
        "retired theorem/proposition display number",
    ),
    (
        re.compile(
            r"(?:Current ground truth|Ground-truth snapshot|Lean Fragment Snapshot|"
            r"Last reviewed|Current local audit|Counts as of|Snapshot)\s*"
            r"(?:\([^)]*2026-05-1[23][^)]*\)|:?\s*2026-05-1[23])",
            re.IGNORECASE,
        ),
        "dated live-status heading",
    ),
)


def _folder_docs() -> list[Path]:
    return sorted(
        path
        for path in PROJECT.rglob("*.md")
        if path.name in DOC_NAMES and not (set(path.relative_to(PROJECT).parts) & EXCLUDED_PARTS)
    )


def test_folder_level_agents_and_readmes_are_discoverable() -> None:
    paths = _folder_docs()
    assert PROJECT / "AGENTS.md" in paths
    assert PROJECT / "README.md" in paths
    assert PROJECT / "tests" / "README.md" in paths
    assert PROJECT / "lean" / "ActinfPolicyEntanglement" / "AGENTS.md" in paths


def test_required_folder_levels_have_agents_and_readmes() -> None:
    missing = [
        (folder / doc_name).relative_to(PROJECT).as_posix()
        for folder in REQUIRED_DOCUMENTED_DIRS
        for doc_name in sorted(DOC_NAMES)
        if not (folder / doc_name).is_file()
    ]

    assert not missing, "\n".join(missing)


def test_folder_level_agents_and_readmes_avoid_stale_status_drift() -> None:
    offenders: list[str] = []
    for path in _folder_docs():
        rel = path.relative_to(PROJECT).as_posix()
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern, label in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    offenders.append(f"{rel}:{line_no}: {label}: {line.strip()}")

    assert not offenders, "\n".join(offenders)
