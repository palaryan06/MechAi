"""Detector for identifying and grouping diagram regions."""

from __future__ import annotations

from typing import Sequence

from mechai.contracts.diagrams import DiagramFigure
from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.diagrams.config import DiagramEngineConfig


class DiagramDetector:
    """Detects and groups layout regions into discrete diagrams."""

    def __init__(self, config: DiagramEngineConfig | None = None) -> None:
        """Initialize the diagram detector."""
        self._config = config or DiagramEngineConfig()

    def detect_diagrams(self, page_regions: Sequence[OrderedLayoutRegion]) -> list[dict]:
        """Group regions into diagrams.
        
        Returns a list of dicts, each containing:
        - 'figure_region': the main FIGURE_REGION
        - 'caption_region': the associated CAPTION (if any)
        - 'content_regions': text regions (labels, callouts) overlapping or inside the figure
        """
        diagrams: list[dict] = []
        figure_regions = [r for r in page_regions if r.region_type == RegionType.FIGURE_REGION]
        
        for fig_reg in figure_regions:
            caption: OrderedLayoutRegion | None = None
            content_regions: list[OrderedLayoutRegion] = []
            
            # Find associated caption (typically just below or above the figure)
            for r in page_regions:
                if r.region_type == RegionType.CAPTION:
                    # Simple vertical proximity check for caption
                    if self._is_vertically_adjacent(fig_reg.bbox, r.bbox):
                        caption = r
                        break
            
            # Find overlapping or fully contained text regions for callouts/labels
            for r in page_regions:
                if r.id == fig_reg.id:
                    continue
                if r.region_type in (RegionType.CAPTION, RegionType.HEADER, RegionType.FOOTER, RegionType.MARGIN):
                    continue
                
                if self._overlaps(fig_reg.bbox, r.bbox):
                    content_regions.append(r)
                    
            diagrams.append({
                "figure_region": fig_reg,
                "caption_region": caption,
                "content_regions": content_regions,
            })
            
        return diagrams

    def _is_vertically_adjacent(self, box1: BoundingBox, box2: BoundingBox) -> bool:
        """Check if box2 is vertically adjacent to box1."""
        vertical_dist = min(abs(box1.bottom - box2.top), abs(box2.bottom - box1.top))
        # Also check horizontal overlap to ensure they belong together
        horiz_overlap = not (box1.right < box2.left or box1.left > box2.right)
        return vertical_dist <= self._config.proximity_threshold_pt * 2 and horiz_overlap

    def _overlaps(self, box1: BoundingBox, box2: BoundingBox) -> bool:
        """Check if box2 overlaps with box1."""
        return not (
            box2.right < box1.left or
            box2.left > box1.right or
            box2.bottom < box1.top or
            box2.top > box1.bottom
        )

    def extract_figure(self, caption_region: OrderedLayoutRegion | None) -> DiagramFigure | None:
        """Extract a DiagramFigure from a caption region."""
        if not caption_region:
            return None
            
        text = caption_region.text.strip()
        identifier = None
        
        for pat in self._config.figure_prefix_patterns:
            match = pat.match(text)
            if match:
                identifier = match.group(0).strip()
                break
                
        return DiagramFigure(
            figure_id=f"fig_{caption_region.id}",
            title=text,
            identifier=identifier,
            bbox=caption_region.bbox,
            provenance=SourceRef(
                page_number=caption_region.page_number,
                extraction_method=ExtractionMethod.RULE,
                confidence=0.98,
                bbox=caption_region.bbox,
            ),
        )
