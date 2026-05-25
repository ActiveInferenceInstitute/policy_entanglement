from pathlib import Path

_DASHBOARD_SRC_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_PROJECT_ROOT = _DASHBOARD_SRC_DIR.parent

OUTPUT = DASHBOARD_PROJECT_ROOT / "output"
WEB_DIR = OUTPUT / "web"
DATA_DIR = OUTPUT / "data"
REP_DIR = OUTPUT / "reports"

__all__ = [
    "DASHBOARD_PROJECT_ROOT",
    "DATA_DIR",
    "OUTPUT",
    "REP_DIR",
    "WEB_DIR",
]
