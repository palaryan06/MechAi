"""Detector for callouts in automotive diagrams."""

from __future__ import annotations

from mechai.contracts.diagrams import DiagramCallout
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.diagrams.config import DiagramEngineConfig


class CalloutDetector:
    """Detects callouts (e.g., '1', 'A', '[1]') from regions within diagrams."""

    def __init__(self, config: DiagramEngineConfig | None = None) -> None:
        """Initialize the callout detector."""
        self._config = config or DiagramEngineConfig()

    def detect_callouts(self, region: OrderedLayoutRegion) -> list[DiagramCallout]:
        """Detect callouts from a layout region.
        
        Typically, callouts in diagrams are isolated text regions.
        """
        callouts: list[DiagramCallout] = []
        text = region.text.strip()
        
        # Check against all callout patterns
        for pattern in self._config.callout_patterns:
            match = pattern.match(text)
            if match:
                callouts.append(
                    DiagramCallout(
                        callout_id=f"callout_{region.id}",
                        text=text,
                        bbox=region.bbox,
                        provenance=SourceRef(
                            page_number=region.page_number,
                            extraction_method=ExtractionMethod.RULE,
                            confidence=0.95,
                            bbox=region.bbox,
                        ),
                    )
                )
                # Once matched, no need to check other patterns for this isolated region
                break
                
        return callouts
