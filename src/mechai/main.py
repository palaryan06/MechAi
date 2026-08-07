"""MechAI application main entry point."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from mechai.cli import main as cli_main

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Run the MechAI primary application entry point.

    Args:
        argv: Optional command line arguments.

    Returns:
        Process exit code.
    """
    return cli_main(argv)


if __name__ == "__main__":
    sys.exit(main())
