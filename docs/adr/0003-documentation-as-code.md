# ADR-0003: Documentation as Code

- **Status:** Accepted
- **Date:** 2026-08-03
- **Author:** Founding Engineering Team

## Context

MechAI is building a long-lived, complex system with multiple contributors — humans and AI agents. As the team grows to 20+ engineers and multiple agents, knowledge must not become tribal. Without a documentation discipline, the codebase becomes unmaintainable and agents cannot work effectively.

The development philosophy requires long-term maintainability. To achieve this, the "why" and the "how" must be recorded — and kept current.

## Decision

We adopt **"documentation is code"** as a core principle.

This means:
- Documentation is a **first-class artifact**, reviewed and maintained like source code.
- Documentation lives **in the repository**, in a dedicated `docs/` folder, keeping it in sync with the code.
- **PRs that change behavior must update the relevant docs**.
- **Significant decisions are recorded as ADRs**.
- **Documentation follows standards** ([Documentation Standards](../engineering/07-documentation-standards.md)) and is held to a quality bar.
- **Stale documentation is treated as a bug.**

## Consequences

### Positive Consequences

- **Knowledge is durable.** The "why" is recorded, not tribal.
- **Agents can work effectively.** Clear docs make the repository navigable for AI agents.
- **Onboarding is faster.** New engineers have a map.
- **Decisions are traceable.** Future contributors know why the system is shaped this way.
- **Docs and code stay in sync**, reducing drift.

### Negative Consequences

- **Cost:** Maintaining docs is ongoing work. Every behavior change has a doc component.
- **Discipline required:** Contributors must remember to update docs.
- **Review burden:** Docs add review surface area.

## Alternatives Considered

### Alternative 1: Docs Outside the Repository (Wiki, Notion)

External documentation. **Rejected** because external docs drift quickly, are not versioned with code, and are not easily accessible to AI agents.

### Alternative 2: Minimal Documentation (Code Comments Only)

Rely on code comments and self-documenting code. **Rejected** because comments capture *what* but not *why*. Architecture decisions, trade-offs, and rationale need dedicated documents.

### Alternative 3: Documentation as Code (Adopted)

Chosen because it keeps knowledge durable, in-sync, and accessible to all contributors.

## Rationale

The development philosophy (**long-term maintainability**, **documentation is code**) is a foundational principle. To build a system that will survive years and a growing team — including AI agents that lose context between sessions — durable, in-repo, maintained documentation is essential.

## Implementation Notes

- The `docs/` folder is the single source of truth (see [Repository Guide](../architecture/02-repository-guide.md)).
- Documentation follows the [Documentation Standards](../engineering/07-documentation-standards.md).
- The [ADR System](README.md) records significant decisions.
- AI agents are expected to read and maintain docs (see [AI Agent Handbook](../agents/01-ai-agent-handbook.md)).

## References

- [Development Philosophy](../04-development-philosophy.md)
- [Documentation Standards](../engineering/07-documentation-standards.md)
- [Repository Guide](../architecture/02-repository-guide.md)
- [AI Agent Handbook](../agents/01-ai-agent-handbook.md)