"""Unit tests for ingestion pipeline data contracts and stage protocols."""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from pathlib import Path  # noqa: TC003

import pytest
from pydantic import ValidationError

from mechai.contracts import (
    AgenticChunkerProtocol,
    BoundingBox,
    ChunkEmbedding,
    DiagnosticCodeExtractorProtocol,
    DocumentMetadata,
    EdgeType,
    EmbeddingGeneratorProtocol,
    EmbeddingProviderProtocol,
    EmbeddingSet,
    ExtractedDiagnosticCode,
    ExtractedDiagnosticCodeSet,
    ExtractedFigure,
    ExtractedFigureSet,
    ExtractedPartNumber,
    ExtractedPartNumberSet,
    ExtractedProcedure,
    ExtractedProcedureSet,
    ExtractedProcedureStep,
    ExtractedTable,
    ExtractedTableCell,
    ExtractedTableSet,
    ExtractedTool,
    ExtractedToolSet,
    ExtractedTorque,
    ExtractedTorqueSet,
    ExtractedWarning,
    ExtractedWarningSet,
    ExtractionMethod,
    FigureExtractorProtocol,
    GraphEdge,
    GraphNode,
    HeadingHierarchyBuilderProtocol,
    HeadingNode,
    HeadingTree,
    IngestionPipelineProtocol,
    KnowledgeGraphGeneratorProtocol,
    KnowledgeGraphModel,
    LayoutDetectorProtocol,
    LayoutDocument,
    LayoutElement,
    LayoutType,
    MetadataGeneratorProtocol,
    NodeType,
    ParsedDocument,
    ParsedImage,
    ParsedPage,
    ParsedWord,
    PartNumberExtractorProtocol,
    PdfParserProtocol,
    PipelineResult,
    PipelineStageOutputs,
    ProcedureDetectorProtocol,
    SemanticChunk,
    SemanticChunkSet,
    SourceRef,
    TableExtractorProtocol,
    TableOfContents,
    TocEntry,
    TocExtractorProtocol,
    ToolExtractorProtocol,
    TorqueExtractorProtocol,
    WarningDetectorProtocol,
)
from mechai.domain.enums import (
    DocumentType,
    ProcedureType,
    ToolCategory,
    TorqueUnit,
    WarningSeverity,
)

# ---------------------------------------------------------------------------
# Provenance & Scrubbing Tests (Stages 1-4)
# ---------------------------------------------------------------------------


def test_provenance_and_bounding_box() -> None:
    """Verify BoundingBox and SourceRef geometry and immutability."""
    bbox = BoundingBox(left=10.0, top=20.0, right=110.0, bottom=120.0)
    assert bbox.width == 100.0
    assert bbox.height == 100.0

    source_ref = SourceRef(
        page_number=1,
        extraction_method=ExtractionMethod.DOCLING,
        confidence=0.95,
        bbox=bbox,
    )
    assert source_ref.extraction_method == ExtractionMethod.DOCLING
    assert source_ref.confidence == 0.95

    with pytest.raises(ValidationError):
        setattr(source_ref, "confidence", 0.5)


def test_stage1_parsed_document() -> None:
    """Verify ParsedDocument contract structure."""
    word = ParsedWord(text="Engine", left=50.0, top=70.0, right=90.0, bottom=85.0)
    img = ParsedImage(image_id="img_001", width=640, height=480)
    page = ParsedPage(page_number=1, text="Engine Overview", words=(word,), images=(img,))
    doc = ParsedDocument(pages=(page,), source_path="/path/to/manual.pdf")

    assert doc.total_pages == 1
    assert doc.pages[0].words[0].text == "Engine"


def test_stage2_layout_document() -> None:
    """Verify LayoutDocument contract."""
    source_ref = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE)
    elem = LayoutElement(
        element_id="elem_001",
        layout_type=LayoutType.HEADING,
        text="Chapter 1: Maintenance",
        page_number=1,
        heading_level=1,
        source_ref=source_ref,
    )
    layout = LayoutDocument(elements=(elem,))
    assert layout.elements[0].layout_type == LayoutType.HEADING


def test_stage3_toc_and_stage4_heading_tree() -> None:
    """Verify TableOfContents and HeadingTree contracts."""
    source_ref = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE)
    toc_entry = TocEntry(level=1, title="Brakes", target_page=10, source_ref=source_ref)
    toc = TableOfContents(entries=(toc_entry,), detected=True)
    assert len(toc.entries) == 1

    node = HeadingNode(
        node_id="node_1",
        title="Brakes",
        level=1,
        page_number=10,
        source_ref=source_ref,
    )
    tree = HeadingTree(roots=(node,), nodes=(node,))
    assert len(tree.roots) == 1


