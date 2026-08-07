# ADR Index

## Why This Document Exists

This is the **table of contents** for all Architectural Decision Records (ADRs) in MechAI. It exists so anyone can see at a glance what decisions have been made, their status, and when. Use this to search for prior decisions before making new ones.

## Understanding Status

- **Proposed:** Under review, not yet adopted.
- **Accepted:** Adopted and implemented.
- **Replaced:** Replaced by a newer ADR.
- **Superseded:** No longer current.

## Current ADRs

| ADR | Title | Status | Date | Summary |
|-----|-------|--------|------|---------|
| 0001 | [Knowledge Graph as Reasoning Core](0001-knowledge-graph-core.md) | Proposed | 2026-08-03 | Adopt a knowledge graph as the primary reasoning substrate, with vector retrieval as a complement. |
| 0002 | [Python as Primary Language](0002-python-primary-language.md) | Proposed | 2026-08-03 | Adopt Python as the primary implementation language. |
| 0003 | [Documentation as Code](0003-documentation-as-code.md) | Accepted | 2026-08-03 | Documentation is a first-class artifact, reviewed like code. |
| 0004 | [Agent Memory System](0004-agent-memory-system.md) | Accepted | 2026-08-03 | Commit a shared memory system for AI agents to persist context. |
| 0006 | [Separation of Document Intelligence from Domain Extraction](0006-document-intelligence-separation.md) | Accepted | 2026-08-07 | Decouple physical document layout intelligence from semantic domain extraction. |
| 0007 | [Canonical Intermediate Representation (CIR) Schema](0007-canonical-intermediate-representation.md) | Accepted | 2026-08-07 | Define immutable, universal document representation schema for all ingestion stages. |
| 0008 | [2D Spatial Reading-Order Graph (DAG)](0008-2d-spatial-reading-order-dag.md) | Accepted | 2026-08-07 | Model reading order as a DAG resolved via recursive XY-cut whitespace projection. |

> **Note:** ADR 0001 and 0002 are *proposed* — they are working hypotheses that will be validated through research and prototyping before being accepted. The architecture documents reference them as planned decisions. When research resolves them, these ADRs will be updated to **Accepted**.

## History of Changes

This index is updated whenever an ADR is added, accepted, superseded, or replaced.

| Date | Change |
|------|--------|
| 2026-08-03 | Initial ADR index created with ADRs 0001-0004. |
| 2026-08-07 | Added ADRs 0006-0008 establishing Document Intelligence Layer and CIR architecture. |

## How to Use This Document

1. **Before a significant decision**, search this index to see if the question is already answered.
2. **After writing an ADR**, add it to this index.
3. **When an ADR status changes**, update this index.

## Related Documents

- [ADR README](README.md) — how the ADR system works.
- [template.md](template.md) — the ADR template.