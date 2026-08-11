"""Factory for Automotive Safety Intelligence Engine."""

from __future__ import annotations

from mechai.safety.action_extractor import ActionExtractor
from mechai.safety.admonition_detector import AdmonitionDetector
from mechai.safety.condition_extractor import ConditionExtractor
from mechai.safety.config import SafetyEngineConfig
from mechai.safety.consequence_extractor import ConsequenceExtractor
from mechai.safety.continuation import AdmonitionContinuationStitcher
from mechai.safety.engine import AutomotiveSafetyEngine
from mechai.safety.hazard_extractor import HazardExtractor
from mechai.safety.relationship_builder import RelationshipBuilder
from mechai.safety.severity_classifier import SeverityClassifier


class SafetyEngineFactory:
    """Factory for creating configured AutomotiveSafetyEngine instances."""

    @staticmethod
    def create_engine(config: SafetyEngineConfig | None = None) -> AutomotiveSafetyEngine:
        """Create a fully configured AutomotiveSafetyEngine.
        
        Args:
            config: Optional configuration overrides.
            
        Returns:
            Configured AutomotiveSafetyEngine instance.
        """
        config = config or SafetyEngineConfig()
        
        admonition_detector = AdmonitionDetector(config)
        severity_classifier = SeverityClassifier(config)
        hazard_extractor = HazardExtractor(config)
        condition_extractor = ConditionExtractor(config)
        consequence_extractor = ConsequenceExtractor(config)
        action_extractor = ActionExtractor(config)
        continuation_stitcher = AdmonitionContinuationStitcher()
        relationship_builder = RelationshipBuilder(config)
        
        return AutomotiveSafetyEngine(
            config=config,
            admonition_detector=admonition_detector,
            severity_classifier=severity_classifier,
            hazard_extractor=hazard_extractor,
            condition_extractor=condition_extractor,
            consequence_extractor=consequence_extractor,
            action_extractor=action_extractor,
            continuation_stitcher=continuation_stitcher,
            relationship_builder=relationship_builder,
        )