# ---------------------------------------------------------------------------
# Extraction Stage Tests (Stages 5-8)
# ---------------------------------------------------------------------------


def test_stage5_to_stage8_contracts() -> None:
    """Verify extraction contracts for procedures, tables, figures, warnings."""
    source_ref = SourceRef(page_number=5, extraction_method=ExtractionMethod.RULE)

    # Stage 5
    step = ExtractedProcedureStep(step_number=1, text="Disconnect battery", source_ref=source_ref)
    proc = ExtractedProcedure(
        procedure_id="proc_1",
        title="Battery Service",
        procedure_type=ProcedureType.REPLACEMENT,
        steps=(step,),
        source_ref=source_ref,
    )
    proc_set = ExtractedProcedureSet(procedures=(proc,))
    assert len(proc_set.procedures) == 1

    # Stage 6
    tbl = ExtractedTable(
        table_id="tbl_1",
        caption="Specs",
        headers=("Spec", "Value"),
        rows=(("Torque", "50 Nm"),),
        page_number=5,
        source_ref=source_ref,
    )
    cell = ExtractedTableCell(text="50 Nm", row=0, column=1)
    assert cell.text == "50 Nm"
    tbl_set = ExtractedTableSet(tables=(tbl,))
    assert len(tbl_set.tables) == 1

    # Stage 7
    fig = ExtractedFigure(figure_id="fig_1", page_number=5, source_ref=source_ref)
    fig_set = ExtractedFigureSet(figures=(fig,))
    assert len(fig_set.figures) == 1

    # Stage 8
    warn = ExtractedWarning(
        warning_id="warn_1",
        severity=WarningSeverity.CAUTION,
        text="Wear safety glasses",
        page_number=5,
        source_ref=source_ref,
    )
    warn_set = ExtractedWarningSet(warnings=(warn,))
    assert len(warn_set.warnings) == 1


# ---------------------------------------------------------------------------
# Domain Fact Extraction Tests (Stages 9-12)
# ---------------------------------------------------------------------------


def test_stage9_to_stage12_contracts() -> None:
    """Verify contracts for tools, torques, part numbers, and DTCs."""
    source_ref = SourceRef(page_number=8, extraction_method=ExtractionMethod.RULE)

    # Tool
    tool = ExtractedTool(
        tool_id="tool_1",
        name="10mm Wrench",
        category=ToolCategory.HAND_TOOL,
        size=10.0,
        size_unit="mm",
        source_ref=source_ref,
    )
    tools = ExtractedToolSet(tools=(tool,))
    assert len(tools.tools) == 1

    # Torque
    torque = ExtractedTorque(
        torque_id="tq_1",
        fastener="M8 Bolt",
        nominal_value=25.0,
        unit=TorqueUnit.NM,
        source_ref=source_ref,
    )
    torques = ExtractedTorqueSet(torques=(torque,))
    assert len(torques.torques) == 1

    # Part Number
    part = ExtractedPartNumber(
        part_number_id="pn_1",
        part_number="90919-01191",
        description="Spark Plug",
        source_ref=source_ref,
    )
    parts = ExtractedPartNumberSet(part_numbers=(part,))
    assert len(parts.part_numbers) == 1

    # DTC
    dtc = ExtractedDiagnosticCode(
        code_id="dtc_1",
        code="P0300",
        description="Random Misfire",
        source_ref=source_ref,
    )
    codes = ExtractedDiagnosticCodeSet(codes=(dtc,))
    assert len(codes.codes) == 1


# ---------------------------------------------------------------------------
# Generation & Pipeline Aggregate Tests (Stages 13-16)
# ---------------------------------------------------------------------------


