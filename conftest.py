"""Root conftest — adds each service's package dir and project root to sys.path
so that test modules can import `bridge.*`, `ping_monitor.*`, `alert_service.*`,
and `shared.*` without install."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent

for service in ("bridge", "ping_monitor", "alert_service"):
    pkg = _root / "services" / service / service
    if pkg.is_dir():
        sys.path.insert(0, str(_root / "services" / service))

# Project root for shared/
sys.path.insert(0, str(_root))
