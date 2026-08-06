# Research Overview

## Why This Document Exists

This document defines **how we conduct research** at MechAI. It exists because the hardest problems we face — representing automotive knowledge, enabling causal reasoning, and grounding AI answers in evidence — are research problems that require disciplined exploration.

This is the "how" of research. The "what" lives in the topic-specific research docs.

## The Research Principles

1. **Questions before answers.** Research starts with a specific, answerable question, not a vague topic.
2. **Evidence over enthusiasm.** We prefer a small, boring, correct step over an exciting, unproven leap.
3. **Prototype to learn.** We run small experiments to test hypotheses before committing to a design.
4. **Document honestly.** We record what we learned, what we tried, and what remains unknown. We don't hide failures.
5. **Ground in the product.** Research serves the product vision, not the other way around.

## The Research Loop

```
Ask → Research → Prototype → Evaluate → Document → Decide
```

### 1. Ask

A good research question is:

- **Specific:** "How do we represent the relationship between an alternator and a battery?" not "How do we do knowledge graphs?"
- **Answerable:** There's a way to know if we've answered it.
- **Product-relevant:** It advances the roadmap or unblocks a decision.

Write the question in the relevant research doc and in the [Open Questions](../reference/03-open-questions.md) tracker.

### 2. Research

- **Read:** papers, docs, open-source code, competitor analysis.
- **Compare:** approaches, their trade-offs, their fit for our constraints.
- **Note:** sources, so findings are traceable.

### 3. Prototype

- Build a small, throwaway prototype in [`experiments/`](../../experiments/).
- Prototype the *riskiest assumption* first.
- Keep it fast. Prototypes are for learning, not production.

### 4. Evaluate

- Define success metrics before running the experiment.
- Measure: accuracy, latency, cost, complexity, maintainability.
- Compare against a baseline where possible.
- Be honest about what the prototype did and didn't show.

### 5. Document

- Write findings in the relevant research doc.
- Be factual: what was tested, what was found, what remains.
- Note open questions.

### 6. Decide

- When research resolves a question, record the decision as an [ADR](../adr/README.md).
- The ADR captures the *decision and why*; the research doc captures the *exploration*.

## Research Outputs

| Output | Where | When |
|--------|-------|------|
| Research question | Research doc + [Open Questions](../reference/03-open-questions.md) | At the start |
| Prototype | [`experiments/`](../../experiments/) | During exploration |
| Findings | Research doc | After evaluation |
| Decision | [ADR](../adr/README.md) | When resolved |

## Research Review

Good research is reviewed like code:

- **Is the question specific?** If not, it's not ready.
- **Is the evidence real?** Sources cited, measurements recorded.
- **Is the thinking honest?** Failures and limitations are acknowledged.
- **Is it product-relevant?** It serves the roadmap.

## How to Use This Document

1. **Starting research?** Follow the research loop.
2. **Prototyping?** Use `experiments/` and document findings in research docs.
3. **Reviewing research?** Apply the review criteria above.

## Related Documents

- [Research Folder README](README.md) — the index.
- [Knowledge Representation](02-knowledge-representation.md) — the core research topic.
- [OBD-II and Telemetry](03-obd-ii-and-telemetry.md) — data research.
- [Evaluation and Benchmarks](04-evaluation-and-benchmarks.md) — how we measure.
- [ADR System](../adr/README.md) — where decisions land.