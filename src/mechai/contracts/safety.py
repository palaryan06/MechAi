"""Data contracts and stage protocols for Automotive Safety Intelligence Engine (Stage 8).

RFC-AUTO-004: Automotive Safety & Admonition Intelligence Engine.
All models are strictly typed, immutable (frozen=True), and fully validated.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.diagrams import AutomotiveDiagramSet
from mechai.contracts.ordering import OrderedLayoutCIR
from mechai.contracts.procedures import AutomotiveProcedureSet
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.contracts.tables import AutomotiveTableSet


class SafetySeverity(StrEnum):
    """Classification of the severity of a safety admonition."""

    DANGER = "DANGER"
    WARNING = "WARNING"
    CAUTION = "CAUTION"
    NOTICE = "NOTICE"
    NOTE = "NOTE"
    IMPORTANT = "IMPORTANT"
    OEM_SAFETY_STATEMENT = "OEM_SAFETY_STATEMENT"
    UNKNOWN_ADMONITION = "UNKNOWN_ADMONITION"


class HazardCategory(StrEnum):
    """Classification of the specific type of hazard."""

    HOT_SURFACE = "HOT_SURFACE"
    FIRE = "FIRE"
    EXPLOSION = "EXPLOSION"
    ELECTRICAL = "ELECTRICAL"
    HIGH_VOLTAGE = "HIGH_VOLTAGE"
    PRESSURE = "PRESSURE"
    CHEMICAL = "CHEMICAL"
    TOXIC_SUBSTANCE = "TOXIC_SUBSTANCE"
    ROTATING_COMPONENT = "ROTATING_COMPONENT"
    MOVING_COMPONENT = "MOVING_COMPONENT"
    CRUSHING = "CRUSHING"
    VEHICLE_MOVEMENT = "VEHICLE_MOVEMENT"
    JACKING_SUPPORT = "JACKING_SUPPORT"
    FUEL = "FUEL"
    COOLANT = "COOLANT"
    OIL = "OIL"
    BATTERY = "BATTERY"
    AIRBAG = "AIRBAG"
    BRAKE_SYSTEM = "BRAKE_SYSTEM"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"
    UNCERTAIN = "UNCERTAIN"  # Used when inference is not safely supported


class SafetyCondition(BaseModel):
    """The situational condition that creates the risk."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    condition_id: str = Field(min_length=1)
    text: str = Field(description="Extracted condition text (e.g., 'When engine is hot')")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    provenance: SourceRef


class SafetyConsequence(BaseModel):
    """The potential consequence if the admonition is ignored."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    consequence_id: str = Field(min_length=1)
    text: str = Field(description="Extracted consequence text (e.g., 'May result in severe burns')")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    provenance: SourceRef


class SafetyAction(BaseModel):
    """The required action to mitigate the hazard."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    action_id: str = Field(min_length=1)
    text: str = Field(description="Extracted action text (e.g., 'Allow engine to cool')")
    is_restriction: bool = Field(default=False, description="True if this is a prohibited action ('Do NOT')")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    provenance: SourceRef


class SafetyRequirement(BaseModel):
    """Required PPE or explicit safety equipment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    requirement_id: str = Field(min_length=1)
    equipment: str = Field(description="Equipment name (e.g., 'Safety Glasses')")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    provenance: SourceRef


class SafetyAdmonition(BaseModel):
    """A discrete structured safety warning unit."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    admonition_id: str = Field(min_length=1)
    severity: SafetySeverity
    original_label: str = Field(description="Original displayed label (e.g., 'WARNING', 'CAUTION')")
    raw_text: str = Field(description="The complete textual content of the admonition")
    
    hazard_category: HazardCategory = Field(default=HazardCategory.UNKNOWN)
    conditions: tuple[SafetyCondition, ...] = Field(default_factory=tuple)
    consequences: tuple[SafetyConsequence, ...] = Field(default_factory=tuple)
    actions: tuple[SafetyAction, ...] = Field(default_factory=tuple)
    requirements: tuple[SafetyRequirement, ...] = Field(default_factory=tuple)

    page_span: tuple[int, int]
    bbox: BoundingBox
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    provenance: SourceRef
    region_ids: tuple[str, ...] = Field(default_factory=tuple)


class SafetyRelationshipType(StrEnum):
    """Semantic relationships between admonitions and other document structures."""

    ADMONITION_APPLIES_TO_PROCEDURE = "ADMONITION_APPLIES_TO_PROCEDURE"
    ADMONITION_APPLIES_TO_STEP = "ADMONITION_APPLIES_TO_STEP"
    ADMONITION_REFERENCES_COMPONENT = "ADMONITION_REFERENCES_COMPONENT"
    ADMONITION_REFERENCES_DIAGRAM = "ADMONITION_REFERENCES_DIAGRAM"
    ADMONITION_REFERENCES_TABLE = "ADMONITION_REFERENCES_TABLE"


class SafetyRelationship(BaseModel):
    """A binding between a safety admonition and another artifact."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    relationship_id: str = Field(min_length=1)
    relationship_type: SafetyRelationshipType
    admonition_id: str
    target_id: str = Field(description="ID of the target procedure, step, diagram, or table")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence: str = Field(description="Evidence for the binding (e.g., 'Spatial proximity to Procedure 1')")
    provenance: SourceRef


class AutomotiveSafetySet(BaseModel):
    """Document-level container for all structured safety information."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str
    admonitions: tuple[SafetyAdmonition, ...] = Field(default_factory=tuple)
    relationships: tuple[SafetyRelationship, ...] = Field(default_factory=tuple)
    total_admonitions: int = Field(ge=0)

    @classmethod
    def from_collections(
        cls,
        document_id: str,
        admonitions: list[SafetyAdmonition] | tuple[SafetyAdmonition, ...],
        relationships: list[SafetyRelationship] | tuple[SafetyRelationship, ...],
    ) -> AutomotiveSafetySet:
        """Create a safety set from collections."""
        ad_tuple = tuple(admonitions)
        rel_tuple = tuple(relationships)
        return cls(
            document_id=document_id,
            admonitions=ad_tuple,
            relationships=rel_tuple,
            total_admonitions=len(ad_tuple),
        )


@runtime_checkable
class AutomotiveSafetyEngineProtocol(Protocol):
    """Protocol for the Automotive Safety Intelligence Engine (Stage 8)."""

    def reconstruct_safety(
        self,
        ordered_cir: OrderedLayoutCIR,
        procedure_set: AutomotiveProcedureSet | None = None,
        table_set: AutomotiveTableSet | None = None,
        diagram_set: AutomotiveDiagramSet | None = None,
    ) -> AutomotiveSafetySet:
        """Process an entire document to extract and bind structured safety information."""
        ...
