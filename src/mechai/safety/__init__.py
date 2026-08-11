"""Automotive Safety & Admonition Intelligence Engine (RFC-AUTO-004)."""

from mechai.safety.action_extractor import ActionExtractor
from mechai.safety.admonition_detector import AdmonitionDetector
from mechai.safety.condition_extractor import ConditionExtractor
from mechai.safety.config import SafetyEngineConfig
from mechai.safety.consequence_extractor import ConsequenceExtractor
from mechai.safety.continuation import AdmonitionContinuationStitcher
from mechai.safety.engine import AutomotiveSafetyEngine
from mechai.safety.factory import SafetyEngineFactory
from mechai.safety.hazard_extractor import HazardExtractor
from mechai.safety.relationship_builder import RelationshipBuilder
from mechai.safety.severity_classifier import SeverityClassifier
from mechai.safety.diagram_binder import DiagramBinder
from mechai.safety.procedure_binder import ProcedureBinder
from mechai.safety.table_binder import TableBinder


__all__ = [
    "ActionExtractor",
    "AdmonitionDetector",
    "ConditionExtractor",
    "SafetyEngineConfig",
    "ConsequenceExtractor",
    "AdmonitionContinuationStitcher",
    "AutomotiveSafetyEngine",
    "SafetyEngineFactory",
    "HazardExtractor",
    "RelationshipBuilder",
    "SeverityClassifier",
    "DiagramBinder",
    "ProcedureBinder",
    "TableBinder",
]
