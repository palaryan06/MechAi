# ADR-0004: Agent Memory System

- **Status:** Accepted
- **Date:** 2026-08-03
- **Author:** Founding Engineering Team

## Context

MechAI is designed for a future where **multiple AI coding agents and human engineers work side by side**. AI agents do not retain context between sessions — every session starts from scratch.

Without a memory system, agents waste effort re-reading the repository, re-discovering conventions, and re-learning what previous agents already figured out. Multiple agents cannot coordinate, and knowledge gained in one session is lost.

The development philosophy requires that **agents are first-class contributors**. For that to work, agents need a durable, shared knowledge store.

## Decision

We adopt a **committed memory system** for AI agents.

- Memory lives in a **`memory/` folder at the repository root**, committed to git.
- Memory is **Markdown** — readable by both humans and agents.
- Memory is **structured by topic** (project context, architecture notes, engineering notes, domain knowledge, session logs, open questions).
- **All agents share the same memory** — it is versioned in the repository.
- **Memory changes go through PRs** like code changes (unless explicitly allowed otherwise).
- **No secrets, PII, or vehicle data** ever go into memory.

## Consequences

### Positive Consequences

- **Persistent agent context:** Agents retain knowledge across sessions.
- **Coordination:** Multiple agents share the same information.
- **Reduced duplication:** Agents don't re-explore what's already mapped.
- **Human-readable:** Humans can read and review agent memory.
- **Versioned:** Memory history is preserved in git.

### Negative Consequences

- **Maintenance:** Memory must be kept concise and current, or it becomes noise.
- **Review burden:** Memory changes add review surface area.
- **Discipline required:** Agents must remember to read and write memory.

## Alternatives Considered

### Alternative 1: No Memory System (Stateless Agents)

Rely on agents reading the repository fresh each time. **Rejected** because the repository is large and growing; fresh reading is expensive, and cross-session knowledge is lost.

### Alternative 2: Local, Non-Committed Agent State

Store per-agent memory in a gitignored local folder. **Rejected** because it is not shared — agents cannot coordinate, and knowledge is lost when the machine changes.

### Alternative 3: External Memory (Vector DB for Agents)

Store agent memory in an external vector database. **Rejected** for now as premature — a simple committed folder is sufficient at this stage and keeps everything in-repo and reviewable. Revisit this when memory grows.

### Alternative 4: Committed Memory System (Adopted)

Chosen because it is shared, versioned, reviewable, and sufficient for current needs.

## Rationale

The development philosophy (**agents are first-class contributors**) and the future scaling goals (**multiple agents working together**) require agents to retain and share context. A committed, structured, Markdown-based memory system provides this with minimal complexity, maximum transparency, and no external dependencies.

This decision aligns with the "simplicity is a feature" principle — we use the simplest thing that works.

## Implementation Notes

- Memory lives in `memory/` at the repository root (see [Repository Guide](../architecture/02-repository-guide.md)).
- The memory structure and rules are defined in [Memory System](../agents/02-memory-system.md).
- Agents are instructed on memory usage in the [AI Agent Handbook](../agents/01-ai-agent-handbook.md).
- Local agent state (`.memory/`) remains gitignored and separate from the shared system.

## References

- [Memory System](../agents/02-memory-system.md)
- [AI Agent Handbook](../agents/01-ai-agent-handbook.md)
- [Development Philosophy](../04-development-philosophy.md)
- [Future Scaling Philosophy (Engineering)](../engineering/09-future-scaling-philosophy.md)