"""Data contracts and protocols for Automotive Table Intelligence Engine (RFC-AUTO-001).

Reconstructs structured automotive tables (Torque specs, service schedules, wear limits,
bearing clearances, fluid capacities, electrical specs, diagnostic trees, general specs)
from OrderedLayoutCIR deterministically without LLMs.

All models are strictly typed, immutable (frozen=True), and preserve 100% provenance.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.provenance import BoundingBox, SourceRef

if TYPE_CHECKING:
    from collections.abc import Iterator

    from mechai.contracts.ordering import OrderedLayoutCIR, OrderedPageCIR


class AutomotiveTableType(StrEnum):
    """Semantic classification of automotive technical tables."""

    TORQUE_SPECIFICATION = "TorqueSpecification"
    SERVICE_INTERVAL = "ServiceInterval"
    STANDARD_SPECIFICATION = "StandardSpecification"
    WEAR_LIMIT = "WearLimit"
    TIGHTENING_SEQUENCE = "TighteningSequence"
    FLUID_CAPACITY = "FluidCapacity"
    ELECTRICAL_SPECIFICATION = "ElectricalSpecification"
    BEARING_CLEARANCE = "BearingClearance"
    DIAGNOSTIC_LOOKUP = "DiagnosticLookup"
    GENERAL_SPECIFICATION = "GeneralSpecification"


class CellAlignment(StrEnum):
    """Horizontal text alignment inside a table cell."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFIED = "justified"


class CellType(StrEnum):
    """Functional role of a table cell."""

    HEADER = "header"
    DATA = "data"
    STUB = "stub"
    SUBHEADER = "subheader"
    UNIT_ROW = "unit_row"
    FOOTNOTE = "footnote"


class AutomotiveTableCell(BaseModel):
    """Individual cell in a reconstructed automotive table with full spatial provenance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cell_id: str = Field(min_length=1, description="Unique cell identifier")
    row_index: Annotated[int, Field(ge=0, description="0-based row index")]
    col_index: Annotated[int, Field(ge=0, description="0-based column index")]
    row_span: Annotated[int, Field(ge=1, default=1, description="Vertical span in rows")]
    col_span: Annotated[int, Field(ge=1, default=1, description="Horizontal span in columns")]
    raw_text: str = Field(default="", description="Exact extracted string content")
    normalized_text: str = Field(default="", description="Sanitized and whitespace-normalized text")
    cell_type: CellType = Field(default=CellType.DATA, description="Functional role of cell")
    alignment: CellAlignment = Field(default=CellAlignment.LEFT, description="Text alignment")
    bbox: BoundingBox = Field(description="Sub-pixel spatial bounding box on page")
    page_number: Annotated[int, Field(ge=1, description="1-based page number")]
    confidence: Annotated[float, Field(ge=0.0, le=1.0, default=1.0, description="Epistemic confidence")]
    provenance: SourceRef = Field(description="Grounding audit reference")
    reading_order_ref: str = Field(description="Referenced region ID or reading sequence index")
    unit: str | None = Field(default=None, description="Extracted automotive unit (e.g. N.m, mm, V)")
    footnote_markers: tuple[str, ...] = Field(default_factory=tuple, description="Referenced footnote tags")


class AutomotiveTableHeader(BaseModel):
    """Hierarchical and flat column header representation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    header_rows: tuple[tuple[AutomotiveTableCell, ...], ...] = Field(
        default_factory=tuple,
        description="Structured multi-level header rows (supporting nested spans)",
    )
    flat_column_names: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Canonical flattened column header names with resolved parent hierarchy",
    )
    column_units: dict[int, str] = Field(
        default_factory=dict,
        description="Resolved measurement units keyed by 0-based column index",
    )
    depth: Annotated[int, Field(ge=1, default=1, description="Number of header rows")]


