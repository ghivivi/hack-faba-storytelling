"""Shared pytest fixtures."""

import sys
from pathlib import Path

# Make python/ importable from tests/
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))
