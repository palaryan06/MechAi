# MechAI Development Philosophy

## Why This Document Exists

The **development philosophy** defines *how* we write software at MechAI. It is the bridge between the product philosophy (what we build) and the engineering standards (the concrete rules). It answers: *What do we value when we sit down to write code, review a PR, or design a system?*

This document is for every contributor — human or AI agent. It sets the cultural and technical expectations for how we work together.

## Core Principles

### 1. Long-Term Maintainability Over Short-Term Speed

**Principle:** We optimize for the codebase we will have in five years, not the demo we need this week.

**What it means:**
- We prefer boring, well-understood technology over clever, novel stacks.
- We write code that a new engineer (or a fresh AI agent) can read and understand without tribal knowledge.
- We accept slightly slower initial velocity in exchange for dramatically lower maintenance cost later.

**In practice:**
- Every new dependency is a decision that must be justified (see [Engineering Handbook](engineering/01-engineering-handbook.md)).
- We refactor early and often, before complexity compounds.
- We document *why* a design exists, not just *what* it does.

### 2. Documentation Is Code

**Principle:** Documentation is a first-class artifact, reviewed and maintained like source code.

**What it means:**
- A PR that changes behavior must update the relevant docs.
- A new architectural decision gets an ADR.
- Stale documentation is treated as a bug.

**In practice:**
- Docs live in the same repository as code, so they stay in sync.
- Every doc explains its purpose and how to use it.
- AI agents are expected to read and update docs as part of their work.

### 3. Evidence Over Opinion

**Principle:** Technical decisions are grounded in evidence, not vibes.

**What it means:**
- We benchmark before choosing a vector store, an embedding model, or a database.
- We write down the trade-offs in an ADR.
- We prefer measurable outcomes (accuracy, latency, cost) over anecdote.

**In practice:**
- Research and experiments are documented in [`docs/research/`](research/) and [`experiments/`](../experiments/).
- Significant decisions are recorded in [`docs/adr/`](adr/).

### 4. Simplicity Is a Feature

**Principle:** The simplest solution that meets the requirement is the best solution.

**What it means:**
- We avoid premature abstraction. We build for today's needs, structured for tomorrow's growth.
- We prefer a clear, direct implementation over an elegant-but-opaque one.
- We delete code that isn't earning its keep.

**In practice:**
- YAGNI (You Aren't Gonna Need It) is a default stance.
- We refactor when a pattern repeats, not before.
- We favor small, focused modules over sprawling monoliths.

### 5. Quality Is Non-Negotiable

**Principle:** Even at seed stage, we write tests, review thoroughly, and hold a high bar.

**What it means:**
- New logic ships with tests.
- PRs are reviewed by at least one other person (human or agent).
- We treat "it works on my machine" as insufficient.

**In practice:**
- See [Testing Philosophy](engineering/05-testing-philosophy.md).
- CI (when established) runs tests, linting, and type checks on every PR.

### 6. Agents Are First-Class Contributors

**Principle:** AI coding agents are teammates, not tools to be feared or ignored.

**What it means:**
- The repository is structured so agents can navigate it safely (see [AI Agent Handbook](agents/01-ai-agent-handbook.md)).
- Agents follow the same standards, git conventions, and review process as humans.
- We invest in the [Memory System](agents/02-memory-system.md) so agents retain context across sessions.

**In practice:**
- Clear folder structure and naming conventions.
- Explicit instructions for agents in the handbook.
- A memory system that persists agent learnings.

### 7. Fail Loudly, Learn Quickly

**Principle:** We surface problems early and treat failures as learning opportunities.

**What it means:**
- We log errors with enough context to debug (see [Logging Philosophy](engineering/04-logging-philosophy.md)).
- We write tests that fail when assumptions break.
- We document post-mortems and share learnings.

**In practice:**
- Structured, contextual logging.
- A culture where "I broke it, here's what I learned" is celebrated, not punished.

## How We Make Decisions

1. **Small decisions:** Made by the implementer, documented in the PR.
2. **Medium decisions:** Discussed in the PR or a short design note.
3. **Large decisions:** Written as an ADR, reviewed by the team, and recorded permanently.

The threshold for an ADR is: *"Will a future engineer need to know why we chose this?"* If yes, write an ADR.

## The Development Loop

```
┌─────────────────────────────────────────────────────────┐
│                    DEVELOPMENT LOOP                     │
│                                                         │
│  Understand → Plan → Implement → Test → Review → Ship   │
│     │          │        │         │      │       │      │
│     └──────────┴────────┴─────────┴──────┴───────┘      │
│                    (iterate)                            │
│                                                         │
│  Every loop is documented:                              │
│  - What we did (commit/PR)                              │
│  - Why we did it (ADR if significant)                   │
│  - What we learned (research/experiment notes)          │
└─────────────────────────────────────────────────────────┘
```

## What We Optimize For (and What We Don't)

| We optimize for | We do NOT optimize for |
|-----------------|------------------------|
| Long-term maintainability | Short-term demo speed |
| Evidence-based decisions | Hype-driven technology |
| Readable, boring code | Clever, opaque code |
| Documented reasoning | Tribal knowledge |
| Tested correctness | "It works on my machine" |
| Agent-friendly structure | Human-only workflows |
| Simplicity | Premature abstraction |

## Related Documents

- [Product Philosophy](03-product-philosophy.md) — what we build and why.
- [Engineering Handbook](engineering/01-engineering-handbook.md) — the concrete rules.
- [Coding Standards](engineering/03-coding-standards.md) — how code looks.
- [AI Agent Handbook](agents/01-ai-agent-handbook.md) — how agents work here.
- [ADR System](adr/README.md) — how we record decisions.

*This philosophy is a living document. Significant changes are recorded as ADRs.*