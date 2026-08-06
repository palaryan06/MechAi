# Open Questions

## Why This File Exists

This file tracks **open questions** for AI agents. It exists so that agents know what questions need resolution and can coordinate on research. It complements the [Open Questions](../docs/reference/03-open-questions.md) tracker with an agent-facing view.

## How to Use This File

- **Before starting research**, check if the question is already tracked.
- **When you resolve a question**, update its status and link the finding.
- **When you identify a new question**, add it here.

## Open Questions

### Q-001: What is the optimal knowledge graph schema?

- **Status:** Open
- **Why it matters:** Foundation of the knowledge graph (ADR-0001).
- **Where it's being addressed:** [Research: Knowledge Representation](../docs/research/02-knowledge-representation.md)

### Q-002: How do we extract the knowledge graph from documents?

- **Status:** Open
- **Why it matters:** Extraction is the hardest part of the graph approach.
- **Where it's being addressed:** [Research: Knowledge Representation](../docs/research/02-knowledge-representation.md)

### Q-003: How do we rank diagnostic hypotheses?

- **Status:** Open
- **Why it matters:** The product must present a ranked, evidence-backed diagnosis.
- **Where it's being addressed:** [Research: Knowledge Representation](../docs/research/02-knowledge-representation.md)

### Q-004: How do we normalize OBD-II data across protocols and vehicles?

- **Status:** Open
- **Why it matters:** OBD-II is a core evidence source.
- **Where it's being addressed:** [Research: OBD-II and Telemetry](../docs/research/03-obd-ii-and-telemetry.md)

### Q-005: How do we quantify uncertainty in a diagnosis?

- **Status:** Open
- **Why it matters:** The product philosophy requires honest uncertainty.
- **Where it's being addressed:** [Research: Evaluation and Benchmarks](../docs/research/04-evaluation-and-benchmarks.md)

### Q-006: Which vector store and graph database should we use?

- **Status:** Open
- **Why it matters:** Foundational dependencies.
- **Where it's being addressed:** Phase 1 research; will result in ADRs.

### Q-007: What data sources are available and licensed?

- **Status:** Open
- **Why it matters:** The product depends on automotive knowledge.
- **Where it's being addressed:** Related to risk R-002.

### Q-008: How do we build a reliable diagnostic benchmark?

- **Status:** Open
- **Why it matters:** Without evaluation, we can't measure progress.
- **Where it's being addressed:** [Research: Evaluation and Benchmarks](../docs/research/04-evaluation-and-benchmarks.md)

### Q-009: What is the right product surface for the first MVP?

- **Status:** Open
- **Why it matters:** The MVP must be focused and useful.
- **Where it's being addressed:** To be decided in Phase 2/3.

## Resolved Questions

*(None yet. When a question is resolved, move it here with a link to the finding.)*

## Status

- **Last updated:** 2026-08-03
- **Status:** Active