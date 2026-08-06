# Known Unknowns

## Why This Document Exists

This document records the **things we don't know yet** that could affect MechAI's direction. It exists so that unknowns are explicit, tracked, and eventually resolved through research and experimentation.

A "known unknown" is a question we know we need to answer. Resolving these is the work of the research phase. When an unknown is resolved, it moves to a finding (research doc) and possibly an ADR.

## How Unknowns Are Recorded

Each unknown has:

- **Question:** What we don't know.
- **Why it matters:** How it affects the direction.
- **Status:** Open | In Research | Resolved
- **Where it's being addressed:** The research doc or experiment.

## Current Known Unknowns

### U-001: What Is the Optimal Knowledge Graph Schema?

- **Question:** What entity types, relationship types, and properties best represent automotive knowledge for causal reasoning?
- **Why it matters:** This is the foundation of the knowledge graph (ADR-0001). Getting it wrong means rework.
- **Status:** Open
- **Where:** [Research: Knowledge Representation](../research/02-knowledge-representation.md)

### U-002: How Do We Extract the Knowledge Graph From Documents?

- **Question:** What is the best approach (LLM-based, deterministic, hybrid) to extract entities and relationships from workshop manuals and TSBs?
- **Why it matters:** Extraction is the hardest and most error-prone part of the graph approach.
- **Status:** Open
- **Where:** [Research: Knowledge Representation](../research/02-knowledge-representation.md)

### U-003: How Do We Rank Diagnostic Hypotheses?

- **Question:** Given evidence (symptoms, DTCs, sensor data), how do we rank the most likely causes?
- **Why it matters:** The product must present a ranked, evidence-backed diagnosis.
- **Status:** Open
- **Where:** [Research: Knowledge Representation](../research/02-knowledge-representation.md)

### U-004: How Do We Normalize OBD-II Data Across Protocols and Vehicles?

- **Question:** How do we robustly parse and normalize OBD-II data across the many protocols, PIDs, and vehicle variations?
- **Why it matters:** OBD-II is a core evidence source.
- **Status:** Open
- **Where:** [Research: OBD-II and Telemetry](../research/03-obd-ii-and-telemetry.md)

### U-005: How Do We Quantify Uncertainty in a Diagnosis?

- **Question:** How do we express confidence and uncertainty in a way that is calibrated and useful to the user?
- **Why it matters:** The product philosophy requires honest uncertainty.
- **Status:** Open
- **Where:** [Research: Evaluation and Benchmarks](../research/04-evaluation-and-benchmarks.md)

### U-006: What Is the Best Vector Store / Graph Database?

- **Question:** Which specific vector store and graph database technologies best fit our needs?
- **Why it matters:** These are foundational dependencies.
- **Status:** Open
- **Where:** To be researched in Phase 1; will result in ADRs.

### U-007: What Data Sources Are Available and Licensed?

- **Question:** What workshop manuals, TSBs, and other knowledge sources can we access, and under what licensing terms?
- **Why it matters:** The product depends on automotive knowledge.
- **Status:** Open
- **Where:** Related to risk R-002.

### U-008: How Do We Build a Reliable Diagnostic Benchmark?

- **Question:** How do we construct a held-out benchmark with vetted ground truth that measures reasoning quality?
- **Why it matters:** Without evaluation, we can't measure progress.
- **Status:** Open
- **Where:** [Research: Evaluation and Benchmarks](../research/04-evaluation-and-benchmarks.md)

### U-009: What Is the Right Product Surface for the First MVP?

- **Question:** What is the best first product experience (web, API, mobile) and which vehicle systems to focus on?
- **Why it matters:** The MVP must be focused and useful.
- **Status:** Open
- **Where:** To be decided in Phase 2/3.

## How to Use This Document

1. **Before starting research**, check if the question is already tracked here.
2. **When you resolve an unknown**, update its status and link the finding.
3. **When you identify a new unknown**, add it here.

## Related Documents

- [Risk Register](01-risk-register.md) — the risks.
- [Known Assumptions](02-known-assumptions.md) — what we assume.
- [Research](../research/README.md) — where unknowns are resolved.
- [Open Questions](../reference/03-open-questions.md) — the agent-facing open questions tracker.