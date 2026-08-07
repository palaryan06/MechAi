"""Data contracts and protocols for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Reconstructs OEM workshop manual repair and service procedures deterministically
from OrderedLayoutCIR and AutomotiveTableSet without LLMs or reasoning hallucinations.

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
    from mechai.contracts.tables import AutomotiveTableSet


class StepNumberingStyle(StrEnum):
    """Typographical styling of step prefix numbering."""

    NUMBERED = "numbered"  # 1., 2., (1), 1)
    BULLET = "bullet"  # •, -, *, ▪
    ROMAN = "roman"  # (i), (ii), i., ii., I., II.
    ALPHABETICAL = "alphabetical"  # a., b., (a), (b), A., B.
    UNNUMBERED = "unnumbered"  # Indented or narrative step


class AdmonitionType(StrEnum):
    """Safety and advisory admonition classification."""

    DANGER = "danger"
    WARNING = "warning"
    CAUTION = "caution"
    NOTE = "note"
    NOTICE = "notice"


class ProcedureCategory(StrEnum):
    """Domain taxonomy classification for OEM repair procedures."""

    REMOVAL_DISASSEMBLY = "RemovalDisassembly"
    INSTALLATION_REASSEMBLY = "InstallationReassembly"
    INSPECTION_ADJUSTMENT = "InspectionAdjustment"
    MAINTENANCE = "Maintenance"
    DIAGNOSTIC_TROUBLESHOOTING = "DiagnosticTroubleshooting"
    OVERHAUL = "Overhaul"
    GENERAL_PROCEDURE = "GeneralProcedure"


class BoundAdmonition(BaseModel):
    """Safety admonition bound directly to a procedure step or procedure header."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    admonition_id: str = Field(min_length=1, description="Unique identifier for admonition")
    admonition_type: AdmonitionType = Field(description="Admonition severity classification")
    text: str = Field(min_length=1, description="Admonition message body")
    bbox: BoundingBox = Field(description="Sub-pixel spatial bounding box")
    page_number: Annotated[int, Field(ge=1, description="1-based page index")]
    region_id: str = Field(description="Referenced layout region ID")
    provenance: SourceRef = Field(description="Grounding audit reference")


class RequiredTool(BaseModel):
    """Tool, instrument, or Special Service Tool (SST) required for procedure execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, description="Canonical name or description of tool")
    tool_number: str | None = Field(default=None, description="OEM tool number or SST identifier")
    is_sst: bool = Field(default=False, description="Whether this is an OEM Special Service Tool")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, default=1.0, description="Epistemic confidence")]


class RequiredMaterial(BaseModel):
    """Consumable, chemical, gasket, or sealant required for procedure execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, description="Material, chemical, or part name")
    specification: str | None = Field(default=None, description="OEM spec, grade, or brand")
    is_replacement_mandatory: bool = Field(default=False, description="Whether replacement with new is mandatory")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, default=1.0, description="Epistemic confidence")]


