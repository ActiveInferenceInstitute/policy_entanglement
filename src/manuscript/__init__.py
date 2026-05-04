"""Manuscript-rendering and validation toolkit.
"""

from __future__ import annotations

from registry import (  # noqa: F401
    CitationRegistry,
    LabelsRegistry,
    Registry,
    load_registry,
)
from tokens import (  # noqa: F401
    CITATION_RE,
    EQ_RE,
    EQREF_RE,
    FIG_RE,
    FIGREF_RE,
    VAR_RE,
    iter_tokens,
)
from renderer import (  # noqa: F401
    RenderResult,
    render_section,
    render_all,
)
from bibliography import auto_bibliography  # noqa: F401
from validation import (  # noqa: F401
    ManuscriptValidationReport,
    validate_manuscript_tree,
)

__all__ = [
    "Registry",
    "LabelsRegistry",
    "CitationRegistry",
    "load_registry",
    "CITATION_RE",
    "EQ_RE",
    "EQREF_RE",
    "FIG_RE",
    "FIGREF_RE",
    "VAR_RE",
    "iter_tokens",
    "RenderResult",
    "render_section",
    "render_all",
    "auto_bibliography",
    "ManuscriptValidationReport",
    "validate_manuscript_tree",
]
