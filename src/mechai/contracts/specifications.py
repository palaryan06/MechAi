"""Canonical Domain Fact Contracts for Automotive Specifications and Torques."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.provenance import SourceRef  # noqa: TC001
from mechai.domain.enums import FastenerCondition, TorqueUnit


class SpecificationType(StrEnum):
    """Classification of the canonical engineering fact."""

    TORQUE = "torque"
    CLEARANCE = "clearance"
    DIMENSION = "dimension"
    CAPACITY = "capacity"
    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    VOLTAGE = "voltage"
    RESISTANCE = "resistance"
    SPEED = "speed"
    ANGLE = "angle"
    WEIGHT = "weight"
    RATIO = "ratio"
    OTHER = "other"


class ConflictCategory(StrEnum):
    """Category of detected conflict between two canonical facts."""

    VALUE_CONFLICT = "value_conflict"
    UNIT_CONFLICT = "unit_conflict"
    APPLICABILITY_CONFLICT = "applicability_conflict"
    CONDITION_CONFLICT = "condition_conflict"
    REVISION_CONFLICT = "revision_conflict"
    TARGET_IDENTITY_CONFLICT = "target_identity_conflict"


class ApplicabilityContext(BaseModel):
    """Context under which a fact is known to be valid and applicable.
    
    If an attribute is None, it means the constraint is unspecified or universal 
    within the manual's scope.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    manufacturer: str | None = None
    model: str | None = None
    model_year: str | None = None
    engine_code: str | None = None
    transmission: str | None = None
    drivetrain: str | None = None
    fuel_type: str | None = None
    market: str | None = None
    variant: str | None = None
    system: str | None = None
    component: str | None = None
    operating_condition: str | None = None
    prerequisite_condition: str | None = None


class SpecificationValue(BaseModel):
    """Dual-representation container for numeric specifications."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw_value: str = Field(min_length=1)
    numeric_value: float | None = None
    original_unit: str | None = None
    canonical_value: float | None = None
    canonical_unit: str | None = None
    tolerance_min: float | None = None
    tolerance_max: float | None = None


class BaseCanonicalFact(BaseModel):
    """Base class for all canonical domain facts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    fact_type: SpecificationType
    applicability: ApplicabilityContext = Field(default_factory=ApplicabilityContext)
    evidence: tuple[SourceRef, ...] = Field(default_factory=tuple)


class AutomotiveTorqueFact(BaseCanonicalFact):
    """Canonical representation of an engineering torque specification."""

    fact_type: SpecificationType = SpecificationType.TORQUE
    target_component: str | None = None
    fastener_description: str | None = None
    fastener_size: str | None = None
    value: SpecificationValue
    tightening_angle_degrees: float | None = None
    tightening_sequence: str | None = None
    fastener_condition: FastenerCondition = FastenerCondition.DRY
    reuse_condition: str | None = None


class AutomotiveSpecificationFact(BaseCanonicalFact):
    """Canonical representation of general specifications (clearances, capacities)."""

    target_component: str | None = None
    value: SpecificationValue
    measurement_condition: str | None = None


class ConflictEdge(BaseModel):
    """Represents an unresolved contradiction between two extracted facts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    fact_a_id: str
    fact_b_id: str
    category: ConflictCategory
    reason: str


class AutomotiveSpecificationSet(BaseModel):
    """Top-level container for all canonical specifications in a document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    torques: tuple[AutomotiveTorqueFact, ...] = Field(default_factory=tuple)
    specifications: tuple[AutomotiveSpecificationFact, ...] = Field(default_factory=tuple)
    conflicts: tuple[ConflictEdge, ...] = Field(default_factory=tuple)

    @property
    def total_facts(self) -> int:
        """Total number of canonical facts."""
        return len(self.torques) + len(self.specifications)

    @property
    def total_conflicts(self) -> int:
        """Total number of conflicts detected."""
        return len(self.conflicts)
