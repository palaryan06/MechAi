# Document Ingestion Pipeline — Design

## Why This Folder Exists

This folder contains the **design specification** for the MechAI document ingestion pipeline. The pipeline's sole responsibility is **turning an automotive workshop manual into structured knowledge**.

This is a design-only deliverable per the task requirement: *"Only after those are approved should implementation begin."*

## Scope

The pipeline transforms a raw workshop manual (PDF) into structured, provenance-carrying knowledge artifacts:

- Parsed pages and layout elements
- Table of contents and heading hierarchy
- Detected procedures, tables, figures, warnings
- Extracted tools, torque specs, part numbers, diagnostic codes
- Document metadata
- Knowledge graph triplets
- Agentic chunks and their embeddings

## Out of Scope

This pipeline **does not** build:
- Chat / conversational interfaces
- RAG retrieval systems
- LangGraph or agent orchestration frameworks
- Public REST APIs
- The reasoning engine

## Documents

| Document | Purpose |
|----------|---------|
| [01-architecture.md](01-architecture.md) | High-level pipeline architecture, stages, and data flow |
| [02-folder-structure.md](02-folder-structure.md) | Repository folder layout for the pipeline |
| [03-interfaces.md](03-interfaces.md) | Stage interfaces (Protocols) and contracts |
| [04-data-models.md](04-data-models.md) | Pydantic data models for all pipeline artifacts |
| [05-implementation-plan.md](05-implementation-plan.md) | Phased implementation plan with tests |

## How to Use This Folder

1. **Reviewing the design?** Read [01-architecture.md](01-architecture.md) first.
2. **Implementing a stage?** Read [03-interfaces.md](03-interfaces.md) and [04-data-models.md](04-data-models.md).
3. **Planning the build order?** Read [05-implementation-plan.md](05-implementation-plan.md).
4. **Approving the design?** Review all documents and signal approval before implementation begins.

## Related Documents

- [Architecture Overview](../01-architecture-overview.md) — where ingestion fits in the system.
- [Data Flows](../03-data-flows.md) — how data moves through the system.
- [Research: Knowledge Representation](../../research/02-knowledge-representation.md) — the knowledge graph foundation.
- [Coding Standards](../../engineering/03-coding-standards.md) — how the code will be written.
- [Naming Conventions](../../engineering/02-naming-conventions.md) — how things are named.
- [Testing Philosophy](../../engineering/05-testing-philosophy.md) — how stages are tested.