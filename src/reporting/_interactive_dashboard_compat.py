"""Infrastructure-first helpers for the local interactive dashboard."""

from __future__ import annotations

try:
    from infrastructure.reporting._interactive_html import (
        PLOTLY_CDN,
        render_interactive_dashboard_html,
    )
    from infrastructure.reporting._interactive_models import (
        _git_dirty,
        _git_rev,
        _to_jsonable,
        _utc_now,
    )

    USE_INFRA_HTML = True
except ImportError:  # standalone checkout without template on PYTHONPATH
    from reporting._interactive_dashboard_fallback import (
        PLOTLY_CDN,
        _git_dirty,
        _git_rev,
        _to_jsonable,
        _utc_now,
        render_interactive_dashboard_html,
    )

    USE_INFRA_HTML = False

__all__ = [
    "PLOTLY_CDN",
    "USE_INFRA_HTML",
    "_git_dirty",
    "_git_rev",
    "_to_jsonable",
    "_utc_now",
    "render_interactive_dashboard_html",
]
