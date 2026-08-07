# ADR-0006: Separation of Document Intelligence from Domain Extraction

- **Status:** Accepted
- **Date:** 2026-08-07
- **Author:** Chief Document Intelligence Architect

## Context

Prior ingestion architectures attempted to extract domain facts (torque specs, part numbers, diagnostic trouble codes) directly from linearized raw PDF token streams. Analysis of real production workshop manuals (RFC-005 Gap Analysis) demonstrated that raw PDF streams suffer from multi-column text interleaving, unbordered table destruction, running header contamination, corrupted legacy symbol fonts, and detached diagram callouts. Attempting domain extraction on raw tokens causes severe accuracy degradation and cascades structural errors into downstream knowledge graph generation.

## Decision

We decouple the ingestion pipeline into two distinct, independently testable architectural layers:
1. **The Document Intelligence Layer (Stages 1.5–4.5)**: Focuses exclusively on layout, physical geometry, typography, reading order DAGs, table cell matrices, section outlines, and callout anchor linking. It is strictly domain-agnostic and contains zero automotive semantics.
2. **Domain & Knowledge Extraction Layer (Stages 5–16)**: Consumes the structured, domain-agnostic Canonical Intermediate Representation (CIR) produced by the Document Intelligence Layer to perform automotive entity and knowledge graph extraction.

## Consequences

### Positive Consequences
- **Modular Testability**: Document layout, table reconstruction, and reading order can be benchmarked on synthetic and golden documents without requiring automotive domain knowledge or models.
- **Cross-Domain Reusability**: The Document Intelligence Layer and CIR can process technical manuals from aviation, marine, heavy machinery, or consumer electronics with zero code modifications.
- **Clean Invariant Enforcement**: Downstream domain extractors operate on guaranteed clean, dehyphenated, correctly ordered text blocks and structured 2D table matrices.

### Negative Consequences
- Introduces an intermediate representation stage and additional contract serialization overhead.

## Alternatives Considered

### Alternative 1: Monolithic End-to-End Extraction Pipeline
- Single-pass extractors running regexes and LLM prompts directly over raw PDF pages.
- **Why Rejected**: Linearized multi-column text and destroyed table grids cause catastrophic hallucination and miss critical specifications.

## References

- [RFC-006: Document Intelligence Layer](file:///c:/Users/palar/PycharmProjects/MechAi/docs/architecture/rfc/RFC-006-document-intelligence-layer.md)
- [RFC-005: Gap Analysis Report](file:///c:/Users/palar/PycharmProjects/MechAi/docs/architecture/rfc/RFC-005-gap-analysis.md)
