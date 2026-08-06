# Ingestion Pipeline Implementation Plan

## Why This Document Exists

This document defines the **phased implementation plan** for the document ingestion pipeline. It describes the build order, dependencies between stages, testing strategy, and acceptance criteria.

The plan is organized into 4 phases, each building on the previous phase. Every phase produces independently testable, shippable code.

## Build Order Rationale

Stages are ordered by dependency:

1. **Foundation** must exist first: data models, interfaces, exceptions, config, fixtures.
2. **Stage 1 (Scrubbing)** has no dependency on other stages and produces the input for all downstream stages.
3. **Stage 2 (Content Extraction)** depends on Stage 1 outputs.
4. **Stage 3 (Domain Extraction)** depends on Stage 2 outputs (especially procedures).
5. **Stage 4 (Knowledge Generation)** depends on all prior stages.

Within each phase, stages are built in dependency order (left to right in the pipeline diagram).

## Phase 0: Foundation

**Goal:** Establish the scaffolding: data models, interfaces, exceptions, config, test fixtures, and the pipeline orchestrator skeleton.

### Tasks

| Task | Files | Dependencies |
|------|-------|--------------|
| 0.1 Project scaffold | `pyproject.toml`, `src/mechai/__init__.py`, `src/mechai/common/` | None |
| 0.2 Data models | `src/mechai/ingestion/models.py` | 0.1 |
| 0.3 Interfaces | `src/mechai/ingestion/interfaces.py` | 0.2 |
| 0.4 Exceptions | `src/mechai/ingestion/exceptions.py` | 0.1 |
| 0.5 Common | `src/mechai/common/config.py`, `logging.py`, `llm.py` | 0.1 |
| 0.6 Test fixtures | `tests/fixtures/generated/` factories | 0.2 |
| 0.7 Pipeline skeleton | `src/mechai/ingestion/pipeline.py` (empty orchestrator) | 0.2, 0.3, 0.4 |

### Tests

| Test | What it verifies |
|------|------------------|
| `test_models.py` | All models construct with valid data, reject invalid data |
| `test_exceptions.py` | Exception hierarchy is correct |
| `test_pipeline.py` | Pipeline skeleton accepts stages and runs empty flow |

### Acceptance Criteria

- [ ] All data models are defined and validated
- [ ] All interfaces are defined as Protocols
- [ ] Exception hierarchy is complete
- [ ] Config module loads from environment variables
- [ ] Test fixtures can construct synthetic data
- [ ] Pipeline skeleton composes stages

## Phase 1: Document Scrubbing

**Goal:** Parse a PDF into a structured document with layout regions, TOC, and heading hierarchy.

### Tasks

| Task | Files | Dependencies |
|------|-------|--------------|
| 1.1 PDF Parser | `src/mechai/ingestion/scrubbing/pdf_parser.py` | 0.2, 0.3, 0.4 |
| 1.2 Layout Detector | `src/mechai/ingestion/scrubbing/layout_detector.py` | 1.1 |
| 1.3 TOC Extractor | `src/mechai/ingestion/scrubbing/toc_extractor.py` | 1.2 |
| 1.4 Heading Hierarchy | `src/mechai/ingestion/scrubbing/heading_hierarchy.py` | 1.2, 1.3 |

### Tests

| Test | What it verifies |
|------|------------------|
| `test_pdf_parser.py` | Extracts text, words, coordinates, images from synthetic PDF |
| `test_layout_detector.py` | Classifies regions correctly (heading, paragraph, table, figure) |
| `test_toc_extractor.py` | Extracts TOC entries from synthetic TOC pages |
| `test_heading_hierarchy.py` | Builds correct tree from headings + TOC cross-reference |

### Acceptance Criteria

- [ ] PDF parser handles text, images, and positional data
- [ ] Layout detector correctly classifies known layout types on synthetic PDFs
- [ ] TOC extractor handles dotted-leader TOC, absent TOC, and malformed TOC
- [ ] Heading hierarchy resolves levels correctly with and without TOC
- [ ] All stages are independently testable with synthetic PDFs
- [ ] All stages are wired into the pipeline orchestrator

## Phase 2: Content Extraction

**Goal:** Detect procedures, tables, figures, and warnings from the structured document.

### Tasks

