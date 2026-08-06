# Architecture Documentation

## Why This Folder Exists

This folder contains the **system architecture** documentation for MechAI. It explains how the system is designed, how the repository is organized, and how the system will scale over time.

Architecture documentation is the bridge between the product vision (what we build) and the engineering standards (how we build it). It answers: *What are the major components, how do they interact, and why is the system shaped this way?*

## Documents in This Folder

| Document | Purpose |
|----------|---------|
| [`01-architecture-overview.md`](01-architecture-overview.md) | The high-level system architecture: components, data flows, and design principles. |
| [`02-repository-guide.md`](02-repository-guide.md) | The map of this repository: every folder, its purpose, and how to navigate it. |
| [`03-data-flows.md`](03-data-flows.md) | How data moves through the system: ingestion, storage, reasoning, and output. |
| [`04-future-scaling.md`](04-future-scaling.md) | How the architecture will evolve as MechAI grows from seed to scale. |

## How to Use This Folder

1. **New engineers and agents** start with the [Repository Guide](02-repository-guide.md) to learn where things live.
2. **Anyone designing a new component** reads the [Architecture Overview](01-architecture-overview.md) to understand the existing shape and constraints.
3. **Anyone working on data** reads the [Data Flows](03-data-flows.md) document.
4. **Anyone planning for growth** reads the [Future Scaling](04-future-scaling.md) document.

## Relationship to ADRs

The architecture documents describe the **current intended state**. When a significant architectural decision is made, it is recorded as an [ADR](../adr/README.md). The ADR records *why* a decision was made; the architecture document reflects *what* the current state is.

If an ADR changes the architecture, the architecture document must be updated in the same PR.

## Diagram Conventions

Architecture diagrams in this folder use [Mermaid](https://mermaid.js.org/) syntax where possible, so they render on GitHub and in most Markdown viewers. When a diagram is too complex for Mermaid, we use ASCII art or link to a dedicated diagram file.

*This folder is a living part of the repository. It is updated as the architecture evolves.*