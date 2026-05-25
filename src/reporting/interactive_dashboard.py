"""Interactive dashboard facade — prefer template infrastructure when available."""

from __future__ import annotations

from dashboard_types.dashboard import Control, Invariant, Panel

try:
    from infrastructure.reporting.interactive_dashboard import InteractiveDashboard
except ImportError:  # standalone private checkout without template parent
    from reporting._interactive_dashboard_local import InteractiveDashboard

__all__ = ["Control", "InteractiveDashboard", "Invariant", "Panel"]
