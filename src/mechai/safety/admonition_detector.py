"""Detector for safety admonition layout regions."""

from __future__ import annotations

from typing import Sequence

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.safety.config import SafetyEngineConfig


class AdmonitionDetector:
    """Detects safety admonition regions from layout structures."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the admonition detector."""
        self._config = config or SafetyEngineConfig()

    def detect_admonition_regions(self, page_regions: Sequence[OrderedLayoutRegion]) -> list[OrderedLayoutRegion]:
        """Detect layout regions containing safety admonitions."""
        admonition_regions: list[OrderedLayoutRegion] = []
        
        for region in page_regions:
            # 1. Explicit layout classification
            if region.region_type in (RegionType.WARNING_BOX, RegionType.NOTE_BOX):
                admonition_regions.append(region)
                continue
                
            # 2. Heuristic text-based detection (e.g., paragraph starting with "WARNING:")
            text = region.text.strip().upper()
            if not text:
                continue
                
            is_admonition = False
            for severity_keyword in self._config.severity_map:
                if text.startswith(f"{severity_keyword}:") or text.startswith(severity_keyword + "\n"):
                    is_admonition = True
                    break
                    
            if is_admonition:
                admonition_regions.append(region)
                
        return admonition_regions
