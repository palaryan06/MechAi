"""Procedure, Step, Tool, TorqueSpecification, and Warning domain entities."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator

from mechai.domain.base import DomainModel, DomainProvenance
from mechai.domain.enums import (
    FastenerCondition,
    HazardType,
    ProcedureType,
    ToolCategory,
    TorqueUnit,
    WarningSeverity,
)


class TorqueSpecification(DomainModel):
    """Fastener tightening specification and angle sequence.

    Attributes:
        torque_id: Unique domain identifier (e.g., 'tq_caliper_mount_bolt').
        fastener: Description of the fastener (e.g., 'Caliper mounting bolts').
        nominal_value: Primary torque value (e.g., 108.0).
        min_value: Minimum allowable torque limit.
        max_value: Maximum allowable torque limit.
        unit: Torque unit measurement.
        angle_degrees: Additional angular turn in degrees for torque-to-yield fasteners.
        is_yield_fastener: Whether fastener is torque-to-yield (replace once removed).
        condition: Thread surface preparation requirement (dry, lubricated, threadlocker).
        sequence_order: Tightening sequence step number in multi-stage sequences.
        notes: Special notes or safety instructions.
        provenance: Grounding provenance.
    """

    torque_id: str = Field(min_length=1)
    fastener: str = Field(min_length=1)
    nominal_value: Annotated[float, Field(ge=0.0)] | None = None
    min_value: Annotated[float, Field(ge=0.0)] | None = None
    max_value: Annotated[float, Field(ge=0.0)] | None = None
    unit: TorqueUnit = TorqueUnit.NM
    angle_degrees: Annotated[float, Field(ge=0.0, le=360.0)] | None = None
    is_yield_fastener: bool = False
    condition: FastenerCondition = FastenerCondition.DRY
    sequence_order: Annotated[int, Field(ge=1)] | None = None
    notes: str | None = None
    provenance: DomainProvenance | None = None

    @field_validator("max_value")
    @classmethod
    def validate_torque_limits(cls, v: float | None, info: object) -> float | None:
        """Ensure max_value is greater than or equal to min_value."""
        if v is not None and hasattr(info, "data") and "min_value" in info.data:
            min_val = info.data["min_value"]
            if min_val is not None and v < min_val:
                raise ValueError(f"max_value ({v}) cannot be less than min_value ({min_val})")
        return v


class Warning(DomainModel):
    """Safety warning, danger alert, or caution message.

    Attributes:
        warning_id: Unique domain identifier (e.g., 'warn_high_voltage_inverter').
        severity: Warning severity level (DANGER, WARNING, CAUTION, NOTE, NOTICE).
        message: Clear safety instruction or hazard description.
        hazard_type: Type of physical or environmental hazard.
        required_ppe: List of required Personal Protective Equipment items.
        safety_precautions: List of mandated procedural precautions.
        provenance: Grounding provenance.
    """

    warning_id: str = Field(min_length=1)
    severity: WarningSeverity = WarningSeverity.WARNING
    message: str = Field(min_length=1)
    hazard_type: HazardType = HazardType.GENERAL
    required_ppe: tuple[str, ...] = Field(default_factory=tuple)
    safety_precautions: tuple[str, ...] = Field(default_factory=tuple)
    provenance: DomainProvenance | None = None


class Tool(DomainModel):
    """Automotive service tool, SST, or measuring instrument.

    Attributes:
        tool_id: Unique domain identifier (e.g., 'tool_socket_14mm', 'tool_sst_09718_00010').
        name: Common name of the tool (e.g., '14mm Socket', 'Torque Wrench').
        category: Tool classification.
        size: Nominal dimension value (e.g., 14.0).
        size_unit: Measurement unit for tool size (e.g., 'mm', 'in').
        drive_size: Socket/ratchet drive size (e.g., '3/8 in', '1/2 in').
        specification: Detailed specification or profile (e.g., '6-point deep impact').
        sst_number: OEM Special Service Tool part/tool number.
        provenance: Grounding provenance.
    """

    tool_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: ToolCategory = ToolCategory.HAND_TOOL
    size: Annotated[float, Field(gt=0.0)] | None = None
    size_unit: str | None = None
    drive_size: str | None = None
    specification: str | None = None
    sst_number: str | None = None
    provenance: DomainProvenance | None = None


class ProcedureStep(DomainModel):
    """A discrete, ordered action step within an automotive procedure.

    Attributes:
        step_number: 1-based sequential step index.
        instruction: Step instruction text.
        sub_steps: Sub-action items within this step.
        tools: Tools required specifically for this step.
        torques: Torque specifications to apply in this step.
        warnings: Safety warnings specific to this step.
        referenced_figures: Figure identifiers referenced in this step.
        notes: Additional contextual notes.
        provenance: Grounding provenance.
    """

    step_number: Annotated[int, Field(ge=1)]
    instruction: str = Field(min_length=1)
    sub_steps: tuple[str, ...] = Field(default_factory=tuple)
    tools: tuple[Tool, ...] = Field(default_factory=tuple)
    torques: tuple[TorqueSpecification, ...] = Field(default_factory=tuple)
    warnings: tuple[Warning, ...] = Field(default_factory=tuple)
    referenced_figures: tuple[str, ...] = Field(default_factory=tuple)
    notes: tuple[str, ...] = Field(default_factory=tuple)
    provenance: DomainProvenance | None = None


class Procedure(DomainModel):
    """Complete diagnostic, repair, inspection, or maintenance workflow.

    Attributes:
        procedure_id: Unique domain identifier (e.g., 'proc_brake_pad_replacement').
        title: Clear procedure title.
        procedure_type: Classification of the procedure.
        system_id: Associated vehicle system identifier.
        component_ids: Associated component identifiers.
        description: High-level overview and scope.
        steps: Ordered sequence of procedural steps.
        required_tools: Comprehensive list of tools required for the whole procedure.
        safety_warnings: General safety warnings applicable to the procedure.
        estimated_minutes: Estimated execution time in minutes.
        prerequisites: Prior procedures or vehicle prep required before starting.
        provenance: Grounding provenance.
    """

    procedure_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    procedure_type: ProcedureType = ProcedureType.REPLACEMENT
    system_id: str | None = None
    component_ids: tuple[str, ...] = Field(default_factory=tuple)
    description: str | None = None
    steps: tuple[ProcedureStep, ...] = Field(default_factory=tuple)
    required_tools: tuple[Tool, ...] = Field(default_factory=tuple)
    safety_warnings: tuple[Warning, ...] = Field(default_factory=tuple)
    estimated_minutes: Annotated[int, Field(ge=1)] | None = None
    prerequisites: tuple[str, ...] = Field(default_factory=tuple)
    provenance: DomainProvenance | None = None
