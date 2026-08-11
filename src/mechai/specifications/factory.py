"""Factory for creating the Automotive Specification Intelligence Engine."""

from __future__ import annotations

from mechai.specifications.applicability import ApplicabilityResolver
from mechai.specifications.config import SpecificationConfig
from mechai.specifications.conflict_detector import ConflictDetector
from mechai.specifications.deduplication import FactDeduplicator
from mechai.specifications.engine import AutomotiveSpecificationEngine
from mechai.specifications.specification_extractor import SpecificationExtractor
from mechai.specifications.torque_extractor import TorqueExtractor


class SpecificationEngineFactory:
    """Factory for instantiating the Specification Engine with its dependencies."""

    @staticmethod
    def create_engine(config: SpecificationConfig | None = None) -> AutomotiveSpecificationEngine:
        """Create a fully configured Specification Engine."""
        cfg = config or SpecificationConfig()
        
        return AutomotiveSpecificationEngine(
            config=cfg,
            torque_extractor=TorqueExtractor(cfg),
            spec_extractor=SpecificationExtractor(cfg),
            applicability_resolver=ApplicabilityResolver(),
            conflict_detector=ConflictDetector(),
            deduplicator=FactDeduplicator(),
        )
