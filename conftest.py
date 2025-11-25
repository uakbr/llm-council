"""Test configuration to ensure package imports work from repo root."""

import os
import sys
from pathlib import Path

# Headless Qt for CI/CLI runs.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Prepend repository root to sys.path for module resolution in tests.
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
