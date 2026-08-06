# Ingestion Pipeline Interfaces

## Why This Document Exists

This document defines the **interfaces (contracts)** between pipeline stages. Each stage is an independently testable unit that exposes a well-defined `Protocol`. The orchestrator composes stages through these protocols; no stage depends on another stage's implementation.

The design uses Python `Protocol` classes (from `typing`) for structural typing, following the [Coding Standards](../../engineering/03-coding-standards.md).

## Design Rules

1. **Every stage implements a single `Protocol`** named `<StageName>Protocol`.
2. **Each protocol declares exactly one public method** — the stage's `call` / `process` entry point.
3. **Inputs and outputs are always the Pydantic models** defined in [Data Models](04-data-models.md).
4. **No stage imports another stage's module.** Stages depend only on shared models.
5. **The orchestrator** (`IngestionPipeline`) is the only component that knows stage ordering.

## Common Type Aliases

```python
from typing import TypeAlias

DocumentBytes: TypeAlias = bytes
DocumentPath: TypeAlias = str | Path
```

## Stage Protocols

### Stage 1: Document Scrubbing

```python
class PdfParserProtocol(Protocol):
    """Stage 1: Parse a PDF into a parsed document."""

    def parse(self, source: DocumentPath | DocumentBytes) -> ParsedDocument:
        """Parse a PDF into pages with text, images, and coordinates.

        Args:
            source: PDF file path or raw bytes.

        Returns:
            ParsedDocument with page-level content.

        Raises:
            DocumentParseError: If the PDF cannot be read.
        """
```

```python
class LayoutDetectorProtocol(Protocol):
    """Stage 2: Classify page regions into layout types."""

    def detect(self, document: ParsedDocument) -> LayoutDocument:
        """Classify each page region into layout types.

        Args:
            document: The parsed PDF document.

        Returns:
            LayoutDocument with typed layout elements.

        Raises:
            LayoutDetectionError: If layout classification fails.
        """
```

```python
class TocExtractorProtocol(Protocol):
    """Stage 3: Extract the table of contents."""

    def extract(self, document: LayoutDocument) -> Toc:
        """Extract the table of contents entries.

        Args:
            document: The layout-classified document.

        Returns:
            Toc with ordered entries.

        Raises:
            TocExtractionError: If TOC pages are found but cannot be parsed.
        """
```

```python
class HeadingHierarchyBuilderProtocol(Protocol):
    """Stage 4: Build the heading hierarchy tree."""

    def build(self, document: LayoutDocument, toc: Toc) -> HeadingTree:
        """Build a hierarchical heading tree.

        Args:
            document: The layout-classified document.
            toc: The extracted table of contents.

        Returns:
            HeadingTree with levels resolved.
        """
```

### Stage 2: Content Extraction

```python
class ProcedureDetectorProtocol(Protocol):
    """Stage 5: Detect repair procedures and their steps."""

    def detect(self, headings: HeadingTree, document: LayoutDocument) -> ProcedureSet:
        """Detect procedures with ordered steps.

        Args:
            headings: The heading hierarchy.
            document: The layout-classified document.

        Returns:
            ProcedureSet with detected procedures.
        """
```

```python
class TableExtractorProtocol(Protocol):
    """Stage 6: Extract tables."""

    def extract(self, document: LayoutDocument) -> TableSet:
        """Extract structured tables.

        Args:
            document: The layout-classified document.

        Returns:
            TableSet with extracted tables.
        """
```

```python
class FigureExtractorProtocol(Protocol):
    """Stage 7: Extract figures and images."""

    def extract(self, document: LayoutDocument) -> FigureSet:
        """Extract figures with captions.

        Args:
            document: The layout-classified document.

        Returns:
            FigureSet with extracted figures.
        """
```

```python
class WarningDetectorProtocol(Protocol):
    """Stage 8: Detect safety warnings."""

    def detect(self, document: LayoutDocument, headings: HeadingTree) -> WarningSet:
        """Detect warnings (DANGER, WARNING, CAUTION, NOTE).

        Args:
            document: The layout-classified document.
            headings: The heading hierarchy for context.

        Returns:
            WarningSet with detected warnings.
        """
```

### Stage 3: Domain Extraction

```python
class ToolExtractorProtocol(Protocol):
    """Stage 9: Extract tools."""

    def extract(self, procedures: ProcedureSet, document: LayoutDocument) -> ToolSet:
        """Extract tools mentioned in procedures.

        Args:
            procedures: Detected procedures.
            document: The layout-classified document.

        Returns:
            ToolSet with extracted tools.
        """
```

```python
class TorqueExtractorProtocol(Protocol):
    """Stage 10: Extract torque specifications."""

    def extract(self, procedures: ProcedureSet, document: LayoutDocument) -> TorqueSet:
        """Extract torque specs.

        Args:
            procedures: Detected procedures.
            document: The layout-classified document.

        Returns:
            TorqueSet with extracted torque values.
        """
```

