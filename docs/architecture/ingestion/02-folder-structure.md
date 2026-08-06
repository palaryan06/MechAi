# Ingestion Pipeline Folder Structure

## Why This Document Exists

This document defines the **repository folder structure** for the document ingestion pipeline. It shows where each stage's code lives, how tests mirror the source, and how the package is organized.

The structure follows the [Coding Standards](../../engineering/03-coding-standards.md) module layout and the [Repository Guide](../02-repository-guide.md) conventions.

## Source Layout

```
src/mechai/
├── common/                        # Shared helpers
│   ├── config.py                  # Centralized config
│   ├── logging.py                 # Structured logging
│   └── llm.py                     # LLM provider abstraction
└── ingestion/
    ├── pipeline.py                # IngestionPipeline orchestrator
    ├── exceptions.py              # IngestionError hierarchy
    ├── models.py                  # All Pydantic data models
    ├── interfaces.py              # Stage Protocol definitions
    ├── scrubbing/                 # Stage 1 (Document Scrubbing)
    │   ├── pdf_parser.py          # 1: PDF Parser
    │   ├── layout_detector.py     # 2: Layout Detector
    │   ├── toc_extractor.py       # 3: TOC Extractor
    │   └── heading_hierarchy.py   # 4: Heading Hierarchy Builder
    ├── content/                   # Stage 2 (Content Extraction)
    │   ├── procedure_detector.py  # 5: Procedure Detector
    │   ├── table_extractor.py     # 6: Table Extractor
    │   ├── figure_extractor.py    # 7: Figure Extractor
    │   └── warning_detector.py    # 8: Warning Detector
    ├── domain/                    # Stage 3 (Domain Extraction)
    │   ├── tool_extractor.py      # 9: Tool Extractor
    │   ├── torque_extractor.py    # 10: Torque Extractor
    │   ├── part_number_extractor.py  # 11: Part Number Extractor
    │   └── diagnostic_code_extractor.py  # 12: Diagnostic Code Extractor
    └── knowledge/                 # Stage 4 (Knowledge Generation)
        ├── metadata_generator.py  # 13: Metadata Generator
        ├── knowledge_graph_generator.py  # 14: KG Generator
        ├── agentic_chunker.py     # 15: Agentic Chunker
        └── embedding_generator.py # 16: Embedding Generator
```

## Test Layout

Tests mirror the source structure under `tests/`:

```
tests/mechai/ingestion/
├── test_pipeline.py
├── test_exceptions.py
├── scrubbing/
│   ├── test_pdf_parser.py
│   ├── test_layout_detector.py
│   ├── test_toc_extractor.py
│   └── test_heading_hierarchy.py
├── content/
│   ├── test_procedure_detector.py
│   ├── test_table_extractor.py
│   ├── test_figure_extractor.py
│   └── test_warning_detector.py
├── domain/
│   ├── test_tool_extractor.py
│   ├── test_torque_extractor.py
│   ├── test_part_number_extractor.py
│   └── test_diagnostic_code_extractor.py
└── knowledge/
    ├── test_metadata_generator.py
    ├── test_knowledge_graph_generator.py
    ├── test_agentic_chunker.py
    └── test_embedding_generator.py
```

## Test Fixtures

Synthetic test fixtures live under `tests/fixtures/`:

```
tests/fixtures/
├── pdfs/                    # Synthetic PDFs (generated)
│   ├── simple_manual.pdf
│   ├── toc_manual.pdf
│   ├── tables_manual.pdf
│   ├── figures_manual.pdf
│   ├── warnings_manual.pdf
│   └── full_manual.pdf
├── texts/                   # Plain-text fixtures for rule extractors
│   ├── procedures.txt
│   ├── torque_specs.txt
│   ├── part_numbers.txt
│   ├── dtc_codes.txt
│   └── warnings.txt
└── generated/               # Programmatic fixtures (factories)
    ├── pdf_factory.py
    ├── text_factory.py
    └── graph_factory.py
```

## Configuration

Configuration follows the [Configuration Philosophy](../../engineering/06-configuration-philosophy.md):

```
# Ingestion
MECHAI_INGESTION_EMBEDDING_PROVIDER=in_memory   # in_memory | sentence_transformers
MECHAI_INGESTION_EMBEDDING_MODEL=all-MiniLM-L6-v2
MECHAI_INGESTION_CHUNK_MAX_TOKENS=512
MECHAI_INGESTION_CHUNK_OVERLAP_TOKENS=32
```

## Naming Conventions Applied

| Item | Convention | Example |
|------|-----------|---------|
| Python module | `snake_case.py` | `tool_extractor.py` |
| Python package | `snake_case` | `ingestion/`, `scrubbing/` |
| Test file | `test_<module>.py` | `test_tool_extractor.py` |
| Test function | `test_<behavior>` | `test_extracts_10mm_socket()` |
| Env var | `MECHAI_` + `UPPER_SNAKE_CASE` | `MECHAI_INGESTION_EMBEDDING_PROVIDER` |

## Why This Structure

1. **Mirrors pipeline stages.** Each stage maps to a module in the corresponding layer folder.
2. **Tests mirror source.** Per the [Testing Philosophy](../../engineering/05-testing-philosophy.md).
3. **Fixtures centralized.** Shared synthetic data in `tests/fixtures/`.
4. **Common utilities separate.** `common/` holds config, logging, LLM abstraction.
5. **Scalable.** New stages slot into layer folders without reorganizing.

## How to Use This Document

1. **Adding a new stage?** Create a module in the appropriate layer folder.
2. **Looking for stage code?** Find the module by stage number.
3. **Adding fixtures?** Put synthetic data in `tests/fixtures/`.

## Related Documents

- [Architecture](01-architecture.md) — the pipeline stages.
- [Interfaces](03-interfaces.md) — stage contracts.
- [Data Models](04-data-models.md) — Pydantic models.
- [Coding Standards](../../engineering/03-coding-standards.md) — module layout.
- [Repository Guide](../02-repository-guide.md) — repository conventions.
- [Naming Conventions](../../engineering/02-naming-conventions.md) — naming rules.