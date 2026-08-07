"""Data contracts for Document Scrubbing stages (Stages 1 to 4)."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.provenance import BoundingBox, SourceRef  # noqa: TC001

# ---------------------------------------------------------------------------
# Stage 1: PDF Parsing Contracts
# ---------------------------------------------------------------------------


class ParsedWord(BaseModel):
    """Word token with positional and typographical metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(min_length=1)
    left: float
    top: float
    right: float
    bottom: float
    font_size: float | None = None
    font_name: str | None = None
    bold: bool = False
    italic: bool = False


class ParsedImage(BaseModel):
    """Embedded image metadata extracted from a page."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    image_id: str = Field(min_length=1)
    bbox: BoundingBox | None = None
    width: Annotated[int, Field(ge=1)] | None = None
    height: Annotated[int, Field(ge=1)] | None = None
    image_format: str | None = None
    file_path: str | None = None


class ParsedPage(BaseModel):
    """Parsed representation of a single document page."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_number: Annotated[int, Field(ge=1)]
    text: str = ""
    words: tuple[ParsedWord, ...] = Field(default_factory=tuple)
    images: tuple[ParsedImage, ...] = Field(default_factory=tuple)
    width: float | None = None
    height: float | None = None


class ParsedDocument(BaseModel):
    """Stage 1 output: fully parsed document representation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pages: tuple[ParsedPage, ...] = Field(default_factory=tuple)
    source_path: str | None = None

    @property
    def total_pages(self) -> int:
        """Total count of pages in the parsed document."""
        return len(self.pages)


# ---------------------------------------------------------------------------
# Stage 2: Layout Detection Contracts
# ---------------------------------------------------------------------------


class LayoutType(StrEnum):
    """Classified visual and structural layout element type."""

    PARAGRAPH = "paragraph"
    HEADING = "heading"
    TABLE = "table"
    FIGURE = "figure"
    LIST = "list"
    CODE = "code"
    TOC = "toc"
    HEADER = "header"
    FOOTER = "footer"
    UNKNOWN = "unknown"


class LayoutElement(BaseModel):
    """Classified region on a page with layout semantics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    element_id: str = Field(min_length=1)
    layout_type: LayoutType
    text: str = ""
    page_number: Annotated[int, Field(ge=1)]
    bbox: BoundingBox | None = None
    heading_level: Annotated[int, Field(ge=1)] | None = None
    source_ref: SourceRef


class LayoutDocument(BaseModel):
    """Stage 2 output: ordered collection of classified layout elements."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    elements: tuple[LayoutElement, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 3: Table of Contents (TOC) Extraction Contracts
# ---------------------------------------------------------------------------


class TocEntry(BaseModel):
    """Single entry within a table of contents."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    level: Annotated[int, Field(ge=1)]
    title: str = Field(min_length=1)
    target_page: Annotated[int, Field(ge=1)]
    source_ref: SourceRef


class TableOfContents(BaseModel):
    """Stage 3 output: extracted table of contents outline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[TocEntry, ...] = Field(default_factory=tuple)
    detected: bool = True


# ---------------------------------------------------------------------------
# Stage 4: Heading Hierarchy Tree Contracts
# ---------------------------------------------------------------------------


class HeadingNode(BaseModel):
    """Hierarchical node within the document outline tree."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    level: Annotated[int, Field(ge=1)]
    page_number: Annotated[int, Field(ge=1)]
    parent_id: str | None = None
    children: tuple[HeadingNode, ...] = Field(default_factory=tuple)
    source_ref: SourceRef


class HeadingTree(BaseModel):
    """Stage 4 output: full document heading hierarchy."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    roots: tuple[HeadingNode, ...] = Field(default_factory=tuple)
    nodes: tuple[HeadingNode, ...] = Field(default_factory=tuple)
