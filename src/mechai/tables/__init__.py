"""Stage 6: Automotive Table Intelligence Engine (RFC-AUTO-001).

Deterministic spatial grid reconstruction, hierarchical header resolution, automotive unit normalization,
footnote binding, and multi-page continuation stitching for OEM service manuals.
"""

from __future__ import annotations

from mechai.tables.classifier import AutomotiveTableClassifier
from mechai.tables.config import TableEngineConfig
from mechai.tables.continuation import AutomotiveTableContinuationStitcher
from mechai.tables.engine import AutomotiveTableEngine
from mechai.tables.factory import AutomotiveTableEngineFactory
from mechai.tables.footnote_extractor import AutomotiveFootnoteExtractor
from mechai.tables.grid_reconstructor import SpatialGridReconstructor
from mechai.tables.unit_extractor import AutomotiveUnitExtractor

__all__ = [
    "AutomotiveFootnoteExtractor",
    "AutomotiveTableClassifier",
    "AutomotiveTableContinuationStitcher",
    "AutomotiveTableEngine",
    "AutomotiveTableEngineFactory",
    "AutomotiveUnitExtractor",
    "SpatialGridReconstructor",
    "TableEngineConfig",
]
