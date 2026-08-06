# Architecture Notes

## Why This File Exists

This file stores **architecture decisions and notes** for AI agents. It captures the "why" behind the system design so agents don't have to re-derive it. Agents should read this before touching architecture.

## Current Architecture (Target)

The target architecture is described in [Architecture Overview](../docs/architecture/01-architecture-overview.md). Key points:

- **Knowledge graph** is the core reasoning substrate (proposed, ADR-0001).
- **Vector store** is a complement for grounding, not the core.
- **Multi-modal inputs** (text, OBD-II, images, voice) are first-class from the start.
- **Deployment-agnostic core** — the same engine runs in SaaS and on-premises.
- **Provenance is critical** — every datum carries its source.

## Key Decisions

### Knowledge Graph as Reasoning Core (ADR-0001)

- **Status:** Proposed
- **What:** The knowledge graph is the primary reasoning substrate.
- **Why:** Enables causal, explainable reasoning — the product philosophy.
- **Implication for agents:** New components must integrate with the knowledge graph, not just a vector store.

### Python as Primary Language (ADR-0002)

- **Status:** Proposed
- **What:** Python is the primary implementation language.
- **Why:** Strong AI/ML ecosystem, readability, talent.
- **Implication for agents:** Follow the Python coding standards.

### Documentation as Code (ADR-0003)

- **Status:** Accepted
- **What:** Documentation is a first-class artifact.
- **Why:** Long-term maintainability and agent effectiveness.
- **Implication for agents:** Update docs when behavior changes.

### Agent Memory System (ADR-0004)

- **Status:** Accepted
- **What:** Committed memory system for agents.
- **Why:** Agents need persistent, shared context.
- **Implication for agents:** Use this memory system.

## Architecture Gotchas

- **The architecture is a target, not yet implemented.** The repository contains no product code.
- **ADR-0001 and ADR-0002 are proposed**, not accepted. They will be validated through research.
- **Provenance is a first-class requirement** — design data models with provenance from day one.

## Status

- **Last updated:** 2026-08-03
- **Status:** Active