| Task | Files | Dependencies |
|------|-------|--------------|
| 2.1 Procedure Detector | `src/mechai/ingestion/content/procedure_detector.py` | 1.2, 1.4 |
| 2.2 Table Extractor | `src/mechai/ingestion/content/table_extractor.py` | 1.2 |
| 2.3 Figure Extractor | `src/mechai/ingestion/content/figure_extractor.py` | 1.2 |
| 2.4 Warning Detector | `src/mechai/ingestion/content/warning_detector.py` | 1.2, 1.4 |

### Tests

| Test | What it verifies |
|------|------------------|
| `test_procedure_detector.py` | Detects procedures with correct step sequences |
| `test_table_extractor.py` | Extracts tables with correct rows, columns, captions |
| `test_figure_extractor.py` | Extracts figures with captions and regions |
| `test_warning_detector.py` | Detects DANGER, WARNING, CAUTION, NOTE with correct severity |

### Acceptance Criteria

- [ ] Procedure detector identifies procedural headings and extracts step sequences
- [ ] Table extractor handles simple tables, merged cells, and missing captions
- [ ] Figure extractor detects embedded images and associates nearby captions
- [ ] Warning detector correctly classifies severity and associates with nearby content
- [ ] All stages are independently testable with synthetic data
- [ ] All stages are wired into the pipeline orchestrator

## Phase 3: Domain Extraction

**Goal:** Extract automotive-specific structured facts: tools, torque specs, part numbers, diagnostic codes.

### Tasks

| Task | Files | Dependencies |
|------|-------|--------------|
| 3.1 Tool Extractor | `src/mechai/ingestion/domain/tool_extractor.py` | 2.1, 1.2 |
| 3.2 Torque Extractor | `src/mechai/ingestion/domain/torque_extractor.py` | 2.1, 1.2 |
| 3.3 Part Number Extractor | `src/mechai/ingestion/domain/part_number_extractor.py` | 2.1, 1.2 |
| 3.4 Diagnostic Code Extractor | `src/mechai/ingestion/domain/diagnostic_code_extractor.py` | 1.2, 2.1 |

### Tests

| Test | What it verifies |
|------|------------------|
| `test_tool_extractor.py` | Extracts tools with sizes and units from procedure text |
| `test_torque_extractor.py` | Extracts torque specs with values and units |
| `test_part_number_extractor.py` | Extracts OEM part numbers from text |
| `test_diagnostic_code_extractor.py` | Extracts OBD-II codes with descriptions |

### Acceptance Criteria

- [ ] Tool extractor handles common tool patterns (sockets, wrenches, special tools)
- [ ] Torque extractor handles N·m, ft·lb, lb-ft, and angle torque specs
- [ ] Part number extractor handles OEM patterns (alphanumeric, hyphenated)
- [ ] Diagnostic code extractor handles P-, C-, B-, U- codes
- [ ] All extractions carry provenance (source page, region, method)
- [ ] All stages are independently testable with synthetic text
- [ ] All stages are wired into the pipeline orchestrator

## Phase 4: Knowledge Generation

**Goal:** Generate metadata, knowledge graph, agentic chunks, and embeddings.

### Tasks

| Task | Files | Dependencies |
|------|-------|--------------|
| 4.1 Metadata Generator | `src/mechai/ingestion/knowledge/metadata_generator.py` | 1.1, 2.1, 3.2, 3.3, 3.4 |
| 4.2 Knowledge Graph Generator | `src/mechai/ingestion/knowledge/knowledge_graph_generator.py` | 4.1, all prior |
| 4.3 Agentic Chunker | `src/mechai/ingestion/knowledge/agentic_chunker.py` | 1.1, 1.4, 2.1 |
| 4.4 Embedding Generator | `src/mechai/ingestion/knowledge/embedding_generator.py` | 4.3 |

### Tests

| Test | What it verifies |
|------|------------------|
| `test_metadata_generator.py` | Infers make, model, year, system from title page content |
| `test_knowledge_graph_generator.py` | Assembles correct nodes and edges from structured outputs |
| `test_agentic_chunker.py` | Generates chunks aligned to section boundaries, not split mid-procedure |
| `test_embedding_generator.py` | Generates vectors of correct dimension; in-memory provider is deterministic |

