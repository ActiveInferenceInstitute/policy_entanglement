from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROSE_GLOBS = (
    "README.md",
    "AGENTS.md",
    "docs/**/*.md",
    "manuscript/**/*.md",
    "manuscript/refs/labels.yaml",
    "lean/**/*.md",
)

EXCLUDED = {
    ROOT / "manuscript" / "refs" / "citations.yaml",
}

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

BRITISH_TO_AMERICAN = {
    "artefact": "artifact",
    "behaviour": "behavior",
    "behavioural": "behavioral",
    "catalogue": "catalog",
    "catalogued": "cataloged",
    "centralise": "centralize",
    "centralised": "centralized",
    "centralises": "centralizes",
    "centre": "center",
    "centred": "centered",
    "colour": "color",
    "defence": "defense",
    "favour": "favor",
    "factorised": "factorized",
    "factorisation": "factorization",
    "formalised": "formalized",
    "formalisation": "formalization",
    "formalise": "formalize",
    "formalises": "formalizes",
    "generalisation": "generalization",
    "initialise": "initialize",
    "initialised": "initialized",
    "initialisation": "initialization",
    "marginalisation": "marginalization",
    "maximisation": "maximization",
    "minimisation": "minimization",
    "modelling": "modeling",
    "neighbourhood": "neighborhood",
    "normalised": "normalized",
    "normaliser": "normalizer",
    "normalisation": "normalization",
    "offence": "offense",
    "optimisation": "optimization",
    "parameterisation": "parameterization",
    "parametrisation": "parameterization",
    "programme": "program",
    "realisation": "realization",
    "regulariser": "regularizer",
    "renormalisation": "renormalization",
    "specialisation": "specialization",
    "unnormalised": "unnormalized",
    "visualisation": "visualization",
}


def _strip_code_spans(text: str) -> str:
    """Remove Markdown code blocks and inline code before prose scanning."""

    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def _prose_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in PROSE_GLOBS:
        files.update(ROOT.glob(pattern))
    return sorted(
        p for p in files if p.is_file() and p not in EXCLUDED and not (set(p.relative_to(ROOT).parts) & EXCLUDED_PARTS)
    )


def test_reader_facing_docs_use_american_english() -> None:
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) + r"s?" for k in BRITISH_TO_AMERICAN) + r")\b",
        flags=re.IGNORECASE,
    )

    offenses: list[str] = []
    for path in _prose_files():
        stripped = _strip_code_spans(path.read_text(encoding="utf-8"))
        for line_no, line in enumerate(stripped.splitlines(), start=1):
            match = pattern.search(line)
            if match:
                word = match.group(1).lower().rstrip("s")
                suggestion = BRITISH_TO_AMERICAN.get(word, "American spelling")
                offenses.append(f"{path.relative_to(ROOT)}:{line_no}: `{match.group(1)}` -> `{suggestion}`")

    assert not offenses, "British spellings in prose:\n" + "\n".join(offenses)
