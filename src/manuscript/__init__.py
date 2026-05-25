"""Manuscript-rendering and validation toolkit."""

from __future__ import annotations

from .bibliography import auto_bibliography, write_references_bib  # noqa: F401
from .registry import (  # noqa: F401
    CitationRegistry,
    LabelsRegistry,
    Registry,
    load_registry,
)
from .renderer import (  # noqa: F401
    RenderResult,
    render_all,
    render_section,
)
from .tokens import (  # noqa: F401
    CITATION_RE,
    EQ_RE,
    EQREF_RE,
    FIG_RE,
    FIGREF_RE,
    VAR_RE,
    iter_tokens,
)
from .validation import (  # noqa: F401
    ManuscriptValidationReport,
    validate_manuscript_tree,
)
from .variables import (  # noqa: F401
    build_manuscript_variables,
    write_manuscript_variables,
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
    "write_references_bib",
    "ManuscriptValidationReport",
    "validate_manuscript_tree",
    "build_manuscript_variables",
    "write_manuscript_variables",
]
