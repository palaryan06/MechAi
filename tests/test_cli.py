"""Test MechAI command-line interface entry points."""

from __future__ import annotations

import sys

import pytest

from mechai import __version__
from mechai.cli import build_parser, main
from mechai.main import main as app_main


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify --version flag outputs the current version and exits cleanly."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert f"mechai {__version__}" in captured.out


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify --help flag outputs usage information and exits cleanly."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "usage: mechai" in captured.out
    assert "status" in captured.out
    assert "config" in captured.out


def test_cli_default_run(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify default CLI execution returns exit code 0."""
    exit_code = main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "MechAI Automotive Reasoning Engine" in captured.out


def test_cli_status_command(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify 'status' subcommand outputs status information."""
    exit_code = main(["status"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Foundation Initialized" in captured.out


def test_cli_config_command(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify 'config' subcommand prints active configuration."""
    exit_code = main(["config"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Environment:" in captured.out
    assert "Log Level:" in captured.out


def test_app_main_entry_point(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify mechai.main.main delegates to CLI main."""
    exit_code = app_main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "MechAI Automotive Reasoning Engine" in captured.out


def test_cli_config_error_handling(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify CLI handles configuration errors with exit code 1."""
    monkeypatch.setenv("MECHAI_LOG_LEVEL", "INVALID_LEVEL")
    exit_code = main([])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Configuration error:" in captured.err


def test_main_module_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify python -m mechai entry point via runpy."""
    import runpy

    monkeypatch.setattr(sys, "argv", ["mechai"])
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("mechai", run_name="__main__", alter_sys=False)
    assert exc_info.value.code == 0


def test_build_parser() -> None:
    """Verify parser arguments and subcommands."""
    parser = build_parser()
    args = parser.parse_args(["--debug", "--json-logs", "status"])
    assert args.debug is True
    assert args.json_logs is True
    assert args.command == "status"
