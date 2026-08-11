"""Factory for diagram intelligence components."""

from __future__ import annotations

from mechai.contracts.diagrams import AutomotiveDiagramEngineProtocol
from mechai.diagrams.config import DiagramEngineConfig
from mechai.diagrams.engine import AutomotiveDiagramEngine


class DiagramEngineFactory:
    """Factory for instantiating the Automotive Diagram Intelligence Engine."""

    @classmethod
    def create_engine(
        cls, config: DiagramEngineConfig | None = None
    ) -> AutomotiveDiagramEngineProtocol:
        """Create a fully configured diagram intelligence engine."""
        return AutomotiveDiagramEngine(config=config)
