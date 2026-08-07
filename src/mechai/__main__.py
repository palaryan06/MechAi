"""MechAI module execution entry point (python -m mechai)."""

from __future__ import annotations

import sys

from mechai.cli import main

if __name__ == "__main__":
    sys.exit(main())
