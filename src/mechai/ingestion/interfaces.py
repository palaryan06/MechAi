"""
Stage Protocols for the ingestion pipeline.

Every stage is a class that implements exactly one Protocol. The pipeline
orchestrator (IngestionPipeline) depends only on these Protocols — never on
concrete implementations. This makes stages independently swappable and
testable with mocks.

Extension guide
---------------
When adding Stage 5 (e.g., TorqueExtractor):
  1. Add TorqueExtractorProtocol here.
  2. Add it to StageRegistry.
  3. Add it to IngestionPipeline.__init__ and run().
  4. The existing stage protocols remain unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from mechai.ingestion.models import (
    EmbeddingResult,
    ExtractedContent,
    KnowledgeGraph,
    ParsedDocument,
)


@runtime_checkable
class PdfParserProtocol(Protocol):
    """Stage 1: Parse a PDF document into structured elements."""

    def parse(self, source: Path | bytes) -> ParsedDocument:
        """
        Parse a PDF document.

        Args:
            source: Path to a PDF file, or raw PDF bytes.

        Returns:
            ParsedDocument with text elements, tables, and markdown.

        Raises:
            DocumentParseError: If the PDF cannot be read or parsed.
        """
        ...


@runtime_checkable
class ContentExtractorProtocol(Protocol):
    """Stage 2: Extract structured content from a parsed document."""

    def extract(self, parsed: ParsedDocument) -> ExtractedContent:
        """
        Extract sections, procedures, warnings, and semantic chunks.

        Args:
            parsed: Stage 1 output.

        Returns:
            ExtractedContent ready for graph building and embedding.

        Raises:
            ExtractionError: If extraction fails critically.
        """
        ...


@runtime_checkable
class GraphBuilderProtocol(Protocol):
    """Stage 3: Build a knowledge graph from extracted content."""

    def build(self, content: ExtractedContent) -> KnowledgeGraph:
        """
        Build a knowledge graph with provenance edges.

        Args:
            content: Stage 2 output.

        Returns:
            KnowledgeGraph with typed nodes and edges.

        Raises:
            GraphBuildError: If graph construction fails.
        """
        ...


@runtime_checkable
class EmbeddingGeneratorProtocol(Protocol):
    """Stage 4: Generate vector embeddings for all semantic chunks."""

    def embed(self, content: ExtractedContent) -> EmbeddingResult:
        """
        Embed all semantic chunks from the extracted content.

        Args:
            content: Stage 2 output (chunks are the embedding unit).

        Returns:
            EmbeddingResult with chunk-embedding pairs.

        Raises:
            EmbeddingError: If the embedding provider fails.
        """
        ...


# ---------------------------------------------------------------------------
# Embedding provider (internal to Stage 4, but kept here for discoverability)
# ---------------------------------------------------------------------------


@runtime_checkable
class EmbeddingProviderProtocol(Protocol):
    """
    Pluggable embedding provider used by Stage 4.

    Implementations:
    - SentenceTransformerProvider: production, uses sentence-transformers
    - MockEmbeddingProvider: deterministic hash-based vectors for tests
    """

    @property
    def model_name(self) -> str:
        """Return the canonical name of the embedding model."""
        ...

    @property
    def dimension(self) -> int:
        """Return the vector dimension produced by this provider."""
        ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of texts.

        Args:
            texts: List of strings to embed.

        Returns:
            List of float vectors, one per input text, in the same order.

        Raises:
            EmbeddingError: If the provider fails.
        """
        ...


# ---------------------------------------------------------------------------
# Stage registry: the single place that lists all stage instances
# ---------------------------------------------------------------------------


class StageRegistry:
    """
    Container holding concrete stage implementations.

    Passed to IngestionPipeline.__init__ to enable dependency injection
    and easy swapping of implementations in tests.

    Extension note: add new stage fields here when new stages are implemented.
    """

    def __init__(
        self,
        *,
        parser: PdfParserProtocol,
        extractor: ContentExtractorProtocol,
        graph_builder: GraphBuilderProtocol,
        embedding_generator: EmbeddingGeneratorProtocol,
    ) -> None:
        self.parser = parser
        self.extractor = extractor
        self.graph_builder = graph_builder
        self.embedding_generator = embedding_generator
