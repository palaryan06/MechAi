"""Data contracts and stage protocols for Automotive Diagram Intelligence Engine (Stage 7).

RFC-AUTO-003: Automotive Diagram Intelligence Engine.
All models are strictly typed, immutable (frozen=True), and fully validated.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.ordering import OrderedLayoutCIR
from mechai.contracts.procedures import AutomotiveProcedureSet
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.contracts.tables import AutomotiveTableSet


class AutomotiveDiagramType(StrEnum):
    """Classified semantic types for automotive technical diagrams."""

    EXPLODED_VIEW = "EXPLODED_VIEW"
    ASSEMBLY_DIAGRAM = "ASSEMBLY_DIAGRAM"
    COMPONENT_DIAGRAM = "COMPONENT_DIAGRAM"
    CONNECTOR_DIAGRAM = "CONNECTOR_DIAGRAM"
    WIRING_DIAGRAM = "WIRING_DIAGRAM"
    CIRCUIT_DIAGRAM = "CIRCUIT_DIAGRAM"
    SCHEMATIC = "SCHEMATIC"
    FLOWCHART = "FLOWCHART"
    INSPECTION_DIAGRAM = "INSPECTION_DIAGRAM"
    CROSS_SECTION = "CROSS_SECTION"
    LOCATION_DIAGRAM = "LOCATION_DIAGRAM"
    ADJUSTMENT_DIAGRAM = "ADJUSTMENT_DIAGRAM"
    IDENTIFICATION_DIAGRAM = "IDENTIFICATION_DIAGRAM"
    UNKNOWN_TECHNICAL_DIAGRAM = "UNKNOWN_TECHNICAL_DIAGRAM"


class DiagramCallout(BaseModel):
    """A visual reference marker indicating a part or note (e.g., '1', 'A', '[1]')."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    callout_id: str = Field(min_length=1)
    text: str = Field(description="The parsed textual representation of the callout")
    bbox: BoundingBox
    provenance: SourceRef


class DiagramLabel(BaseModel):
    """A textual label found inside or adjacent to a diagram component."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    label_id: str = Field(min_length=1)
    text: str
    bbox: BoundingBox
    provenance: SourceRef


class LeaderLine(BaseModel):
    """A line visually connecting a callout or label to a specific component."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    line_id: str = Field(min_length=1)
    start_point: tuple[float, float] = Field(description="Origin coordinate (x, y)")
    end_point: tuple[float, float] = Field(description="Destination coordinate (x, y)")
    is_inferred: bool = Field(description="True if inferred via proximity, False if deterministic vector")
    provenance: SourceRef


class DiagramRelationshipType(StrEnum):
    """Classified semantic relationships between diagram elements."""

    CALLOUT_POINTS_TO_COMPONENT = "CALLOUT_POINTS_TO_COMPONENT"
    COMPONENT_BELONGS_TO_ASSEMBLY = "COMPONENT_BELONGS_TO_ASSEMBLY"
    COMPONENT_ADJACENT_TO = "COMPONENT_ADJACENT_TO"
    COMPONENT_ALIGNED_WITH = "COMPONENT_ALIGNED_WITH"
    COMPONENT_REFERENCED_BY_PROCEDURE = "COMPONENT_REFERENCED_BY_PROCEDURE"
    LABEL_DESCRIBES_COMPONENT = "LABEL_DESCRIBES_COMPONENT"


class DiagramRelationship(BaseModel):
    """An inferred semantic relationship between elements in a diagram.

    Preserves strict separation between visual evidence and inferred semantics.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    relationship_id: str = Field(min_length=1)
    relationship_type: DiagramRelationshipType
    source_id: str = Field(description="ID of the origin element (e.g., callout_id)")
    target_id: str = Field(description="ID of the target element (e.g., label_id, or implied region)")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence: str = Field(description="Description of visual evidence (e.g., 'spatial proximity < 5pt')")
    reasoning_rule: str = Field(description="Name of the heuristic or rule used for inference")
    provenance: SourceRef


class DiagramFigure(BaseModel):
    """The identifying figure caption and title for a diagram."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    figure_id: str = Field(min_length=1)
    title: str = Field(description="Full caption/title (e.g., 'Fig. 1 Exploded View of Cylinder Head')")
    identifier: str | None = Field(description="Parsed identifier (e.g., 'Fig. 1')")
    bbox: BoundingBox
    provenance: SourceRef


class AutomotiveDiagram(BaseModel):
    """Structured evidence-based representation of an automotive technical diagram."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    diagram_id: str = Field(min_length=1)
    diagram_type: AutomotiveDiagramType
    figure: DiagramFigure | None = Field(default=None)
    callouts: tuple[DiagramCallout, ...] = Field(default_factory=tuple)
    labels: tuple[DiagramLabel, ...] = Field(default_factory=tuple)
    leader_lines: tuple[LeaderLine, ...] = Field(default_factory=tuple)
    relationships: tuple[DiagramRelationship, ...] = Field(default_factory=tuple)

    linked_procedure_ids: tuple[str, ...] = Field(
        default_factory=tuple,
        description="IDs of procedures explicitly referencing this diagram",
    )
    linked_table_ids: tuple[str, ...] = Field(
        default_factory=tuple,
        description="IDs of tables explicitly referenced by this diagram",
    )

    page_span: tuple[int, int]
    bbox: BoundingBox
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    provenance: SourceRef
    region_ids: tuple[str, ...] = Field(default_factory=tuple)


class AutomotiveDiagramSet(BaseModel):
    """Document-level container for all structured automotive diagrams."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str
    diagrams: tuple[AutomotiveDiagram, ...] = Field(default_factory=tuple)
    total_diagrams: int = Field(ge=0)

    @classmethod
    def from_diagrams(
        cls,
        document_id: str,
        diagrams: list[AutomotiveDiagram] | tuple[AutomotiveDiagram, ...],
    ) -> AutomotiveDiagramSet:
        """Create a diagram set from a collection of diagrams."""
        diag_tuple = tuple(diagrams)
        return cls(
            document_id=document_id,
            diagrams=diag_tuple,
            total_diagrams=len(diag_tuple),
        )


@runtime_checkable
class AutomotiveDiagramEngineProtocol(Protocol):
    """Protocol for the Automotive Diagram Intelligence Engine (Stage 7)."""

    def reconstruct_diagrams(
        self,
        ordered_cir: OrderedLayoutCIR,
        table_set: AutomotiveTableSet | None = None,
        procedure_set: AutomotiveProcedureSet | None = None,
    ) -> AutomotiveDiagramSet:
        """Process an entire document to reconstruct structured automotive diagrams.

        Args:
            ordered_cir: The reading-order sorted layout representation.
            table_set: Optional extracted tables for cross-linking.
            procedure_set: Optional extracted procedures for cross-linking.

        Returns:
            A strictly typed, provenance-preserving set of AutomotiveDiagrams.
        """
        ...
