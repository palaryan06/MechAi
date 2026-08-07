"""Test MechAI package versioning."""

from __future__ import annotations

import re

import mechai


def test_version_format() -> None:
    """Verify that package version is a valid semantic version string."""
    assert hasattr(mechai, "__version__")
    assert isinstance(mechai.__version__, str)
    # Match standard semver pattern (MAJOR.MINOR.PATCH)
    assert re.match(r"^\d+\.\d+\.\d+", mechai.__version__) is not None


def test_version_exports() -> None:
    """Verify that __all__ exports __version__."""
    assert "__version__" in mechai.__all__
