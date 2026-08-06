# Roadmap

## Why This Document Exists

This is the **current MechAI roadmap**. It defines the phases, milestones, and priorities for building MechAI. It is the concrete translation of the [Mission](../02-mission.md) into a plan.

This roadmap is a **living document**. It is updated as we learn, as research resolves questions, and as the mission evolves. Significant changes to the roadmap are discussed with the team.

## Roadmap Phases

```
Phase 0: Foundation (now)      → This repository
Phase 1: Research              → Knowledge representation, OBD-II, evaluation
Phase 2: Prototype             → Small knowledge graph + reasoning demo
Phase 3: MVP                   → First product: text + OBD-II diagnosis
Phase 4: Growth                → Multi-modal, SaaS + on-premises
Phase 5: Scale                 → Full vision
```

## Phase 0: Foundation (Current)

**Goal:** Establish the engineering foundation that future work builds on.

**Milestones:**
- [x] Repository structure and documentation system
- [x] Engineering standards and processes
- [x] AI agent handbook and memory system
- [x] ADR system
- [x] Research and experiment infrastructure
- [ ] CI/CD (when product code arrives)
- [ ] Python project scaffolding (when product code arrives)

**Exit criteria:** The repository is a solid foundation that humans and agents can work in safely and effectively.

## Phase 1: Research

**Goal:** Resolve the core open questions before building the product.

**Milestones:**
- [ ] Validate the knowledge graph approach (see [Research: Knowledge Representation](../research/02-knowledge-representation.md))
- [ ] Research OBD-II parsing and normalization (see [Research: OBD-II](../research/03-obd-ii-and-telemetry.md))
- [ ] Define the evaluation and benchmark approach (see [Research: Evaluation](../research/04-evaluation-and-benchmarks.md))
- [ ] Record foundational ADRs (vector store, graph DB, data model)

**Exit criteria:** The core architecture decisions are validated and recorded as ADRs.

## Phase 2: Prototype

**Goal:** Build a small, working prototype that demonstrates the reasoning approach.

**Milestones:**
- [ ] Build a small knowledge graph (3-5 vehicle systems) from synthetic/sample data
- [ ] Implement a basic reasoning path: symptom → hypothesis → evidence
- [ ] Integrate OBD-II data as evidence
- [ ] Demonstrate a grounded, explainable diagnosis
- [ ] Evaluate against a small benchmark

**Exit criteria:** A prototype that can explain *why* a symptom implies a fault, with sources.

## Phase 3: MVP

**Goal:** Ship the first product: text + OBD-II diagnosis for a focused set of vehicle systems.

**Milestones:**
- [ ] SaaS web experience
- [ ] OBD-II ingestion (via user-provided data or adapter)
- [ ] Knowledge graph for a focused set of systems
- [ ] Reasoning engine with evidence and uncertainty
- [ ] Evaluation benchmark with measurable targets
- [ ] CI/CD, observability, and deployment

**Exit criteria:** A usable product that provides evidence-backed diagnoses for a focused scope.

## Phase 4: Growth

**Goal:** Expand modalities, coverage, and deployment options.

**Milestones:**
- [ ] Image understanding (photos of parts, dashboards)
- [ ] Voice input
- [ ] Expanded vehicle coverage
- [ ] On-premises deployment
- [ ] Fleet/telemetry support

**Exit criteria:** Multi-modal, multi-deployment product serving multiple customer segments.

## Phase 5: Scale

**Goal:** The full vision — the world's most intelligent AI mechanic.

**Milestones:**
- [ ] Broad vehicle coverage
- [ ] Advanced causal reasoning
- [ ] Full multi-modal integration
- [ ] Scale to millions of documents and billions of telemetry points

**Exit criteria:** The vision is realized.

## Current Priorities

The immediate priorities (Phase 0 → Phase 1) are:

1. **Complete the foundation** (this repository).
2. **Begin research** on knowledge representation.
3. **Prototype** the knowledge graph and reasoning.
4. **Record ADRs** as decisions are made.

## How to Use This Roadmap

1. **Planning sprints?** Pull milestones from the current phase.
2. **Proposing new work?** Link it to a roadmap milestone.
3. **Reviewing priorities?** Check the [Priorities](02-priorities.md) doc.

## Related Documents

- [Mission](../02-mission.md) — the near-term direction.
- [Vision](../01-vision.md) — the long-term goal.
- [Priorities](02-priorities.md) — how we prioritize.
- [Risk Register](../risk/01-risk-register.md) — risks that could affect the roadmap.