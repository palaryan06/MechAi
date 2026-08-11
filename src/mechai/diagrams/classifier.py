"""Classifier for automotive diagram types."""

from __future__ import annotations

from mechai.contracts.diagrams import AutomotiveDiagramType, DiagramCallout, DiagramFigure, DiagramLabel
from mechai.diagrams.config import DiagramEngineConfig


class DiagramClassifier:
    """Classifies diagram regions into specific automotive diagram types."""

    def __init__(self, config: DiagramEngineConfig | None = None) -> None:
        """Initialize the classifier."""
        self._config = config or DiagramEngineConfig()

    def classify(
        self,
        figure: DiagramFigure | None,
        labels: tuple[DiagramLabel, ...],
        callouts: tuple[DiagramCallout, ...],
    ) -> AutomotiveDiagramType:
        """Deterministically classify the diagram based on textual and structural evidence."""
        # Check figure title first
        if figure and figure.title:
            title_lower = figure.title.lower()
            if "exploded" in title_lower:
                return AutomotiveDiagramType.EXPLODED_VIEW
            if "cross section" in title_lower or "cross-section" in title_lower:
                return AutomotiveDiagramType.CROSS_SECTION
            if "wiring" in title_lower or "wire harness" in title_lower:
                return AutomotiveDiagramType.WIRING_DIAGRAM
            if "connector" in title_lower or "terminal" in title_lower:
                return AutomotiveDiagramType.CONNECTOR_DIAGRAM
            if "circuit" in title_lower:
                return AutomotiveDiagramType.CIRCUIT_DIAGRAM
            if "schematic" in title_lower:
                return AutomotiveDiagramType.SCHEMATIC
            if "flowchart" in title_lower or "troubleshooting" in title_lower:
                return AutomotiveDiagramType.FLOWCHART
            if "location" in title_lower or "routing" in title_lower:
                return AutomotiveDiagramType.LOCATION_DIAGRAM
            if "adjustment" in title_lower or "clearance" in title_lower:
                return AutomotiveDiagramType.ADJUSTMENT_DIAGRAM
            if "inspection" in title_lower or "check" in title_lower:
                return AutomotiveDiagramType.INSPECTION_DIAGRAM
            if "identification" in title_lower or "vin" in title_lower:
                return AutomotiveDiagramType.IDENTIFICATION_DIAGRAM
            if "assembly" in title_lower or "installation" in title_lower:
                return AutomotiveDiagramType.ASSEMBLY_DIAGRAM
            if "component" in title_lower or "parts" in title_lower:
                return AutomotiveDiagramType.COMPONENT_DIAGRAM

        # Check labels for wiring / connector clues
        wiring_score = 0
        for label in labels:
            text_lower = label.text.lower()
            if any(kw in text_lower for kw in self._config.connector_keywords):
                wiring_score += 1
            if any(kw in text_lower for kw in self._config.circuit_keywords):
                wiring_score += 1
                
        if wiring_score >= 2:
            return AutomotiveDiagramType.WIRING_DIAGRAM

        # Exploded view heuristic: Many callouts pointing to components without a specific wiring/circuit context
        if len(callouts) >= 3:
            return AutomotiveDiagramType.EXPLODED_VIEW

        return AutomotiveDiagramType.UNKNOWN_TECHNICAL_DIAGRAM
