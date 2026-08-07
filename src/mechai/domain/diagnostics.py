"""DiagnosticCode (DTC), Symptom, Inspection, and Repair domain entities."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import Field, field_validator

from mechai.domain.base import DomainModel, DomainProvenance
from mechai.domain.enums import (
    DifficultyLevel,
    DtcCategory,
    InspectionOutcome,
    SymptomCategory,
)

# Standard OBD-II DTC format: P0123, C0035, B1234, U0100
_OBD2_REGEX = re.compile(r"^[PCBUpcbu][0-9A-Fa-f]{4}$")


class DiagnosticCode(DomainModel):
    """OBD-II or OEM Diagnostic Trouble Code (DTC).

    Attributes:
        code_id: Unique domain identifier (e.g., 'dtc_p0301').
        code: The alphanumeric DTC string (e.g., 'P0301', 'C0035').
        category: System category (Powertrain, Chassis, Body, Network).
        description: Standard SAE/OEM trouble code definition.
        technical_meaning: In-depth engineering description of the fault condition.
        mil_illuminated: Whether this fault illuminates the Malfunction Indicator Lamp.
        system_id: Associated vehicle system identifier.
        affected_component_ids: Components implicated by this trouble code.
        possible_causes: Verified mechanical or electrical root causes.
        associated_symptoms: Observable customer symptoms caused by this fault.
        is_generic_obd2: True if standard SAE code; False if manufacturer-specific.
        provenance: Grounding provenance.
    """

    code_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    category: DtcCategory = DtcCategory.POWERTRAIN_P
    description: str = Field(min_length=1)
    technical_meaning: str | None = None
    mil_illuminated: bool = True
    system_id: str | None = None
    affected_component_ids: tuple[str, ...] = Field(default_factory=tuple)
    possible_causes: tuple[str, ...] = Field(default_factory=tuple)
    associated_symptoms: tuple[str, ...] = Field(default_factory=tuple)
    is_generic_obd2: bool = True
    provenance: DomainProvenance | None = None

    @field_validator("code")
    @classmethod
    def normalize_and_validate_code(cls, v: str) -> str:
        """Normalize code to uppercase and validate non-empty string."""
        normalized = v.strip().upper()
        if not normalized:
            raise ValueError("DTC code cannot be empty")
        return normalized


class Symptom(DomainModel):
    """Observable physical defect, noise, performance degradation, or warning.

    Attributes:
        symptom_id: Unique domain identifier (e.g., 'sym_misfire_under_load').
        description: Clear description of the observed defect or complaint.
        category: Symptom classification.
        system_id: Associated vehicle system.
        trigger_conditions: Operational conditions when the symptom manifests.
        probable_causes: Hypothesized physical causes explaining the symptom.
        associated_dtcs: Diagnostic trouble codes that commonly accompany this symptom.
        suspected_components: Components suspected of causing this symptom.
        provenance: Grounding provenance.
    """

    symptom_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: SymptomCategory = SymptomCategory.DRIVEABILITY
    system_id: str | None = None
    trigger_conditions: tuple[str, ...] = Field(default_factory=tuple)
    probable_causes: tuple[str, ...] = Field(default_factory=tuple)
    associated_dtcs: tuple[str, ...] = Field(default_factory=tuple)
    suspected_components: tuple[str, ...] = Field(default_factory=tuple)
    provenance: DomainProvenance | None = None


class Inspection(DomainModel):
    """Diagnostic test, physical measurement, or functional inspection checklist item.

    Attributes:
        inspection_id: Unique domain identifier (e.g., 'insp_rotor_thickness').
        point_name: Name of the inspection checkpoint (e.g., 'Brake Disc Thickness').
        description: Detailed instruction on how to perform the test.
        system_id: Associated vehicle system identifier.
        component_id: Associated component identifier.
        tool_required: Tool or instrument used for the measurement.
        nominal_spec: Standard baseline specification text.
        min_tolerance: Minimum allowable value.
        max_tolerance: Maximum allowable value.
        tolerance_unit: Measurement unit (e.g., 'mm', 'V', 'psi', 'ohms').
        outcome: Result outcome of the inspection.
        observed_value: Measured numeric value.
        provenance: Grounding provenance.
    """

    inspection_id: str = Field(min_length=1)
    point_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    system_id: str | None = None
    component_id: str | None = None
    tool_required: str | None = None
    nominal_spec: str | None = None
    min_tolerance: float | None = None
    max_tolerance: float | None = None
    tolerance_unit: str | None = None
    outcome: InspectionOutcome = InspectionOutcome.NOT_TESTED
    observed_value: float | None = None
    provenance: DomainProvenance | None = None

    @field_validator("max_tolerance")
    @classmethod
    def validate_tolerance_limits(cls, v: float | None, info: object) -> float | None:
        """Ensure max_tolerance is greater than or equal to min_tolerance."""
        if v is not None and hasattr(info, "data") and "min_tolerance" in info.data:
            min_tol = info.data["min_tolerance"]
            if min_tol is not None and v < min_tol:
                msg = f"max_tolerance ({v}) cannot be less than min_tolerance ({min_tol})"
                raise ValueError(msg)
        return v


class Repair(DomainModel):
    """Corrective service operation resolving diagnostic trouble codes and symptoms.

    Attributes:
        repair_id: Unique domain identifier (e.g., 'rep_replace_spark_plugs').
        title: Clear title of the repair operation.
        description: Detailed overview of corrective actions.
        target_dtcs: Diagnostic trouble codes addressed by this repair.
        target_symptoms: Symptoms resolved by this repair.
        component_ids: Components repaired, replaced, or adjusted.
        procedure_ids: Ordered sequence of procedure IDs implementing this repair.
        estimated_labor_hours: Estimated flat-rate labor time in hours.
        difficulty: Technical skill difficulty level.
        provenance: Grounding provenance.
    """

    repair_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    target_dtcs: tuple[str, ...] = Field(default_factory=tuple)
    target_symptoms: tuple[str, ...] = Field(default_factory=tuple)
    component_ids: tuple[str, ...] = Field(default_factory=tuple)
    procedure_ids: tuple[str, ...] = Field(default_factory=tuple)
    estimated_labor_hours: Annotated[float, Field(gt=0.0)] | None = None
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    provenance: DomainProvenance | None = None
