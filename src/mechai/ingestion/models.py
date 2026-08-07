"""
Pydantic v2 data models for the ingestion pipeline.

Every stage has a single, well-typed output model. All pipeline models are
immutable (frozen=True) so they can be safely passed across stage boundaries
without defensive copying.

Extension guide
---------------
When adding Stage 5–16 from the full architecture, follow this pattern:
  1. Add the new output model here (e.g., TorqueSet, DiagnosticCodeSet).
  2. Add a new field to ExtractedContent if the extraction enriches it,
     OR add a new top-level model if it's a completely separate output.
  3. Add the new model to PipelineResult.
  4. Never change frozen fields on existing models — add new optional fields.

Design decisions
----------------
- image_data is intentionally excluded from all models (store path/URI instead
  to avoid OOM on large manuals with many embedded figures).
- KnowledgeGraph stores the NetworkX graph as a JSON node-link dict so the
  model is serialisable without importing NetworkX at the model layer.
- EmbeddingResult carries embeddings in-memory; the caller is responsible for
  writing them to a persistent vector store.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    import networkx as nx


# ---------------------------------------------------------------------------
# Shared provenance types
# ---------------------------------------------------------------------------


class ExtractionMethod(str, Enum):
    """How an artifact was produced."""

    RULE = "rule"
    HEURISTIC = "heuristic"
    LLM = "llm"
    DOCLING = "docling"


class BoundingBox(BaseModel):
    """Page bounding box in points from page origin."""

    model_config = ConfigDict(frozen=True)

    left: float
    top: float
    right: float
    bottom: float


class SourceRef(BaseModel):
    """Provenance: the source location in the original document."""

    model_config = ConfigDict(frozen=True)

    page_number: int = Field(ge=1)
    extraction_method: ExtractionMethod
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bbox: BoundingBox | None = None


# ---------------------------------------------------------------------------
# Stage 1: Document Parsing
# ---------------------------------------------------------------------------


class TextElementLabel(str, Enum):
    """
    Classification of a text element (mirrors Docling's DocItemLabel).

    Extension note: if Docling adds new labels (e.g., EQUATION, CODE_BLOCK),
    add them here and update the mapping in stage1_parsing.py.
    """

    TITLE = "title"
    SECTION_HEADER = "section_header"
    TEXT = "text"
    LIST_ITEM = "list_item"
    CAPTION = "caption"
    PAGE_HEADER = "page_header"
    PAGE_FOOTER = "page_footer"
    CODE = "code"
    FORMULA = "formula"
    FOOTNOTE = "footnote"
    OTHER = "other"


class TextElement(BaseModel):
    """A classified text element from the document."""

    model_config = ConfigDict(frozen=True)

    element_id: str
    text: str
    label: TextElementLabel
    page_number: int = Field(ge=1)
    level: int = Field(default=0, ge=0)
    """Heading depth: 0 = not a heading, 1 = title, 2 = chapter, 3 = section …"""
    source_ref: SourceRef


class TableElement(BaseModel):
    """A structured table extracted from the document."""

    model_config = ConfigDict(frozen=True)

    table_id: str
    caption: str | None = None
    headers: list[str]
    rows: list[list[str]]
    page_number: int = Field(ge=1)
    source_ref: SourceRef


class ParsedDocument(BaseModel):
    """
    Stage 1 output: the parsed PDF in our domain format.

    Docling-specific types do NOT appear in this model; stages 2–4 remain
    independent of the parsing library.
    """

    model_config = ConfigDict(frozen=True)

    source_path: Path
    page_count: int = Field(ge=1)
    title: str | None = None
    raw_markdown: str
    """Full document as Docling-exported markdown (for debugging and FTS)."""
    elements: list[TextElement]
    tables: list[TableElement]


# ---------------------------------------------------------------------------
# Stage 2: Structured Extraction
# ---------------------------------------------------------------------------


class WarningSeverity(str, Enum):
    """Severity of a safety warning."""

    DANGER = "danger"
    WARNING = "warning"
    CAUTION = "caution"
    NOTE = "note"


class DetectedWarning(BaseModel):
    """A safety warning detected in the document."""

    model_config = ConfigDict(frozen=True)

    warning_id: str
    severity: WarningSeverity
    text: str
    page_number: int = Field(ge=1)
    source_ref: SourceRef


class ProcedureStep(BaseModel):
    """A single ordered step in a repair procedure."""

    model_config = ConfigDict(frozen=True)

    step_number: int = Field(ge=1)
    text: str
    source_ref: SourceRef


class Procedure(BaseModel):
    """A repair procedure: a titled sequence of steps."""

    model_config = ConfigDict(frozen=True)

    procedure_id: str
    title: str
    steps: list[ProcedureStep]
    page_number: int = Field(ge=1)
    source_ref: SourceRef


class Section(BaseModel):
    """
    A document section in the heading hierarchy.

    level 1 = document title / top-level chapter
    level 2 = section (sub-chapter)
    level 3 = subsection
    level 4+ = further nesting
    """

    model_config = ConfigDict(frozen=True)

    section_id: str
    title: str
    level: int = Field(ge=1)
    page_number: int = Field(ge=1)
    parent_id: str | None = None
    source_ref: SourceRef


class SemanticChunk(BaseModel):
    """
    A self-contained text chunk aligned to section boundaries.

    Chunks are the unit of embedding (Stage 4) and retrieval.
    They carry their heading path so the reasoning engine knows context.
    """

    model_config = ConfigDict(frozen=True)

    chunk_id: str
    text: str
    heading_path: list[str]
    """e.g. ["Engine System", "Cooling", "Radiator Removal"]"""
    page_number: int = Field(ge=1)
    section_id: str | None = None
    source_ref: SourceRef


class ExtractedContent(BaseModel):
    """
    Stage 2 output: structured content ready for graph building and embedding.

    Extension note: future domain-extraction stages (torque, part numbers,
    DTCs) add their outputs as new optional fields here, defaulting to [].
    This keeps PipelineResult backward-compatible.
    """

    model_config = ConfigDict(frozen=True)

    source_path: Path
    page_count: int = Field(ge=1)
    sections: list[Section]
    procedures: list[Procedure]
    warnings: list[DetectedWarning]
    tables: list[TableElement]
    chunks: list[SemanticChunk]

    # Extension placeholders — filled by future stages
    torque_specs: list[Any] = Field(default_factory=list)
    part_numbers: list[Any] = Field(default_factory=list)
    dtc_codes: list[Any] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stage 3: Knowledge Graph
# ---------------------------------------------------------------------------


class NodeType(str, Enum):
    """Type of a knowledge graph node."""

    DOCUMENT = "document"
    SECTION = "section"
    PROCEDURE = "procedure"
    TABLE = "table"
    WARNING = "warning"
    CHUNK = "chunk"

    # Extension: add COMPONENT, TOOL, TORQUE_SPEC, DTC, SYMPTOM when
    # the corresponding extraction stages are implemented.


class EdgeType(str, Enum):
    """Type of a knowledge graph edge."""

    HAS_SECTION = "HAS_SECTION"
    HAS_SUBSECTION = "HAS_SUBSECTION"
    CONTAINS_PROCEDURE = "CONTAINS_PROCEDURE"
    CONTAINS_TABLE = "CONTAINS_TABLE"
    CONTAINS_WARNING = "CONTAINS_WARNING"
    CONTAINS_CHUNK = "CONTAINS_CHUNK"
    PRECEDES = "PRECEDES"

    # Extension: causal edges for reasoning (Phase 2)
    # CAUSES = "CAUSES"
    # SYMPTOM_OF = "SYMPTOM_OF"
    # REQUIRES = "REQUIRES"
    # IDENTIFIED_BY = "IDENTIFIED_BY"


class GraphStats(BaseModel):
    """Summary statistics about the knowledge graph."""

    model_config = ConfigDict(frozen=True)

    node_count: int
    edge_count: int
    section_count: int
    procedure_count: int
    table_count: int
    warning_count: int
    chunk_count: int


class KnowledgeGraph(BaseModel):
    """
    Stage 3 output: a knowledge graph encoded as a NetworkX node-link dict.

    The graph is stored in serialisable form (dict) rather than a live
    NetworkX object so the model can be safely pickled, JSON-serialised, and
    compared in tests without importing NetworkX at the model layer.

    Use to_networkx() to get a live DiGraph for traversal / reasoning.

    Extension note: when adding a graph database backend (Neo4j, Memgraph),
    add an export_to_cypher() method here and a GraphWriter service that
    consumes this model.
    """

    model_config = ConfigDict(frozen=True)

    source_path: Path
    graph_data: dict[str, Any]
    """NetworkX node-link JSON format (output of nx.node_link_data)."""
    stats: GraphStats

    def to_networkx(self) -> nx.DiGraph:
        """Reconstruct a live NetworkX DiGraph from the serialised data."""
        import networkx as nx

        return nx.node_link_graph(  # type: ignore[no-untyped-call]
            self.graph_data,
            directed=True,
            multigraph=False,
            edges="links",
        )


# ---------------------------------------------------------------------------
# Stage 4: Embeddings
# ---------------------------------------------------------------------------


class ChunkEmbedding(BaseModel):
    """An embedding vector for one semantic chunk."""

    model_config = ConfigDict(frozen=True)

    chunk_id: str
    text: str
    vector: list[float]
    model_name: str
    dimension: int = Field(ge=1)


class EmbeddingResult(BaseModel):
    """
    Stage 4 output: vector embeddings for all semantic chunks.

    Extension note: when connecting a persistent vector store (Qdrant,
    ChromaDB, LanceDB), add a VectorStoreWriter service that consumes this
    model. Do NOT embed vector store writes inside Stage 4 itself.
    """

    model_config = ConfigDict(frozen=True)

    source_path: Path
    embeddings: list[ChunkEmbedding]
    model_name: str
    dimension: int = Field(ge=1)
    chunk_count: int = Field(ge=0)


# ---------------------------------------------------------------------------
# Pipeline aggregate result
# ---------------------------------------------------------------------------


class PipelineResult(BaseModel):
    """
    Complete output of the four-stage ingestion pipeline.

    Consumed by:
    - The reasoning engine (graph + embeddings for retrieval)
    - Downstream writers (vector store, graph database, document store)
    - Evaluation harness (all fields for quality measurement)
    """

    model_config = ConfigDict(frozen=True)

    source_path: Path
    parsed: ParsedDocument
    content: ExtractedContent
    graph: KnowledgeGraph
    embeddings: EmbeddingResult
