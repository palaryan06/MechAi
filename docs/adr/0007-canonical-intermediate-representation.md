# ADR-0007: Canonical Intermediate Representation (CIR) Schema

- **Status:** Accepted
- **Date:** 2026-08-07
- **Author:** Chief Document Intelligence Architect

## Context

Different PDF extraction backends (PyMuPDF, Docling, pdfplumber, OCR engines) produce incompatible coordinate systems, data models, and metadata representations. Downstream stages require a unified, strongly typed, immutable contract that preserves physical geometry, typography, reading order, and hierarchical containment with unbroken sub-pixel provenance.

## Decision

We establish the **Canonical Intermediate Representation (CIR)** (`DocumentCIR`) as the universal data contract across the MechAI ingestion pipeline. All CIR data structures:
1. Are defined using Pydantic v2 with `frozen=True` and strict typing (`extra="forbid"`).
2. Carry immutable `SourceRef` provenance anchoring to 1-based page numbers, sub-pixel `BoundingBox` coordinates, extraction methods, and calibrated epistemic confidence scores ($c \in [0.0, 1.0]$).
3. Strictly model physical and structural primitives (`PageCIR`, `RegionCIR`, `TableCIR`, `TableCellCIR`, `FigureCIR`, `CalloutAnchorCIR`, `AdmonitionCIR`, `OutlineNodeCIR`, `ReadingOrderDAG`).

## Consequences

### Positive Consequences
- **Backend Portability**: Parser engines can be swapped or hybridized (e.g. PyMuPDF for text/tables, Docling for complex models) without modifying downstream extraction logic.
- **Auditable Provenance**: Every extracted fact in the knowledge graph can trace its exact physical bounding box coordinates on the source PDF.
- **Type Safety**: Full IDE autocompletion, runtime validation, and static type checking via MyPy.

### Negative Consequences
- Memory overhead for maintaining detailed token and glyph-level provenance trees across large multi-thousand page documents.

## References

- [RFC-006: Canonical Intermediate Representation](file:///c:/Users/palar/PycharmProjects/MechAi/docs/architecture/rfc/RFC-006-document-intelligence-layer.md)
- [PR-002: Domain Entities & Contracts](file:///c:/Users/palar/PycharmProjects/MechAi/src/mechai/contracts/)
