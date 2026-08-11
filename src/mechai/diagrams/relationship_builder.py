"""Builder for semantic relationships in automotive diagrams."""

from __future__ import annotations

import math
from typing import Sequence

from mechai.contracts.diagrams import (
    DiagramCallout,
    DiagramLabel,
    DiagramRelationship,
    DiagramRelationshipType,
    LeaderLine,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.diagrams.config import DiagramEngineConfig


class RelationshipBuilder:
    """Infers semantic relationships between diagram elements."""

    def __init__(self, config: DiagramEngineConfig | None = None) -> None:
        """Initialize the relationship builder."""
        self._config = config or DiagramEngineConfig()

    def build_relationships(
        self,
        callouts: Sequence[DiagramCallout],
        labels: Sequence[DiagramLabel],
        leader_lines: Sequence[LeaderLine],
        page_number: int,
    ) -> list[DiagramRelationship]:
        """Build relationships based on leader lines and spatial proximity."""
        relationships: list[DiagramRelationship] = []
        rel_idx = 1
        
        # 1. Use explicit leader lines if available
        # (Assuming leader line start_point is near callout/label and end_point is near component)
        # Since we don't extract visual components natively yet, we link callouts to labels if a line connects them,
        # or we just emit CALLOUT_POINTS_TO_COMPONENT pointing to a virtual coordinate region.
        
        # For this RFC, if a callout and label are adjacent, we relate them.
        for callout in callouts:
            closest_label: DiagramLabel | None = None
            min_dist = float("inf")
            
            for label in labels:
                dist = self._distance(callout.bbox, label.bbox)
                if dist < min_dist:
                    min_dist = dist
                    closest_label = label
                    
            if closest_label and min_dist <= self._config.proximity_threshold_pt:
                relationships.append(
                    DiagramRelationship(
                        relationship_id=f"rel_p{page_number}_{rel_idx:03d}",
                        relationship_type=DiagramRelationshipType.LABEL_DESCRIBES_COMPONENT,
                        source_id=callout.callout_id,
                        target_id=closest_label.label_id,
                        confidence=0.85,
                        evidence=f"Spatial proximity {min_dist:.1f}pt <= {self._config.proximity_threshold_pt}pt",
                        reasoning_rule="spatial_proximity_heuristic",
                        provenance=SourceRef(
                            page_number=page_number,
                            extraction_method=ExtractionMethod.HEURISTIC,
                            confidence=0.85,
                            bbox=callout.bbox,
                        ),
                    )
                )
                rel_idx += 1
                
        return relationships

    def _distance(self, box1: BoundingBox, box2: BoundingBox) -> float:
        """Calculate Euclidean distance between centers of two bounding boxes."""
        dx = box1.center_x - box2.center_x
        dy = box1.center_y - box2.center_y
        return math.sqrt(dx * dx + dy * dy)
