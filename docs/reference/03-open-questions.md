# Open Questions

## Why This Document Exists

This is the **agent-facing open questions tracker**. It exists so that AI agents and humans can see, at a glance, what questions are open and need resolution. It complements the [Known Unknowns](../risk/03-known-unknowns.md) (project-level) with a more operational, agent-friendly tracker.

## How to Use This Document

- **Before starting research**, check if the question is already tracked.
- **When you resolve a question**, update its status and link the finding.
- **When you identify a new question**, add it here.

## Open Questions

### Q-001: What is the optimal knowledge graph schema?

- **Status:** Open
- **Why it matters:** Foundation of the knowledge graph (ADR-0001).
- **Where it's being addressed:** [Research: Knowledge Representation](../research/02-knowledge-representation.md)
- **Related unknown:** U-001

### Q-002: How do we extract the knowledge graph from documents?

- **Status:** Open
- **Why it matters:** Extraction is the hardest part of the graph approach.
- **Where it's being addressed:** [Research: Knowledge Representation](../research/02-knowledge-representation.md)
- **Related unknown:** U-002

### Q-003: How do we rank diagnostic hypotheses?

- **Status:** Open
- **Why it matters:** The product must present a ranked, evidence-backed diagnosis.
- **Where it's being addressed:** [Research: Knowledge Representation](../research/02-knowledge-representation.md)
- **Related unknown:** U-003

### Q-004: How do we normalize OBD-II data across protocols and vehicles?

- **Status:** Open
- **Why it matters:** OBD-II is a core evidence source.
- **Where it's being addressed:** [Research: OBD-II and Telemetry](../research/03-obd-ii-and-telemetry.md)
- **Related unknown:** U-004

### Q-005: How do we quantify uncertainty in a diagnosis?

- **Status:** Open
- **Why it matters:** The product philosophy requires honest uncertainty.
- **Where it's being addressed:** [Research: Evaluation and Benchmarks](../research/04-evaluation-and-benchmarks.md)
- **Related unknown:** U-005

### Q-006: Which vector store and graph database should we use?

- **Status:** Open
- **Why it matters:** Foundational dependencies.
- **Where it's being addressed:** Phase 1 research; will result in ADRs.
- **Related unknown:** U-006

### Q-007: What data sources are available and licensed?

- **Status:** Open
- **Why it matters:** The product depends on automotive knowledge.
- **Where it's being addressed:** Related to risk R-002.
- **Related unknown:** U-007

### Q-008: How do we build a reliable diagnostic benchmark?

- **Status:** Open
- **Why it matters:** Without evaluation, we can't measure progress.
- **Where it's being addressed:** [Research: Evaluation and Benchmarks](../research/04-evaluation-and-benchmarks.md)
- **Related unknown:** U-008

### Q-009: What is the right product surface for the first MVP?

- **Status:** Open
- **Why it matters:** The MVP must be focused and useful.
- **Where it's being addressed:** To be decided in Phase 2/3.
- **Related unknown:** U-009

## Resolved Questions

*(None yet. When a question is resolved, move it here with a link to the finding.)*

## How to Add a Question

When adding a question:

1. Give it a unique ID (Q-XXX).
2. State the question clearly.
3. Explain why it matters.
4. Link to where it's being addressed (if known).

## Related Documents

- [Known Unknowns](../risk/03-known-unknowns.md) — the project-level tracker.
- [Research](../research/README.md) — where questions are resolved.
- [Project Glossary](01-project-glossary.md) — shared vocabulary.