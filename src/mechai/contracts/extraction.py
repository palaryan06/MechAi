"""Data contracts for Content Extraction stages (Stages 5 to 8)."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.provenance import BoundingBox, SourceRef  # noqa: TC001
from mechai.domain.enums import ProcedureType, WarningSeverity

# ---------------------------------------------------------------------------
# Stage 5: Procedure Detection Contracts
# ---------------------------------------------------------------------------


class ExtractedProcedureStep(BaseModel):
    """Extracted procedure step."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_number: Annotated[int, Field(ge=1)]
    text: str = Field(min_length=1)
    source_ref: SourceRef


class ExtractedProcedure(BaseModel):
    """Extracted repair or maintenance procedure."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    procedure_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    procedure_type: ProcedureType = ProcedureType.REPLACEMENT
    steps: tuple[ExtractedProcedureStep, ...] = Field(default_factory=tuple)
    heading_id: str | None = None
    system: str | None = None
    source_ref: SourceRef


class ExtractedProcedureSet(BaseModel):
    """Stage 5 output: detected repair procedures."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    procedures: tuple[ExtractedProcedure, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 6: Table Extraction Contracts
# ---------------------------------------------------------------------------


class ExtractedTableCell(BaseModel):
    """Single cell within an extracted table."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = ""
    row: Annotated[int, Field(ge=0)]
    column: Annotated[int, Field(ge=0)]


class ExtractedTable(BaseModel):
    """Extracted tabular grid from a document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    table_id: str = Field(min_length=1)
    caption: str | None = None
    headers: tuple[str, ...] = Field(default_factory=tuple)
    rows: tuple[tuple[str, ...], ...] = Field(default_factory=tuple)
    page_number: Annotated[int, Field(ge=1)]
    source_ref: SourceRef


class ExtractedTableSet(BaseModel):
    """Stage 6 output: extracted document tables."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tables: tuple[ExtractedTable, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 7: Figure Extraction Contracts
# ---------------------------------------------------------------------------


class ExtractedFigure(BaseModel):
    """Extracted figure or technical diagram reference."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    figure_id: str = Field(min_length=1)
    caption: str | None = None
    file_path: str | None = None
    page_number: Annotated[int, Field(ge=1)]
    bbox: BoundingBox | None = None
    source_ref: SourceRef


class ExtractedFigureSet(BaseModel):
    """Stage 7 output: extracted technical figures."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    figures: tuple[ExtractedFigure, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 8: Safety Warning Extraction Contracts
# ---------------------------------------------------------------------------


class ExtractedWarning(BaseModel):
    """Extracted safety alert or caution statement."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    warning_id: str = Field(min_length=1)
    severity: WarningSeverity = WarningSeverity.WARNING
    text: str = Field(min_length=1)
    page_number: Annotated[int, Field(ge=1)]
    related_heading_id: str | None = None
    source_ref: SourceRef


class ExtractedWarningSet(BaseModel):
    """Stage 8 output: extracted safety warnings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    warnings: tuple[ExtractedWarning, ...] = Field(default_factory=tuple)
