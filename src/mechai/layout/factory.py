"""Layout Engine Factory for dependency injection and instantiation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mechai.layout.zoner import GeometricLayoutZoner

if TYPE_CHECKING:
    from mechai.contracts.layout import GeometricLayoutZonerProtocol
    from mechai.layout.config import LayoutZonerConfig


class LayoutEngineFactory:
    """Factory for creating and configuring Layout Engine instances."""

    @staticmethod
    def create(
        config: LayoutZonerConfig | None = None,
    ) -> GeometricLayoutZonerProtocol:
        """Create a GeometricLayoutZoner instance satisfying GeometricLayoutZonerProtocol."""
        return GeometricLayoutZoner(config=config)
