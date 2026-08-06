# Project Context

## Why This File Exists

This is the **high-level project context** for AI agents. It provides the essential context every agent needs before starting work. Agents should skim this file at the start of every session.

## The Project

- **Name:** MechAI
- **Mission:** Build the world's most intelligent AI mechanic — a system that reasons over automotive knowledge rather than acting as a simple chatbot.
- **Phase:** Foundation (Seed) — this repository is the engineering foundation, not a prototype.
- **Primary language:** Python (proposed, ADR-0002).
- **Core architecture:** Knowledge graph as reasoning substrate, vector store for grounding (proposed, ADR-0001).

## Key Documents

| Document | Purpose |
|----------|---------|
| [Vision](../docs/01-vision.md) | The long-term goal. |
| [Mission](../docs/02-mission.md) | What we do now. |
| [Product Philosophy](../docs/03-product-philosophy.md) | Product principles. |
| [Development Philosophy](../docs/04-development-philosophy.md) | How we build. |
| [Repository Guide](../docs/architecture/02-repository-guide.md) | Where things live. |
| [Engineering Handbook](../docs/engineering/01-engineering-handbook.md) | How we work. |
| [AI Agent Handbook](../docs/agents/01-ai-agent-handbook.md) | How agents work. |
| [Roadmap](../docs/roadmap/01-roadmap.md) | What we're building. |

## Current Priorities

1. **Complete the foundation** (this repository).
2. **Begin research** on knowledge representation.
3. **Prototype** the knowledge graph and reasoning.
4. **Record ADRs** as decisions are made.

## Current State

- The repository contains **no product code** — it is foundation-only.
- The documentation system, standards, processes, and agent infrastructure are in place.
- Research is the next focus (Phase 1).

## Rules for Agents

- Read the [AI Agent Handbook](../docs/agents/01-ai-agent-handbook.md) before working.
- Follow the [Engineering Handbook](../docs/engineering/01-engineering-handbook.md).
- Never commit secrets, PII, or vehicle data.
- Use this memory system to persist context.

## Status

- **Last updated:** 2026-08-03
- **Status:** Active