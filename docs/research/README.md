# Research Documentation

## Why This Folder Exists

This folder contains **MechAI's research documentation**. MechAI's core value is *reasoning over automotive knowledge* — not just retrieving it. That is a research problem as much as an engineering one. This folder is where we explore, document, and track the hard open questions.

Research is the bridge between the product vision (what we want) and the architecture (how we build it). It answers: *What do we need to understand before we can build this?*

## Documents in This Folder

| Document | Purpose |
|----------|---------|
| [`01-research-overview.md`](01-research-overview.md) | How we conduct and document research. |
| [`02-knowledge-representation.md`](02-knowledge-representation.md) | The core research question: how to represent automotive knowledge for reasoning. |
| [`03-obd-ii-and-telemetry.md`](03-obd-ii-and-telemetry.md) | OBD-II data: what it is, what it tells us, and the challenges. |
| [`04-evaluation-and-benchmarks.md`](04-evaluation-and-benchmarks.md) | How we measure whether MechAI actually reasons correctly. |

## How Research Works

Research in MechAI follows a cycle:

```
Ask a question → Research → Prototype → Evaluate → Document → Decide (ADR)
```

### 1. Ask a Question

Research starts with a **specific, answerable question**. Examples:

- "How do we represent causal relationships between vehicle components for reasoning?"
- "What is the best way to build a knowledge graph from workshop manuals?"
- "How do we quantify uncertainty in a diagnostic recommendation?"

Questions are tracked in the [Open Questions](../reference/03-open-questions.md) doc and in the research docs.

### 2. Research & Prototype

- **Research** involves reading, comparing approaches, and thinking.
- **Prototyping** happens in [`experiments/`](../../experiments/) — throwaway code to test an approach.
- Both are documented here (findings) and in experiments (code).

### 3. Evaluate

- How do we know approach A is better than approach B?
- We measure: accuracy, latency, cost, explainability, maintainability.
- See [Evaluation & Benchmarks](04-evaluation-and-benchmarks.md).

### 4. Document

- Findings are documented with sources, evidence, and open questions.
- Keep it factual: what was tested, what was found, what remains unknown.

### 5. Decide (ADR)

- When a research question is resolved, the decision is recorded as an [ADR](../adr/README.md).
- The ADR captures the *why*; the research doc captures the *exploration*.

## Research vs Experiments

| | Research docs | Experiments |
|---|---|---|
| Location | `docs/research/` | `experiments/` |
| Content | Findings, reasoning, references | Code, data, scratch work |
| Lifetime | Long-lived (a living record) | Short-lived (may be deleted) |
| Purpose | Explain *what we know and why* | Test *does this work* |

Research docs are curated and durable. Experiments are fast and throwaway. Both matter.

## Prioritizing Research

Research priorities come from:

- The [Roadmap](../roadmap/README.md) — what we need to build next.
- The [Open Questions](../reference/03-open-questions.md) — what we don't know.
- The [Product Philosophy](../03-product-philosophy.md) — what the product demands.

A research topic is worth pursuing if it advances a current roadmap item or unblocks a critical decision.

## How to Use This Folder

1. **Starting a research topic?** Read the [Research Overview](01-research-overview.md) and create a research doc.
2. **Prototyping?** Put code in `experiments/`, findings in the research doc.
3. **Reviewing research?** Check that findings are factual, sourced, and honest about uncertainty.
4. **Making a decision?** Record it as an ADR and link back to the research.

## Related Documents

- [Experiment Conventions](../../experiments/README.md) — how to run experiments.
- [ADR System](../adr/README.md) — how decisions are recorded.
- [Open Questions](../reference/03-open-questions.md) — the open questions tracker.
- [Vision](../01-vision.md) — why we're researching this.