class ProcedureStep(BaseModel):
    """Atomic repair step preserving exact sequence, hierarchy, requirements, and cross-references."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str = Field(min_length=1, description="Unique step identifier")
    sequence_number: Annotated[int, Field(ge=1, description="1-based global sequential index in procedure")]
    display_number: str = Field(description="Original verbatim display prefix (e.g. '1.', '(a)', '•')")
    numbering_style: StepNumberingStyle = Field(description="Typographical numbering style")
    level: Annotated[int, Field(ge=0, description="Hierarchy depth: 0=root step, 1=substep, 2=sub-substep")]
    parent_step_id: str | None = Field(default=None, description="Parent step ID for nested substeps")
    child_step_ids: tuple[str, ...] = Field(default_factory=tuple, description="IDs of immediate child substeps")
    action_text: str = Field(min_length=1, description="Sanitized action instruction text")
    bbox: BoundingBox = Field(description="Sub-pixel spatial bounding box on page")
    page_number: Annotated[int, Field(ge=1, description="1-based page number")]
    reading_order_ref: str = Field(description="Referenced OrderedLayoutRegion ID")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, default=1.0, description="Epistemic confidence")]
    provenance: SourceRef = Field(description="Grounding audit reference")
    bound_admonitions: tuple[BoundAdmonition, ...] = Field(
        default_factory=tuple,
        description="Safety warnings/cautions/notes modifying this specific step",
    )
    required_tools: tuple[RequiredTool, ...] = Field(
        default_factory=tuple,
        description="Tools or SSTs referenced in this step",
    )
    required_materials: tuple[RequiredMaterial, ...] = Field(
        default_factory=tuple,
        description="Consumables, sealants, or replacement parts referenced in this step",
    )
    referenced_tables: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Referenced table IDs from AutomotiveTableSet or textual table identifiers",
    )
    referenced_figures: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Referenced figure or diagram identifiers (e.g. 'Fig. 6A-12')",
    )
    referenced_callouts: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Referenced diagram callout numbers/letters (e.g. '(1)', '[A]')",
    )
    referenced_pages: tuple[int, ...] = Field(
        default_factory=tuple,
        description="Referenced target page numbers",
    )
    is_optional: bool = Field(default=False, description="Whether this step is optional (e.g. 'If equipped')")
    is_branching: bool = Field(default=False, description="Whether this step introduces conditional branching")
    branch_condition: str | None = Field(default=None, description="Branching condition description if present")


class AutomotiveProcedure(BaseModel):
    """Reconstructed OEM repair procedure with complete step hierarchy and cross-page tracking."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    procedure_id: str = Field(min_length=1, description="Unique procedure identifier")
    title: str = Field(min_length=1, description="Canonical procedure title")
    description: str | None = Field(default=None, description="Introductory procedure narrative if present")
    category: ProcedureCategory = Field(
        default=ProcedureCategory.GENERAL_PROCEDURE,
        description="Domain procedure category",
    )
    steps: tuple[ProcedureStep, ...] = Field(
        default_factory=tuple,
        description="Ordered sequence of hierarchical procedure steps",
    )
    preconditions: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Initial requirements, prerequisites, or preparation actions",
    )
    postconditions: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Final inspection, reassembly, or verification actions",
    )
    required_tools: tuple[RequiredTool, ...] = Field(
        default_factory=tuple,
        description="Aggregated distinct tools & SSTs required across procedure",
    )
    required_materials: tuple[RequiredMaterial, ...] = Field(
        default_factory=tuple,
        description="Aggregated distinct consumables & materials required across procedure",
    )
    bound_admonitions: tuple[BoundAdmonition, ...] = Field(
        default_factory=tuple,
        description="Procedure-level safety warnings, cautions, or notes",
    )
    referenced_tables: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Referenced table IDs across entire procedure",
    )
    referenced_figures: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Referenced figure IDs across entire procedure",
    )
    estimated_time: str | None = Field(default=None, description="Estimated labor time if documented")
    difficulty_level: str | None = Field(default=None, description="Documented technician skill/difficulty level")
    page_span: tuple[int, int] = Field(description="Inclusive (start_page, end_page) span")
    bbox: BoundingBox | None = Field(default=None, description="Encompassing bounding box on page (if single page)")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, default=1.0, description="Epistemic confidence")]
    provenance: SourceRef = Field(description="Grounding audit reference")
    region_ids: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Underlying OrderedLayoutRegion IDs comprising this procedure",
    )
    is_multi_page: bool = Field(default=False, description="Whether procedure spans multiple physical pages")

    @property
    def total_steps(self) -> int:
        """Total number of atomic steps comprising this procedure."""
        return len(self.steps)


class AutomotiveProcedureSet(BaseModel):
    """Document-level collection of reconstructed OEM repair procedures."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1, description="Parent document identifier")
    procedures: tuple[AutomotiveProcedure, ...] = Field(
        default_factory=tuple,
        description="All reconstructed procedures in document reading order",
    )
    total_procedures: Annotated[int, Field(ge=0, description="Count of reconstructed procedures")]
    total_steps: Annotated[int, Field(ge=0, description="Sum of all steps across procedures")]
    provenance: SourceRef = Field(description="Grounding audit reference")


@runtime_checkable
class AutomotiveProcedureEngineProtocol(Protocol):
    """Standard interface protocol for Stage 7 Automotive Procedure Intelligence Engine."""

    def reconstruct_procedures(
        self,
        ordered_cir: OrderedLayoutCIR,
        table_set: AutomotiveTableSet | None = None,
    ) -> AutomotiveProcedureSet:
        """Reconstruct structured automotive procedures across an entire ordered document."""
        ...

    def reconstruct_stream(
        self,
        pages: Iterator[OrderedPageCIR],
        table_set: AutomotiveTableSet | None = None,
    ) -> Iterator[AutomotiveProcedure]:
        """Stream reconstructed procedures lazily page-by-page."""
        ...
