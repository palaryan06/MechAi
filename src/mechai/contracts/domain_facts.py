"""Data contracts for Domain Fact Extraction stages (Stages 9 to 12)."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.provenance import SourceRef  # noqa: TC001
from mechai.domain.enums import FastenerCondition, ToolCategory, TorqueUnit

# ---------------------------------------------------------------------------
# Stage 9: Tool Extraction Contracts
# ---------------------------------------------------------------------------


class ExtractedTool(BaseModel):
    """Tool reference extracted from procedural or technical text."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: ToolCategory = ToolCategory.HAND_TOOL
    size: Annotated[float, Field(gt=0.0)] | None = None
    size_unit: str | None = None
    specification: str | None = None
    sst_number: str | None = None
    procedure_id: str | None = None
    source_ref: SourceRef


class ExtractedToolSet(BaseModel):
    """Stage 9 output: extracted service tools."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tools: tuple[ExtractedTool, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 10: Torque Specification Extraction Contracts
# ---------------------------------------------------------------------------


class ExtractedTorque(BaseModel):
    """Torque specification extracted from procedural text or tables."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    torque_id: str = Field(min_length=1)
    fastener: str = Field(min_length=1)
    nominal_value: Annotated[float, Field(ge=0.0)] | None = None
    min_value: Annotated[float, Field(ge=0.0)] | None = None
    max_value: Annotated[float, Field(ge=0.0)] | None = None
    unit: TorqueUnit = TorqueUnit.NM
    angle_degrees: Annotated[float, Field(ge=0.0, le=360.0)] | None = None
    is_yield_fastener: bool = False
    condition: FastenerCondition = FastenerCondition.DRY
    procedure_id: str | None = None
    source_ref: SourceRef


class ExtractedTorqueSet(BaseModel):
    """Stage 10 output: extracted torque specifications."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    torques: tuple[ExtractedTorque, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 11: Part Number Extraction Contracts
# ---------------------------------------------------------------------------


class ExtractedPartNumber(BaseModel):
    """Part number mention extracted from text or diagrams."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    part_number_id: str = Field(min_length=1)
    part_number: str = Field(min_length=1)
    description: str | None = None
    manufacturer: str | None = None
    procedure_id: str | None = None
    source_ref: SourceRef


class ExtractedPartNumberSet(BaseModel):
    """Stage 11 output: extracted part numbers."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    part_numbers: tuple[ExtractedPartNumber, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 12: Diagnostic Trouble Code Extraction Contracts
# ---------------------------------------------------------------------------


class ExtractedDiagnosticCode(BaseModel):
    """OBD-II Diagnostic Trouble Code extracted from diagnostic procedures."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    description: str | None = None
    symptom: str | None = None
    procedure_id: str | None = None
    source_ref: SourceRef


class ExtractedDiagnosticCodeSet(BaseModel):
    """Stage 12 output: extracted diagnostic trouble codes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    codes: tuple[ExtractedDiagnosticCode, ...] = Field(default_factory=tuple)
