"""Automotive Specification Intelligence Engine.

This module implements the deterministic extraction, normalization, and deduplication
of engineering specifications (torque, clearances, etc.) from parsed document structures.
"""

from mechai.specifications.engine import AutomotiveSpecificationEngine
from mechai.specifications.factory import SpecificationEngineFactory
from mechai.specifications.config import SpecificationConfig

__all__ = [
    "AutomotiveSpecificationEngine",
    "SpecificationEngineFactory",
    "SpecificationConfig",
]
