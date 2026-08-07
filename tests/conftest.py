"""Shared Pytest fixtures and configuration for MechAI tests."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from mechai.common.config import clear_config_cache

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def isolate_env() -> Generator[None, None, None]:
    """Isolate environment variables between tests to prevent test pollution."""
    # Save original MECHAI_* environment variables
    original_env = {k: v for k, v in os.environ.items() if k.startswith("MECHAI_")}

    # Clear cached config singleton
    clear_config_cache()

    yield

    # Restore environment
    for key in list(os.environ.keys()):
        if key.startswith("MECHAI_") and key not in original_env:
            del os.environ[key]

    for key, value in original_env.items():
        os.environ[key] = value

    clear_config_cache()
