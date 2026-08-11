"""Golden tests for diagram data contracts."""

import pytest
from pydantic import ValidationError

from mechai.contracts.diagrams import (
    AutomotiveDiagram,
    AutomotiveDiagramType,
    DiagramCallout,
    DiagramFigure,
    DiagramLabel,
    DiagramRelationship,
    DiagramRelationshipType,
    LeaderLine,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef


class TestDiagramGoldenContracts:
    """Validate strict immutability and schema enforcement on diagram contracts."""

    def test_immutability_enforcement(self) -> None:
        """Test that data contracts are strictly immutable (frozen=True)."""
        callout = DiagramCallout(
            callout_id="c1",
            text="1",
            bbox=BoundingBox(left=10, top=10, right=20, bottom=20),
            provenance=SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE, confidence=1.0),
        )

        with pytest.raises(ValidationError, match="Instance is frozen"):
            callout.text = "2"  # type: ignore

    def test_json_serialization_roundtrip(self) -> None:
        """Test that diagrams can be serialized and deserialized accurately."""
        diag = AutomotiveDiagram(
            diagram_id="diag_1",
            diagram_type=AutomotiveDiagramType.EXPLODED_VIEW,
            figure=DiagramFigure(
                figure_id="fig_1",
                title="Fig. 1 Exploded View",
                identifier="Fig. 1",
                bbox=BoundingBox(left=10, top=10, right=200, bottom=30),
                provenance=SourceRef(page_number=1),
            ),
            callouts=tuple([
                DiagramCallout(
                    callout_id="c1",
                    text="1",
                    bbox=BoundingBox(left=50, top=50, right=60, bottom=60),
                    provenance=SourceRef(page_number=1),
                )
            ]),
            labels=tuple([
                DiagramLabel(
                    label_id="l1",
                    text="Bolt",
                    bbox=BoundingBox(left=70, top=50, right=100, bottom=60),
                    provenance=SourceRef(page_number=1),
                )
            ]),
            relationships=tuple([
                DiagramRelationship(
                    relationship_id="r1",
                    relationship_type=DiagramRelationshipType.LABEL_DESCRIBES_COMPONENT,
                    source_id="c1",
                    target_id="l1",
                    confidence=0.9,
                    evidence="Proximity",
                    reasoning_rule="spatial",
                    provenance=SourceRef(page_number=1),
                )
            ]),
            linked_procedure_ids=tuple(["proc_1"]),
            linked_table_ids=tuple(["table_1"]),
            page_span=(1, 1),
            bbox=BoundingBox(left=10, top=10, right=200, bottom=200),
            provenance=SourceRef(page_number=1),
        )

        json_data = diag.model_dump_json()
        restored = AutomotiveDiagram.model_validate_json(json_data)

        assert restored == diag
        assert restored.diagram_type == AutomotiveDiagramType.EXPLODED_VIEW
        assert len(restored.callouts) == 1
        assert len(restored.linked_procedure_ids) == 1