```python
class PartNumberExtractorProtocol(Protocol):
    """Stage 11: Extract part numbers."""

    def extract(self, procedures: ProcedureSet, document: LayoutDocument) -> PartNumberSet:
        """Extract OEM part numbers.

        Args:
            procedures: Detected procedures.
            document: The layout-classified document.

        Returns:
            PartNumberSet with extracted part numbers.
        """
```

```python
class DiagnosticCodeExtractorProtocol(Protocol):
    """Stage 12: Extract diagnostic trouble codes."""

    def extract(self, document: LayoutDocument, procedures: ProcedureSet) -> DiagnosticCodeSet:
        """Extract OBD-II diagnostic codes.

        Args:
            document: The layout-classified document.
            procedures: Detected procedures.

        Returns:
            DiagnosticCodeSet with extracted DTCs.
        """
```

### Stage 4: Knowledge Generation

```python
class MetadataGeneratorProtocol(Protocol):
    """Stage 13: Generate document-level metadata."""

    def generate(self, inputs: PipelineStageOutputs) -> DocumentMetadata:
        """Infer document metadata (make, model, year, system, type).

        Args:
            inputs: All prior stage outputs.

        Returns:
            DocumentMetadata with inferred attributes.
        """
```

```python
class KnowledgeGraphGeneratorProtocol(Protocol):
    """Stage 14: Generate the knowledge graph."""

    def generate(self, inputs: PipelineStageOutputs) -> GraphModel:
        """Assemble knowledge graph triples from extracted outputs.

        Args:
            inputs: All prior stage outputs.

        Returns:
            GraphModel with nodes and edges.
        """
```

```python
class AgenticChunkerProtocol(Protocol):
    """Stage 15: Segment the document into agentic chunks."""

    def chunk(self, document: ParsedDocument, headings: HeadingTree,
              procedures: ProcedureSet) -> ChunkSet:
        """Segment the document into semantic chunks.

        Args:
            document: The parsed PDF document.
            headings: The heading hierarchy.
            procedures: Detected procedures.

        Returns:
            ChunkSet with coherent text chunks.
        """
```

```python
class EmbeddingGeneratorProtocol(Protocol):
    """Stage 16: Generate embeddings for chunks."""

    def embed(self, chunks: ChunkSet) -> EmbeddingSet:
        """Embed each chunk.

        Args:
            chunks: The agentic chunks.

        Returns:
            EmbeddingSet with chunk-embedding pairs.

        Raises:
            EmbeddingError: If the embedding provider fails.
        """
```

## The Embedding Provider (Internal)

The embedding generator uses an injectable **embedding provider**:

```python
class EmbeddingProvider(Protocol):
    """Produces vector embeddings for text."""

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector."""

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text strings."""
```

Two implementations:

| Provider | Use | Deterministic? |
|----------|-----|----------------|
| `InMemoryEmbeddingProvider` | Tests | Yes — hash-based vector |
| `SentenceTransformerProvider` | Production | No — model-based |

## The Pipeline Orchestrator

```python
class IngestionPipeline:
    """Composes all 16 stages in order."""

    def __init__(self, stages: StageRegistry) -> None:
        """Construct the pipeline from a stage registry.

        Args:
            stages: A registry mapping stage keys to stage instances.
        """

    def run(self, source: DocumentPath | DocumentBytes) -> PipelineResult:
        """Run the full ingestion pipeline.

        Args:
            source: PDF file path or raw bytes.

        Returns:
            PipelineResult with all stage outputs.

        Raises:
            IngestionError: If any stage fails.
        """
```

The `StageRegistry` is a dataclass holding instances of all 16 stages, making the pipeline easily configurable and testable with mock stages.

## Configuration Interface

The `common/config.py` module exposes typed configuration:

```python
class IngestionConfig:
    """Ingestion pipeline configuration.

    Attributes:
        embedding_provider: Provider name ("in_memory" | "sentence_transformers").
        embedding_model: Model name for the external provider.
        chunk_max_tokens: Max tokens per agentic chunk.
        chunk_overlap_tokens: Overlap tokens between chunks.
    """

    embedding_provider: str
    embedding_model: str
    chunk_max_tokens: int
    chunk_overlap_tokens: int
```

## How to Use This Document

1. **Implementing a stage?** Implement the corresponding Protocol and its method.
2. **Testing a stage?** Pass a mock/real previous-stage output through the Protocol.
3. **Composing stages?** Use the `IngestionPipeline` and `StageRegistry`.

## Related Documents

- [Architecture](01-architecture.md) — stage descriptions.
- [Data Models](04-data-models.md) — the model definitions.
- [Folder Structure](02-folder-structure.md) — where implementations live.
- [Implementation Plan](05-implementation-plan.md) — build order.