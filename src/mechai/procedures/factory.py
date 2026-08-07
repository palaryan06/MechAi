"""Automotive Procedure Engine Factory for dependency injection and instantiation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mechai.procedures.engine import AutomotiveProcedureEngine

if TYPE_CHECKING:
    from mechai.contracts.procedures import AutomotiveProcedureEngineProtocol
    from mechai.procedures.config import ProcedureEngineConfig


class AutomotiveProcedureEngineFactory:
    """Factory for creating and configuring Automotive Procedure Intelligence Engine instances."""

    @staticmethod
    def create(
        config: ProcedureEngineConfig | None = None,
    ) -> AutomotiveProcedureEngineProtocol:
        """Create an AutomotiveProcedureEngine instance satisfying AutomotiveProcedureEngineProtocol."""
        return AutomotiveProcedureEngine(config=config)
