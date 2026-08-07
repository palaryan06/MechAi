"""Automotive Procedure Intelligence Engine module (RFC-AUTO-002).

Reconstructs structured OEM automotive repair procedures from OrderedLayoutCIR and AutomotiveTableSet.
"""

from __future__ import annotations

from mechai.procedures.admonition_binder import AdmonitionBinder
from mechai.procedures.boundary_detector import BoundaryDetector
from mechai.procedures.config import ProcedureEngineConfig
from mechai.procedures.continuation import ProcedureContinuationStitcher
from mechai.procedures.cross_ref_resolver import CrossReferenceResolver
from mechai.procedures.engine import AutomotiveProcedureEngine
from mechai.procedures.factory import AutomotiveProcedureEngineFactory
from mechai.procedures.requirement_extractor import RequirementExtractor
from mechai.procedures.step_parser import StepParser

__all__ = [
    "AdmonitionBinder",
    "AutomotiveProcedureEngine",
    "AutomotiveProcedureEngineFactory",
    "BoundaryDetector",
    "CrossReferenceResolver",
    "ProcedureContinuationStitcher",
    "ProcedureEngineConfig",
    "RequirementExtractor",
    "StepParser",
]
