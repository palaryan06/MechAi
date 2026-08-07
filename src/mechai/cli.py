"""MechAI command line interface and project entry point.

Provides CLI commands for checking system status, version, and active configuration.
"""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

from mechai import __version__
from mechai.common.config import LogFormat, get_config
from mechai.common.logging import configure_logging, get_logger

if TYPE_CHECKING:
    from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="mechai",
        description="MechAI - Automotive Diagnostic Reasoning Engine",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=None,
        help="Enable debug logging output.",
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        default=None,
        help="Emit structured JSON logs.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: status
    subparsers.add_parser("status", help="Display system status and configuration summary.")

    # Command: config
    subparsers.add_parser("config", help="Print loaded application configuration.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point for MechAI.

    Args:
        argv: Optional command-line argument list (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = get_config()
    except Exception as exc:
        sys.stderr.write(f"Configuration error: {exc}\n")
        return 1

    # Override config with explicit CLI flags if provided
    log_level = "DEBUG" if args.debug else config.log_level
    json_output = (
        True if args.json_logs else (config.log_format == LogFormat.JSON or config.is_production)
    )

    configure_logging(level=log_level, json_output=json_output)
    logger = get_logger("mechai.cli")

    if args.command == "config":
        sys.stdout.write(f"Environment: {config.environment.value}\n")
        sys.stdout.write(f"Log Level: {config.log_level}\n")
        sys.stdout.write(f"Log Format: {config.log_format.value}\n")
        sys.stdout.write(f"Debug Mode: {config.debug}\n")
        return 0

    if args.command == "status":
        logger.info(
            "mechai.status",
            version=__version__,
            environment=config.environment.value,
            debug=config.debug,
        )
        sys.stdout.write(
            f"MechAI v{__version__} [{config.environment.value}] - Foundation Initialized\n"
        )
        return 0

    # Default action (no subcommand specified)
    logger.info(
        "mechai.startup",
        version=__version__,
        environment=config.environment.value,
        status="ready",
    )
    sys.stdout.write(
        f"MechAI Automotive Reasoning Engine v{__version__} "
        f"(Environment: {config.environment.value})\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
