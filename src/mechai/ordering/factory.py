"""Factory and dependency injection for Reading Order Engine (Stage 2.1).

RFC-008: ReadingOrderEngineFactory for instantiating protocol-compliant engines.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mechai.ordering.sorter import ReadingOrderEngine

if TYPE_CHECKING:
    from mechai.contracts.ordering import ReadingOrderEngineProtocol
    from mechai.ordering.config import ReadingOrderConfig


class ReadingOrderEngineFactory:
    """Factory for creating Reading Order Engine instances."""

    @staticmethod
    def create(config: ReadingOrderConfig | None = None) -> ReadingOrderEngineProtocol:
        """Instantiate a ReadingOrderEngine adhering to ReadingOrderEngineProtocol."""
        return ReadingOrderEngine(config=config)
