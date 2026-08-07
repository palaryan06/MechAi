"""Data contracts for Knowledge Generation stages (Stages 13 to 16) and Aggregates."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.domain_facts import (  # noqa: TC001
    ExtractedDiagnosticCodeSet,
    ExtractedPartNumberSet,
    ExtractedToolSet,
    ExtractedTorqueSet,
)
from mechai.contracts.extraction import (  # noqa: TC001
    ExtractedFigureSet,
    ExtractedProcedureSet,
    ExtractedTableSet,
    ExtractedWarningSet,
)
from mechai.contracts.provenance import SourceRef  # noqa: TC001
from mechai.contracts.scrubbing import (  # noqa: TC001
    HeadingTree,
    LayoutDocument,
    ParsedDocument,
    TableOfContents,
)
from mechai.domain.enums import DocumentType

# ---------------------------------------------------------------------------
# Stage 13: Document Metadata Generation Contracts
# ---------------------------------------------------------------------------


class DocumentMetadata(BaseModel):
    """Stage 13 output: inferred document-level automotive metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    make: str | None = None
    model: str | None = None
    year_start: Annotated[int, Field(ge=1886, le=2100)] | None = None
    year_end: Annotated[int, Field(ge=1886, le=2100)] | None = None
    system: str | None = None
    document_type: DocumentType = DocumentType.WORKSHOP_MANUAL
    page_count: Annotated[int, Field(ge=1)]
    title: str | None = None
    source_ref: SourceRef


# ---------------------------------------------------------------------------
# Stage 14: Knowledge Graph Generation Contracts
# ---------------------------------------------------------------------------


class NodeType(StrEnum):
    """Classification of knowledge graph nodes."""

    VEHICLE = "vehicle"
    ENGINE = "engine"
    TRANSMISSION = "transmission"
    SYSTEM = "system"
    COMPONENT = "component"
    PROCEDURE = "procedure"
    TOOL = "tool"
    TORQUE = "torque"
    PART_NUMBER = "part_number"
    DIAGNOSTIC_CODE = "diagnostic_code"
    WARNING = "warning"
    SYMPTOM = "symptom"
    MANUAL = "manual"
    SECTION = "section"


class EdgeType(StrEnum):
    """Relationships between automotive knowledge graph nodes."""

    PART_OF = "PART_OF"
    USES_TOOL = "USES_TOOL"
    REQUIRES_TORQUE = "REQUIRES_TORQUE"
    WARNED_BY = "WARNED_BY"
    IDENTIFIED_BY = "IDENTIFIED_BY"
    APPLIES_TO = "APPLIES_TO"
    SYMPTOM_OF = "SYMPTOM_OF"
    RESOLVED_BY = "RESOLVED_BY"
    PRECEDES = "PRECEDES"
    REFERENCES = "REFERENCES"


class GraphNode(BaseModel):
    """Node in the generated knowledge graph."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str = Field(min_length=1)
    node_type: NodeType
    label: str = Field(min_length=1)
    properties: dict[str, str] = Field(default_factory=dict)
    source_ref: SourceRef


class GraphEdge(BaseModel):
    """Directed edge in the generated knowledge graph."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    edge_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    edge_type: EdgeType
    properties: dict[str, str] = Field(default_factory=dict)
    source_ref: SourceRef


class KnowledgeGraphModel(BaseModel):
    """Stage 14 output: assembled knowledge graph triples."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    nodes: tuple[GraphNode, ...] = Field(default_factory=tuple)
    edges: tuple[GraphEdge, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 15: Agentic Semantic Chunker Contracts
# ---------------------------------------------------------------------------


class SemanticChunk(BaseModel):
    """Self-contained semantic text chunk aligned to section and procedural boundaries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    heading_path: tuple[str, ...] = Field(default_factory=tuple)
    page_number: Annotated[int, Field(ge=1)]
    procedure_id: str | None = None
    section_id: str | None = None
    token_count: Annotated[int, Field(ge=1)] | None = None
    source_ref: SourceRef


class SemanticChunkSet(BaseModel):
    """Stage 15 output: semantic chunks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    chunks: tuple[SemanticChunk, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Stage 16: Embedding Generation Contracts
# ---------------------------------------------------------------------------


class ChunkEmbedding(BaseModel):
    """Vector embedding for a specific semantic chunk."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: str = Field(min_length=1)
    vector: tuple[float, ...] = Field(min_length=1)
    model: str = Field(min_length=1)
    dimension: Annotated[int, Field(ge=1)]


class EmbeddingSet(BaseModel):
    """Stage 16 output: vector embeddings for all document chunks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    embeddings: tuple[ChunkEmbedding, ...] = Field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Aggregated Pipeline Output Contracts
# ---------------------------------------------------------------------------


class PipelineStageOutputs(BaseModel):
    """Container aggregating intermediate outputs across all stages."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    parsed_document: ParsedDocument
    layout_document: LayoutDocument
    toc: TableOfContents
    heading_tree: HeadingTree
    procedures: ExtractedProcedureSet
    tables: ExtractedTableSet
    figures: ExtractedFigureSet
    warnings: ExtractedWarningSet
    tools: ExtractedToolSet
    torques: ExtractedTorqueSet
    part_numbers: ExtractedPartNumberSet
    diagnostic_codes: ExtractedDiagnosticCodeSet


class PipelineResult(BaseModel):
    """Final output emitted by the completed IngestionPipeline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metadata: DocumentMetadata
    graph: KnowledgeGraphModel
    chunks: SemanticChunkSet
    embeddings: EmbeddingSet
    source_path: str | None = None