### Acceptance Criteria

- [ ] Metadata generator infers vehicle attributes from title page and headers
- [ ] Knowledge graph generator produces valid nodes and edges with provenance
- [ ] Agentic chunker produces chunks that respect heading and procedure boundaries
- [ ] Embedding generator works with in-memory provider (deterministic) and SentenceTransformer provider
- [ ] All stages are independently testable
- [ ] Full pipeline integration test passes: synthetic PDF → PipelineResult

## Integration Testing

### Pipeline Integration Test

```python
def test_full_pipeline_returns_pipeline_result():
    """End-to-end test: synthetic PDF through the full pipeline."""
    # Arrange
    pipeline = create_default_pipeline()
    pdf_path = FIXTURES_DIR / "pdfs" / "full_manual.pdf"

    # Act
    result = pipeline.run(pdf_path)

    # Assert
    assert isinstance(result, PipelineResult)
    assert result.metadata is not None
    assert len(result.graph.nodes) > 0
    assert len(result.chunks.chunks) > 0
    assert len(result.embeddings.embeddings) > 0
    assert result.embeddings.embeddings[0].dimension > 0
```

### Stage Isolation Tests

Each stage is tested in isolation by passing synthetic outputs from the previous stage. For example:

```python
def test_procedure_detector_works_in_isolation():
    """Test ProcedureDetector with synthetic LayoutDocument + HeadingTree."""
    # Arrange
    detector = ProcedureDetector()
    layout = create_synthetic_layout_with_procedures()
    headings = create_synthetic_headings()

    # Act
    result = detector.detect(headings, layout)

    # Assert
    assert len(result.procedures) > 0
    assert all(len(p.steps) > 0 for p in result.procedures)
```

## Dependency Graph

```mermaid
flowchart LR
    P0[Phase 0: Foundation] --> P1[Phase 1: Scrubbing]
    P1 --> P2[Phase 2: Content Extraction]
    P2 --> P3[Phase 3: Domain Extraction]
    P3 --> P4[Phase 4: Knowledge Generation]
```

## Testing Strategy

Per the [Testing Philosophy](../../engineering/05-testing-philosophy.md):

- **Unit tests:** Every stage is tested in isolation. Synthetic inputs produce expected outputs.
- **Integration tests:** Stage sequences are tested together (e.g., PDF Parser → Layout Detector → TOC Extractor).
- **E2E test:** Full pipeline runs on a synthetic PDF and produces a valid `PipelineResult`.
- **No real data:** All tests use programmatically generated synthetic data from `tests/fixtures/generated/`.
- **Deterministic tests:** Rule-based extraction tests are deterministic. LLM-assisted stages are tested with mock LLM providers.

## Estimated Effort

| Phase | Stages | Files | Estimated Effort |
|-------|--------|-------|------------------|
| Phase 0: Foundation | 0 | ~15 | 1 session |
| Phase 1: Scrubbing | 4 | 4 modules + 4 test files | 2-3 sessions |
| Phase 2: Content Extraction | 4 | 4 modules + 4 test files | 2-3 sessions |
| Phase 3: Domain Extraction | 4 | 4 modules + 4 test files | 2-3 sessions |
| Phase 4: Knowledge Generation | 4 | 4 modules + 4 test files | 2-3 sessions |
| **Total** | **16** | **~40 files** | **9-13 sessions** |

## How to Use This Document

1. **Starting a phase?** Read the tasks and acceptance criteria for that phase.
2. **Starting a stage?** Read the [Architecture](01-architecture.md), [Interfaces](03-interfaces.md), and [Data Models](04-data-models.md) for that stage.
3. **Running tests?** Each stage has a corresponding test file. Run `pytest tests/mechai/ingestion/` to run all.
4. **Reviewing progress?** Check acceptance criteria against the current state.

## Related Documents

- [Architecture](01-architecture.md) — the pipeline stages.
- [Interfaces](03-interfaces.md) — stage contracts.
- [Data Models](04-data-models.md) — the model definitions.
- [Folder Structure](02-folder-structure.md) — where files live.
- [Testing Philosophy](../../engineering/05-testing-philosophy.md) — how we test.
- [Engineering Handbook](../../engineering/01-engineering-handbook.md) — the core rules.