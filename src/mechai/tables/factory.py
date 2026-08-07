"""Factory for creating Automotive Table Intelligence Engine instances (RFC-AUTO-001)."""

from __future__ import annotations

from mechai.contracts.tables import AutomotiveTableEngineProtocol
from mechai.tables.config import TableEngineConfig
from mechai.tables.engine import AutomotiveTableEngine


class AutomotiveTableEngineFactory:
    """Factory for instantiating AutomotiveTableEngine instances."""

    @staticmethod
    def create(config: TableEngineConfig | None = None) -> AutomotiveTableEngineProtocol:
        """Create an instance of AutomotiveTableEngine conforming to AutomotiveTableEngineProtocol."""
        return AutomotiveTableEngine(config=config)
