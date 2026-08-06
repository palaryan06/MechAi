# Future Scaling Philosophy

## Why This Document Exists

This document describes **how the MechAI architecture will evolve** as the company grows from seed to scale. It answers: *What will we need to change, and what will we keep, as we grow from a small team to 20+ engineers, from a prototype to a SaaS + on-premises product, and from a single model to a multi-modal reasoning system?*

This is a **planning document**, not a commitment. It describes the direction and the principles that will guide scaling decisions. Specific scaling decisions will be made when they are needed, and recorded as ADRs.

## Scaling Dimensions

MechAI will scale along several dimensions simultaneously:

1. **Team size:** From a few engineers to 20+ engineers and multiple AI agents.
2. **Data volume:** From a few manuals to thousands of vehicle models, millions of documents, and billions of telemetry points.
3. **User load:** From a handful of test users to thousands of concurrent SaaS users.
4. **Deployment:** From a single environment to SaaS + on-premises + potentially edge.
5. **Modality:** From text to OBD-II, images, and voice.
6. **Reasoning complexity:** From simple retrieval to multi-step causal reasoning over a large knowledge graph.

## Scaling Principles

### 1. Modularity Is the Foundation

**Principle:** The system is composed of independent, replaceable modules.

**Why it matters:** When we need to scale a component (e.g., the vector store), we can replace it without rewriting the whole system. When we add a modality (e.g., voice), we add a module rather than rearchitecting.

**In practice:**
- Clear interfaces between components.
- Each component is independently testable.
- Components communicate through well-defined contracts.

### 2. The Core Reasoning Engine Is Deployment-Agnostic

**Principle:** The same reasoning engine runs in SaaS and on-premises.

**Why it matters:** The mission requires serving privacy-sensitive customers who need local deployment. We must not build a SaaS-only architecture that cannot be deployed on-premises.

**In practice:**
- The reasoning engine has no hard dependency on cloud services.
- Storage and compute are abstracted behind interfaces.
- On-premises deployment is a configuration, not a fork.

### 3. Data Grows, Provenance Stays

**Principle:** As data volume grows, provenance becomes *more* important, not less.

**Why it matters:** The product philosophy requires every claim to be traceable. At scale, without provenance, the system becomes an untrustworthy black box.

**In practice:**
- Provenance is part of the data model from day one.
- Scaling storage must not sacrifice provenance.
- We invest in data quality tooling as data grows.

### 4. Agents Scale With Us

**Principle:** AI coding agents are part of the team, and the architecture must support them at scale.

**Why it matters:** With 20+ engineers and multiple agents, the repository must be navigable and safe for all contributors.

**In practice:**
- Clear documentation and structure (see [Repository Guide](02-repository-guide.md)).
- A robust [Memory System](../agents/02-memory-system.md) so agents retain context.
- Standards that agents can follow reliably.

### 5. Simplicity Scales Better Than Cleverness

**Principle:** Boring, well-understood technology scales more predictably than clever, novel stacks.

**Why it matters:** At scale, operational complexity is the enemy. We prefer technology with a large community, good tooling, and known failure modes.

**In practice:**
- We benchmark before choosing new technology.
- We prefer managed services where they reduce operational burden.
- We document the trade-offs in ADRs.

## Scaling Timeline (Indicative)

| Phase | Team | Data | Deployment | Focus |
|-------|------|------|------------|-------|
| **Seed (now)** | 1-3 engineers | A few manuals | Local dev | Foundation, research |
| **Prototype** | 3-5 engineers | Dozens of manuals | Single cloud env | Knowledge graph, reasoning prototype |
| **MVP** | 5-10 engineers | Hundreds of manuals | SaaS (single region) | First product, OBD-II, text |
| **Growth** | 10-20 engineers | Thousands of manuals, telemetry | SaaS (multi-region) + on-premises | Multi-modal, scale, reliability |
| **Scale** | 20+ engineers | Millions of documents, billions of telemetry | SaaS + on-premises + edge | Full vision |

## What We Will Keep (The Invariants)

These are the architectural invariants that should **not** change as we scale:

1. **Evidence-based reasoning:** Every answer is traceable to a source.
2. **Knowledge graph as the reasoning substrate:** The graph is the heart of causal reasoning.
3. **Provenance in the data model:** Every datum carries its source.
4. **Deployment-agnostic core:** The reasoning engine runs anywhere.
5. **Modular components:** Independent, replaceable, testable.
6. **Documentation is code:** Docs stay in sync with the system.

## What Will Likely Change

These are the areas where we expect significant change as we scale:

| Area | Now | Likely Future |
|------|-----|---------------|
| **Vector store** | None (research) | Specialized vector database |
| **Knowledge graph** | None (research) | Graph database with distributed query |
| **Document store** | None (research) | Object storage + search index |
| **Vehicle state** | None (research) | Time-series database |
| **Compute** | Local dev | GPU clusters for embedding/reasoning |
| **Deployment** | Local dev | Kubernetes (SaaS) + on-prem packages |
| **Observability** | None | Distributed tracing, metrics, alerting |
| **CI/CD** | None | Full pipeline with automated testing |

## Scaling Risks

| Risk | Mitigation |
|------|------------|
| Knowledge graph becomes too large to query efficiently | Partition by vehicle model/system; use graph DB with distributed query |
| Vector store becomes a bottleneck | Benchmark early; choose a scalable store; cache aggressively |
| On-premises deployment diverges from SaaS | Keep the core deployment-agnostic; test both in CI |
| Data quality degrades as volume grows | Invest in validation tooling; provenance from day one |
| Team grows faster than documentation | Documentation is code; agents help maintain it |
| Multi-modal inputs multiply complexity | Modular ingestion; clear interfaces; incremental modality adoption |

## How to Use This Document

1. **Planning a new component?** Design it to be modular and deployment-agnostic.
2. **Choosing technology?** Prefer scalable, well-understood options; record the decision in an ADR.
3. **Worried about a scaling risk?** Add it to the [Risk Register](../risk/01-risk-register.md).
4. **Making a significant scaling decision?** Write an ADR and update this document.

## Related Documents

- [Architecture Overview](01-architecture-overview.md) — the current target architecture.
- [Data Flows](03-data-flows.md) — how data moves.
- [Future Scaling Philosophy (Engineering)](../engineering/09-future-scaling-philosophy.md) — the engineering perspective.
- [Risk Register](../risk/01-risk-register.md) — known risks.
- [Roadmap](../roadmap/README.md) — the near-term plan.