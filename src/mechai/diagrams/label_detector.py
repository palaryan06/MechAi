"""Detector for text labels in automotive diagrams."""

from __future__ import annotations

from mechai.contracts.diagrams import DiagramLabel
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.diagrams.config import DiagramEngineConfig


class LabelDetector:
    """Detects text labels (e.g., 'Crankshaft', 'Intake') from regions within diagrams."""

    def __init__(self, config: DiagramEngineConfig | None = None) -> None:
        """Initialize the label detector."""
        self._config = config or DiagramEngineConfig()

    def detect_label(self, region: OrderedLayoutRegion) -> DiagramLabel | None:
        """Detect a label from a layout region.
        
        Labels are typically text regions inside a diagram that are NOT callouts.
        """
        text = region.text.strip()
        
        # Skip if it's purely a callout
        for pattern in self._config.callout_patterns:
            if pattern.match(text):
                return None
                
        # Skip if it's empty
        if not text:
            return None
            
        return DiagramLabel(
            label_id=f"label_{region.id}",
            text=text,
            bbox=region.bbox,
            provenance=SourceRef(
                page_number=region.page_number,
                extraction_method=ExtractionMethod.RULE,
                confidence=0.90,
                bbox=region.bbox,
            ),
        )
