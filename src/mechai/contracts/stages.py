"""Stage protocols (interfaces) for all 16 ingestion pipeline stages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from mechai.contracts.domain_facts import (
        ExtractedDiagnosticCodeSet,
        ExtractedPartNumberSet,
        ExtractedToolSet,
        ExtractedTorqueSet,
    )
    from mechai.contracts.extraction import (
        ExtractedFigureSet,
        ExtractedProcedureSet,
        ExtractedTableSet,
        ExtractedWarningSet,
    )
    from mechai.contracts.generation import (
        DocumentMetadata,
        EmbeddingSet,
        KnowledgeGraphModel,
        PipelineResult,
        PipelineStageOutputs,
        SemanticChunkSet,
    )
    from mechai.contracts.scrubbing import (
        HeadingTree,
        LayoutDocument,
        ParsedDocument,
        TableOfContents,
    )

# ---------------------------------------------------------------------------
# Stage 1-4 Protocols (Document Scrubbing)
# ---------------------------------------------------------------------------


@runtime_checkable
class PdfParserProtocol(Protocol):
    """Stage 1: Parse a PDF into a structured parsed document."""

    def parse(self, source: str | Path | bytes) -> ParsedDocument:
        """Parse raw PDF file or bytes into text, coordinates, and images."""
        ...


@runtime_checkable
class LayoutDetectorProtocol(Protocol):
    """Stage 2: Classify page regions into structural layout types."""

    def detect(self, document: ParsedDocument) -> LayoutDocument:
        """Classify page regions into paragraphs, headings, tables, figures, etc."""
        ...


@runtime_checkable
class TocExtractorProtocol(Protocol):
    """Stage 3: Extract the table of contents."""

    def extract(self, document: LayoutDocument) -> TableOfContents:
        """Extract table of contents entries and target pages."""
        ...


@runtime_checkable
class HeadingHierarchyBuilderProtocol(Protocol):
    """Stage 4: Construct the hierarchical outline tree."""

    def build(self, document: LayoutDocument, toc: TableOfContents) -> HeadingTree:
        """Build heading tree resolving nested hierarchy levels."""
        ...


# ---------------------------------------------------------------------------
# Stage 5-8 Protocols (Content Extraction)
# ---------------------------------------------------------------------------


@runtime_checkable
class ProcedureDetectorProtocol(Protocol):
    """Stage 5: Detect repair and service procedures."""

    def detect(self, headings: HeadingTree, document: LayoutDocument) -> ExtractedProcedureSet:
        """Detect repair procedures and their ordered action steps."""
        ...


@runtime_checkable
class TableExtractorProtocol(Protocol):
    """Stage 6: Extract structured tabular data."""

    def extract(self, document: LayoutDocument) -> ExtractedTableSet:
        """Extract structured tables with headers and rows."""
        ...


@runtime_checkable
class FigureExtractorProtocol(Protocol):
    """Stage 7: Extract figures and diagrams."""

    def extract(self, document: LayoutDocument) -> ExtractedFigureSet:
        """Extract technical figures with captions and page coordinates."""
        ...


@runtime_checkable
class WarningDetectorProtocol(Protocol):
    """Stage 8: Detect safety warnings and cautions."""

    def detect(self, document: LayoutDocument, headings: HeadingTree) -> ExtractedWarningSet:
        """Detect safety warnings (DANGER, WARNING, CAUTION, NOTE)."""
        ...


# ---------------------------------------------------------------------------
# Stage 9-12 Protocols (Domain Fact Extraction)
# ---------------------------------------------------------------------------


@runtime_checkable
class ToolExtractorProtocol(Protocol):
    """Stage 9: Extract automotive tools and SST references."""

    def extract(
        self, procedures: ExtractedProcedureSet, document: LayoutDocument
    ) -> ExtractedToolSet:
        """Extract tools referenced in procedures."""
        ...


@runtime_checkable
class TorqueExtractorProtocol(Protocol):
    """Stage 10: Extract torque specifications."""

    def extract(
        self, procedures: ExtractedProcedureSet, document: LayoutDocument
    ) -> ExtractedTorqueSet:
        """Extract torque values, units, and angle turns."""
        ...


@runtime_checkable
class PartNumberExtractorProtocol(Protocol):
    """Stage 11: Extract OEM and aftermarket part numbers."""

    def extract(
        self, procedures: ExtractedProcedureSet, document: LayoutDocument
    ) -> ExtractedPartNumberSet:
        """Extract part numbers from procedures and technical content."""
        ...


@runtime_checkable
class DiagnosticCodeExtractorProtocol(Protocol):
    """Stage 12: Extract OBD-II Diagnostic Trouble Codes (DTCs)."""

    def extract(
        self, document: LayoutDocument, procedures: ExtractedProcedureSet
    ) -> ExtractedDiagnosticCodeSet:
        """Extract OBD-II diagnostic trouble codes."""
        ...


# ---------------------------------------------------------------------------
# Stage 13-16 Protocols (Knowledge Generation)
# ---------------------------------------------------------------------------


@runtime_checkable
class MetadataGeneratorProtocol(Protocol):
    """Stage 13: Infer document-level metadata."""

    def generate(self, inputs: PipelineStageOutputs) -> DocumentMetadata:
        """Infer vehicle make, model, year, system, and document type."""
        ...


@runtime_checkable
class KnowledgeGraphGeneratorProtocol(Protocol):
    """Stage 14: Assemble the automotive knowledge graph."""

    def generate(self, inputs: PipelineStageOutputs) -> KnowledgeGraphModel:
        """Construct knowledge graph nodes and edges from extracted domain entities."""
        ...


@runtime_checkable
class AgenticChunkerProtocol(Protocol):
    """Stage 15: Segment document into semantic chunks."""

    def chunk(
        self,
        document: ParsedDocument,
        headings: HeadingTree,
        procedures: ExtractedProcedureSet,
    ) -> SemanticChunkSet:
        """Segment document into coherent chunks along semantic boundaries."""
        ...


@runtime_checkable
class EmbeddingGeneratorProtocol(Protocol):
    """Stage 16: Generate vector embeddings for chunks."""

    def embed(self, chunks: SemanticChunkSet) -> EmbeddingSet:
        """Generate vector embeddings for all semantic chunks."""
        ...


# ---------------------------------------------------------------------------
# Provider & Pipeline Protocols
# ---------------------------------------------------------------------------


@runtime_checkable
class EmbeddingProviderProtocol(Protocol):
    """Pluggable provider interface for vector embedding generation."""

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector."""
        ...

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a batch of text strings into vectors."""
        ...


@runtime_checkable
class IngestionPipelineProtocol(Protocol):
    """End-to-end ingestion pipeline orchestrator protocol."""

    def run(self, source: str | Path | bytes) -> PipelineResult:
        """Execute all ingestion stages end-to-end."""
        ...