def test_stage13_to_stage16_and_aggregates() -> None:
    """Verify knowledge generation contracts and aggregate pipeline outputs."""
    source_ref = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE)

    # Stage 13: Metadata
    meta = DocumentMetadata(
        make="Toyota",
        model="Supra",
        year_start=1993,
        year_end=1998,
        document_type=DocumentType.WORKSHOP_MANUAL,
        page_count=500,
        title="1993 Toyota Supra RM",
        source_ref=source_ref,
    )
    assert meta.make == "Toyota"

    # Stage 14: Graph
    node1 = GraphNode(
        node_id="n_toyota",
        node_type=NodeType.VEHICLE,
        label="Toyota Supra",
        source_ref=source_ref,
    )
    node2 = GraphNode(
        node_id="n_engine",
        node_type=NodeType.ENGINE,
        label="2JZ-GTE",
        source_ref=source_ref,
    )
    edge = GraphEdge(
        edge_id="e_1",
        source_id="n_toyota",
        target_id="n_engine",
        edge_type=EdgeType.APPLIES_TO,
        source_ref=source_ref,
    )
    graph = KnowledgeGraphModel(nodes=(node1, node2), edges=(edge,))
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

    # Stage 15: Chunker
    chunk = SemanticChunk(
        chunk_id="chk_1",
        text="Detailed procedure text",
        heading_path=("Brakes", "Discs"),
        page_number=12,
        source_ref=source_ref,
    )
    chunks = SemanticChunkSet(chunks=(chunk,))
    assert len(chunks.chunks) == 1

    # Stage 16: Embeddings
    embedding = ChunkEmbedding(
        chunk_id="chk_1",
        vector=(0.123, -0.456, 0.789),
        model="text-embedding-3-small",
        dimension=3,
    )
    embeddings = EmbeddingSet(embeddings=(embedding,))
    assert len(embeddings.embeddings) == 1

    # Stage Outputs Aggregation
    word = ParsedWord(text="Test", left=0.0, top=0.0, right=10.0, bottom=10.0)
    parsed_doc = ParsedDocument(pages=(ParsedPage(page_number=1, words=(word,)),))
    layout_doc = LayoutDocument(elements=())
    toc = TableOfContents(entries=(), detected=False)
    heading_tree = HeadingTree(roots=(), nodes=())
    stage_outputs = PipelineStageOutputs(
        parsed_document=parsed_doc,
        layout_document=layout_doc,
        toc=toc,
        heading_tree=heading_tree,
        procedures=ExtractedProcedureSet(procedures=()),
        tables=ExtractedTableSet(tables=()),
        figures=ExtractedFigureSet(figures=()),
        warnings=ExtractedWarningSet(warnings=()),
        tools=ExtractedToolSet(tools=()),
        torques=ExtractedTorqueSet(torques=()),
        part_numbers=ExtractedPartNumberSet(part_numbers=()),
        diagnostic_codes=ExtractedDiagnosticCodeSet(codes=()),
    )
    assert stage_outputs.parsed_document.total_pages == 1

    # Final Pipeline Result
    result = PipelineResult(
        metadata=meta,
        graph=graph,
        chunks=chunks,
        embeddings=embeddings,
        source_path="/path/to/manual.pdf",
    )
    assert result.metadata.make == "Toyota"

    # Serialization round-trip
    dumped = result.model_dump_json()
    reloaded = PipelineResult.model_validate_json(dumped)
    assert reloaded == result


# ---------------------------------------------------------------------------
# Protocol Compliance Tests
# ---------------------------------------------------------------------------