class AutomotiveTableRow(BaseModel):
    """Single row of cells within an automotive table."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    row_index: Annotated[int, Field(ge=0, description="0-based row index within data rows")]
    cells: tuple[AutomotiveTableCell, ...] = Field(
        default_factory=tuple,
        description="Cells in this row ordered by column index",
    )
    is_subheader: bool = Field(default=False, description="True if row acts as a category separator")
    is_unit_row: bool = Field(default=False, description="True if row solely defines units")


class AutomotiveTableFootnote(BaseModel):
    """Footnote or qualifying note attached to an automotive table."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    marker: str = Field(min_length=1, description="Footnote marker symbol or string (e.g. *1, (a))")
    text: str = Field(min_length=1, description="Footnote definition text")
    page_number: Annotated[int, Field(ge=1, description="Page number where footnote appears")]
    provenance: SourceRef = Field(description="Grounding source reference")


class AutomotiveTable(BaseModel):
    """Reconstructed structured automotive table with complete geometry, units, and continuity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    table_id: str = Field(min_length=1, description="Unique table identifier")
    title: str | None = Field(default=None, description="Table title or caption if detected")
    table_type: AutomotiveTableType = Field(
        default=AutomotiveTableType.GENERAL_SPECIFICATION,
        description="Automotive semantic table classification",
    )
    confidence: Annotated[float, Field(ge=0.0, le=1.0, default=1.0, description="Reconstruction confidence")]
    page_number: Annotated[int, Field(ge=1, description="Primary starting page number")]
    bbox: BoundingBox = Field(description="Enclosing bounding box of the entire table")
    header: AutomotiveTableHeader = Field(description="Table header structure")
    rows: tuple[AutomotiveTableRow, ...] = Field(default_factory=tuple, description="Data rows")
    num_rows: Annotated[int, Field(ge=0, default=0, description="Total number of data rows")]
    num_columns: Annotated[int, Field(ge=0, default=0, description="Total number of columns")]
    notes: tuple[str, ...] = Field(default_factory=tuple, description="Associated general notes")
    warnings: tuple[str, ...] = Field(default_factory=tuple, description="Associated safety warnings")
    footnotes: tuple[AutomotiveTableFootnote, ...] = Field(default_factory=tuple, description="Resolved footnotes")
    is_multi_page: bool = Field(default=False, description="True if table spans multiple pages")
    is_continuation: bool = Field(default=False, description="True if continued from a previous page")
    continued_from_id: str | None = Field(default=None, description="Previous table ID if continued")
    continued_to_id: str | None = Field(default=None, description="Next table ID if continues")
    page_span: tuple[int, ...] = Field(default_factory=tuple, description="All pages spanned by table")
    is_rotated: bool = Field(default=False, description="True if table is in landscape/rotated layout")
    rotation_angle: float = Field(default=0.0, description="Rotation angle in degrees")
    provenance: SourceRef = Field(description="Enclosing grounding provenance")
    source_region_ids: tuple[str, ...] = Field(default_factory=tuple, description="Source LayoutRegion IDs")


class AutomotiveTableSet(BaseModel):
    """Complete collection of reconstructed automotive tables for a document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1, description="Source document identifier")
    tables: tuple[AutomotiveTable, ...] = Field(default_factory=tuple, description="Reconstructed tables")
    total_tables: Annotated[int, Field(ge=0, default=0, description="Total table count")]
    provenance: SourceRef = Field(description="Document-level provenance")


@runtime_checkable
class AutomotiveTableEngineProtocol(Protocol):
    """Protocol interface for Stage 6 Automotive Table Intelligence Engine."""

    def reconstruct_tables(self, ordered_layout: OrderedLayoutCIR) -> AutomotiveTableSet:
        """Reconstruct structured automotive tables from an entire OrderedLayoutCIR."""
        ...

    def reconstruct_page_tables(self, ordered_page: OrderedPageCIR) -> tuple[AutomotiveTable, ...]:
        """Reconstruct structured tables from a single OrderedPageCIR."""
        ...

    def reconstruct_stream(self, ordered_pages: Iterator[OrderedPageCIR]) -> Iterator[AutomotiveTable]:
        """Stream reconstructed tables page-by-page across document pages."""
        ...
