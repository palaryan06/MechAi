"""Data contracts and stage protocols for Layout Intelligence Engine (Stage 2.0).

RFC-007: Geometric Zoning & Layout Classification.
All models are strictly typed, immutable (frozen=True), and fully validated.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.contracts.scrubbing import ParsedDocument, ParsedPage


class RegionType(StrEnum):
    """Supported semantic layout region types for Stage 2.0 Layout Intelligence."""

    HEADER = "Header"
    FOOTER = "Footer"
    MARGIN = "Margin"
    BODY = "Body"
    SIDEBAR = "Sidebar"
    TITLE = "Title"
    HEADING = "Heading"
    SUBHEADING = "Subheading"
    PARAGRAPH = "Paragraph"
    LIST = "List"
    TABLE_REGION = "TableRegion"
    FIGURE_REGION = "FigureRegion"
    CAPTION = "Caption"
    WARNING_BOX = "WarningBox"
    NOTE_BOX = "NoteBox"
    UNKNOWN = "Unknown"


class ColumnGutter(BaseModel):
    """Vertical whitespace gutter separating multi-column layout zones."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    left: float
    right: float
    top: float
    bottom: float

    @property
    def width(self) -> float:
        """Width of the whitespace gutter in points."""
        return max(0.0, self.right - self.left)

    @property
    def height(self) -> float:
        """Height of the whitespace gutter in points."""
        return max(0.0, self.bottom - self.top)


class PageMargins(BaseModel):
    """Calculated boundary margins for a document page."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    left: float = Field(ge=0.0)
    top: float = Field(ge=0.0)
    right: float = Field(ge=0.0)
    bottom: float = Field(ge=0.0)


class LayoutRegion(BaseModel):
    """Classified spatial region with exact geometric bounding and provenance.

    Every LayoutRegion maintains an unbroken mathematical link to the source page
    coordinates and physical token streams.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1, description="Unique region identifier (e.g., 'reg_p1_001')")
    bbox: BoundingBox = Field(description="Axis-aligned bounding box on the page in points")
    page_number: Annotated[int, Field(ge=1, description="1-based page number")]
    region_type: RegionType = Field(description="Classified semantic layout type")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, description="Epistemic confidence score")]
    provenance: SourceRef = Field(description="Grounding provenance referencing source extraction")
    text: str = Field(default="", description="Consolidated raw text inside this layout region")
    reading_zone_id: str | None = Field(
        default=None,
        description="Identifier of enclosing reading zone (e.g., 'zone_col_0', 'zone_header')",
    )
    column_index: int | None = Field(
        default=None,
        description="0-based column index if located inside a multi-column zone",
    )


class PageLayoutCIR(BaseModel):
    """Canonical Intermediate Representation of a single structured page layout."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_number: Annotated[int, Field(ge=1)]
    width: float = Field(gt=0.0)
    height: float = Field(gt=0.0)
    margins: PageMargins
    header_zone: BoundingBox | None = None
    footer_zone: BoundingBox | None = None
    columns: tuple[ColumnGutter, ...] = Field(default_factory=tuple)
    regions: tuple[LayoutRegion, ...] = Field(default_factory=tuple)


class LayoutCIR(BaseModel):
    """Canonical Intermediate Representation of document layout structure (Stage 2.0 output)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    source_path: str | None = None
    total_pages: Annotated[int, Field(ge=1)]
    pages: tuple[PageLayoutCIR, ...] = Field(default_factory=tuple)
    regions: tuple[LayoutRegion, ...] = Field(default_factory=tuple)
    provenance: SourceRef = Field(
        default_factory=lambda: SourceRef(
            page_number=1,
            extraction_method=ExtractionMethod.RULE,
            confidence=1.0,
        )
    )


@runtime_checkable
class GeometricLayoutZonerProtocol(Protocol):
    """Stage 2.0 Protocol: Geometric zoning and layout classification."""

    def segment_layout(self, document: ParsedDocument) -> LayoutCIR:
        """Transform ParsedDocument into complete LayoutCIR."""
        ...

    def segment_page(
        self,
        page: ParsedPage,
        page_index: int = 1,
        total_pages: int = 1,
    ) -> PageLayoutCIR:
        """Segment a single page into PageLayoutCIR."""
        ...

    def segment_stream(self, document: ParsedDocument) -> Iterator[PageLayoutCIR]:
        """Streaming generator processing pages iteratively to minimize memory."""
        ...


@runtime_checkable
class LayoutEngineProtocol(Protocol):
    """Universal Protocol interface for the Layout Intelligence Engine."""

    def process(self, document: ParsedDocument) -> LayoutCIR:
        """Process a parsed document and produce LayoutCIR."""
        ...

    def process_stream(self, document: ParsedDocument) -> Iterator[PageLayoutCIR]:
        """Stream page layouts for large documents."""
        ...