def test_stage_protocols_runtime_checkable() -> None:
    """Verify all 16 stage protocols are runtime checkable."""

    # Stage 1: Parser
    class DummyParser:
        def parse(self, source: str | Path | bytes) -> ParsedDocument:
            return ParsedDocument(pages=())

    assert isinstance(DummyParser(), PdfParserProtocol)

    # Stage 2: Layout
    class DummyDetector:
        def detect(self, document: ParsedDocument) -> LayoutDocument:
            return LayoutDocument(elements=())

    assert isinstance(DummyDetector(), LayoutDetectorProtocol)

    # Stage 3: TOC
    class DummyTocExtractor:
        def extract(self, document: LayoutDocument) -> TableOfContents:
            return TableOfContents(entries=(), detected=False)

    assert isinstance(DummyTocExtractor(), TocExtractorProtocol)

    # Stage 4: Heading Hierarchy
    class DummyHeadingHierarchy:
        def build(self, document: LayoutDocument, toc: TableOfContents) -> HeadingTree:
            return HeadingTree(roots=(), nodes=())

    assert isinstance(DummyHeadingHierarchy(), HeadingHierarchyBuilderProtocol)

    # Stage 5: Procedure Detector
    class DummyProcedureDetector:
        def detect(self, headings: HeadingTree, document: LayoutDocument) -> ExtractedProcedureSet:
            return ExtractedProcedureSet(procedures=())

    assert isinstance(DummyProcedureDetector(), ProcedureDetectorProtocol)

    # Stage 6: Table Extractor
    class DummyTableExtractor:
        def extract(self, document: LayoutDocument) -> ExtractedTableSet:
            return ExtractedTableSet(tables=())

    assert isinstance(DummyTableExtractor(), TableExtractorProtocol)

    # Stage 7: Figure Extractor
    class DummyFigureExtractor:
        def extract(self, document: LayoutDocument) -> ExtractedFigureSet:
            return ExtractedFigureSet(figures=())

    assert isinstance(DummyFigureExtractor(), FigureExtractorProtocol)

    # Stage 8: Warning Detector
    class DummyWarningDetector:
        def detect(self, document: LayoutDocument, headings: HeadingTree) -> ExtractedWarningSet:
            return ExtractedWarningSet(warnings=())

    assert isinstance(DummyWarningDetector(), WarningDetectorProtocol)

    # Stage 9: Tool Extractor
    class DummyToolExtractor:
        def extract(
            self, procedures: ExtractedProcedureSet, document: LayoutDocument
        ) -> ExtractedToolSet:
            return ExtractedToolSet(tools=())

    assert isinstance(DummyToolExtractor(), ToolExtractorProtocol)

    # Stage 10: Torque Extractor
    class DummyTorqueExtractor:
        def extract(
            self, procedures: ExtractedProcedureSet, document: LayoutDocument
        ) -> ExtractedTorqueSet:
            return ExtractedTorqueSet(torques=())

    assert isinstance(DummyTorqueExtractor(), TorqueExtractorProtocol)

    # Stage 11: Part Number Extractor
    class DummyPartNumberExtractor:
        def extract(
            self, procedures: ExtractedProcedureSet, document: LayoutDocument
        ) -> ExtractedPartNumberSet:
            return ExtractedPartNumberSet(part_numbers=())

    assert isinstance(DummyPartNumberExtractor(), PartNumberExtractorProtocol)

    # Stage 12: DTC Extractor
    class DummyDtcExtractor:
        def extract(
            self, document: LayoutDocument, procedures: ExtractedProcedureSet
        ) -> ExtractedDiagnosticCodeSet:
            return ExtractedDiagnosticCodeSet(codes=())

    assert isinstance(DummyDtcExtractor(), DiagnosticCodeExtractorProtocol)

    # Stage 13: Metadata Generator
    class DummyMetadataGenerator:
        def generate(self, inputs: PipelineStageOutputs) -> DocumentMetadata:
            return DocumentMetadata(
                page_count=1,
                source_ref=SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE),
            )

    assert isinstance(DummyMetadataGenerator(), MetadataGeneratorProtocol)

    # Stage 14: KG Generator
    class DummyGraphGenerator:
        def generate(self, inputs: PipelineStageOutputs) -> KnowledgeGraphModel:
            return KnowledgeGraphModel(nodes=(), edges=())

    assert isinstance(DummyGraphGenerator(), KnowledgeGraphGeneratorProtocol)

    # Stage 15: Chunker
    class DummyChunker:
        def chunk(
            self,
            document: ParsedDocument,
            headings: HeadingTree,
            procedures: ExtractedProcedureSet,
        ) -> SemanticChunkSet:
            return SemanticChunkSet(chunks=())

    assert isinstance(DummyChunker(), AgenticChunkerProtocol)

    # Stage 16: Embedding Generator
    class DummyEmbeddingGenerator:
        def embed(self, chunks: SemanticChunkSet) -> EmbeddingSet:
            return EmbeddingSet(embeddings=())

    assert isinstance(DummyEmbeddingGenerator(), EmbeddingGeneratorProtocol)

    # Provider & Pipeline
    class DummyEmbeddingProvider:
        def embed_text(self, text: str) -> list[float]:
            return [0.1, 0.2]

        def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
            return [[0.1, 0.2]]

    assert isinstance(DummyEmbeddingProvider(), EmbeddingProviderProtocol)

    class DummyPipeline:
        def run(self, source: str | Path | bytes) -> PipelineResult:
            ref = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE)
            return PipelineResult(
                metadata=DocumentMetadata(page_count=1, source_ref=ref),
                graph=KnowledgeGraphModel(nodes=(), edges=()),
                chunks=SemanticChunkSet(chunks=()),
                embeddings=EmbeddingSet(embeddings=()),
            )

    assert isinstance(DummyPipeline(), IngestionPipelineProtocol)
