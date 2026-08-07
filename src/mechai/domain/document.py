"""Manual, DocumentSection, Figure, and Table domain entities."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator

from mechai.domain.base import DomainModel, DomainProvenance
from mechai.domain.enums import DiagramType, DocumentType, TableType


class Figure(DomainModel):
    """Technical diagram, schematic, exploded view, or illustration reference.

    Attributes:
        figure_id: Unique domain identifier (e.g., 'fig_brake_caliper_exploded').
        label: Figure designation string (e.g., 'Fig. 14-2', 'Illustration A').
        caption: Caption or description describing the diagram.
        diagram_type: Classification of the visual representation.
        referenced_components: Identifiers of components highlighted in this figure.
        referenced_tools: Identifiers of tools depicted in this figure.
        page_number: 1-based source page number where the figure appears.
        provenance: Grounding provenance.
    """

    figure_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    caption: str | None = None
    diagram_type: DiagramType = DiagramType.EXPLODED_VIEW
    referenced_components: tuple[str, ...] = Field(default_factory=tuple)
    referenced_tools: tuple[str, ...] = Field(default_factory=tuple)
    page_number: Annotated[int, Field(ge=1)] | None = None
    provenance: DomainProvenance | None = None


class Table(DomainModel):
    """Structured tabular data within automotive service documentation.

    Attributes:
        table_id: Unique domain identifier (e.g., 'tbl_brake_torque_specs').
        label: Table reference string (e.g., 'Table 5-1', 'Specifications Matrix').
        title: Descriptive table header title.
        table_type: Tabular classification.
        headers: Column header names.
        rows: Structured grid of row cell values.
        page_number: 1-based source page number where the table appears.
        provenance: Grounding provenance.
    """

    table_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    title: str | None = None
    table_type: TableType = TableType.SPECIFICATIONS
    headers: tuple[str, ...] = Field(default_factory=tuple)
    rows: tuple[tuple[str, ...], ...] = Field(default_factory=tuple)
    page_number: Annotated[int, Field(ge=1)] | None = None
    provenance: DomainProvenance | None = None


class DocumentSection(DomainModel):
    """Structured hierarchical section or chapter within automotive documentation.

    Attributes:
        section_id: Unique domain identifier (e.g., 'sec_br_disc_brake_pad').
        section_number: Section code or number (e.g., 'BR-14', 'Section 5.2').
        title: Section title text.
        level: Hierarchical outline level (1 = Chapter, 2 = Section, etc.).
        parent_section_id: Identifier of the enclosing parent section.
        subsections: Identifiers of child sub-sections.
        system_ids: Vehicle systems covered in this section.
        component_ids: Components referenced in this section.
        procedure_ids: Procedures defined within this section.
        page_start: Starting page number of this section.
        page_end: Ending page number of this section.
        provenance: Grounding provenance.
    """

    section_id: str = Field(min_length=1)
    section_number: str | None = None
    title: str = Field(min_length=1)
    level: Annotated[int, Field(ge=1)] = 1
    parent_section_id: str | None = None
    subsections: tuple[str, ...] = Field(default_factory=tuple)
    system_ids: tuple[str, ...] = Field(default_factory=tuple)
    component_ids: tuple[str, ...] = Field(default_factory=tuple)
    procedure_ids: tuple[str, ...] = Field(default_factory=tuple)
    page_start: Annotated[int, Field(ge=1)] | None = None
    page_end: Annotated[int, Field(ge=1)] | None = None
    provenance: DomainProvenance | None = None

    @field_validator("page_end")
    @classmethod
    def validate_page_range(cls, v: int | None, info: object) -> int | None:
        """Ensure page_end is greater than or equal to page_start."""
        if v is not None and hasattr(info, "data") and "page_start" in info.data:
            page_start = info.data["page_start"]
            if page_start is not None and v < page_start:
                raise ValueError(f"page_end ({v}) cannot be less than page_start ({page_start})")
        return v


class Manual(DomainModel):
    """Technical service manual or workshop documentation container.

    Attributes:
        manual_id: Unique domain identifier (e.g., 'man_toyota_supra_1994_rm390u').
        title: Full publication title.
        document_type: Technical document categorization.
        publisher: Publishing organization or OEM.
        publication_year: Year of publication.
        document_code: OEM publication reference code (e.g., 'RM390U').
        target_vehicles: Identifiers of applicable vehicle models.
        target_engines: Identifiers of applicable engines.
        target_transmissions: Identifiers of applicable transmissions.
        sections: Nested or referenced document sections.
        figures: Figures included in this manual.
        tables: Tables included in this manual.
        total_pages: Total documented page count.
        provenance: Grounding provenance.
    """

    manual_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    document_type: DocumentType = DocumentType.WORKSHOP_MANUAL
    publisher: str | None = None
    publication_year: Annotated[int, Field(ge=1886, le=2100)] | None = None
    document_code: str | None = None
    target_vehicles: tuple[str, ...] = Field(default_factory=tuple)
    target_engines: tuple[str, ...] = Field(default_factory=tuple)
    target_transmissions: tuple[str, ...] = Field(default_factory=tuple)
    sections: tuple[DocumentSection, ...] = Field(default_factory=tuple)
    figures: tuple[Figure, ...] = Field(default_factory=tuple)
    tables: tuple[Table, ...] = Field(default_factory=tuple)
    total_pages: Annotated[int, Field(ge=1)] | None = None
    provenance: DomainProvenance | None = None
