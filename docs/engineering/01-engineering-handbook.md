# Engineering Handbook

## Why This Document Exists

This is the **core engineering handbook** for MechAI. It is the first document a new engineer (human or AI agent) reads to understand how we work. It consolidates the most important rules, values, and practices into one reference.

This handbook is intentionally concise. It points to deeper documents where needed. It is the "if you only read one document, read this one" for engineering.

## Who This Is For

- **New human engineers** onboarding to the team.
- **AI coding agents** starting work in this repository.
- **Existing team members** who need a refresher on our standards.

## Our Engineering Values

1. **Long-term maintainability over short-term speed.** We build for the codebase we'll have in five years.
2. **Documentation is code.** Docs are reviewed and maintained like source code.
3. **Evidence over opinion.** Decisions are grounded in data and recorded as ADRs.
4. **Simplicity is a feature.** The simplest solution that works is the best.
5. **Quality is non-negotiable.** Tests, reviews, and a high bar, even at seed stage.
6. **Agents are first-class contributors.** The repository supports humans and AI agents equally.
7. **Fail loudly, learn quickly.** Surface problems early; treat failures as learning.

## The Rules

### 1. Follow the Standards

- Read and follow the [Coding Standards](03-coding-standards.md) and [Naming Conventions](02-naming-conventions.md).
- Formatting, naming, and structure must be consistent across the codebase.

### 2. Write Tests

- New product logic ships with tests. See [Testing Philosophy](05-testing-philosophy.md).
- Tests must be meaningful: they test behavior, not implementation details.

### 3. Document as You Go

- If you change behavior, update the relevant docs in the same PR.
- If a decision is significant, write an ADR. See [ADR System](../adr/README.md).
- Follow the [Documentation Standards](07-documentation-standards.md).

### 4. Log Properly

- Use structured, contextual logging. See [Logging Philosophy](04-logging-philosophy.md).
- Never log secrets, PII, or sensitive vehicle data.

### 5. Manage Configuration Safely

- Secrets never enter the repository. Use environment variables. See [Configuration Philosophy](06-configuration-philosophy.md).

### 6. Think About Security

- Security is everyone's responsibility. See [Security Philosophy](08-security-philosophy.md) and the [Security Policy](../../SECURITY.md).

### 7. Use Git Properly

- Follow the [Git Workflow](../processes/02-git-workflow.md) and [Branch Strategy](../processes/03-branch-strategy.md).
- Use Conventional Commits. One logical change per commit.

### 8. Review Thoroughly

- All PRs require at least one approval. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Reviewers are kind, specific, and provide rationale.

## The Development Loop

```
Understand → Plan → Implement → Test → Review → Ship
```

Every loop is documented:
- **What we did:** commit/PR.
- **Why we did it:** ADR if significant.
- **What we learned:** research/experiment notes.

## Dependencies

- **Every new dependency is a decision.** Before adding a dependency, ask:
  - Does it serve a clear, current need?
  - Is it well-maintained and widely used?
  - What is the maintenance cost over five years?
  - Could we do without it?
- Record significant dependency decisions in an ADR.

## Working With AI Agents

- AI agents are teammates. They follow the same standards and review process as humans.
- Agents must read the [AI Agent Handbook](../agents/01-ai-agent-handbook.md) before starting work.
- Agents must use the [Memory System](../agents/02-memory-system.md) to persist context.

## What We Do NOT Do

- **No premature abstraction.** Build for today's needs, structured for tomorrow's growth.
- **No clever hacks.** Readable, boring code outlives clever code.
- **No ungrounded claims.** In product code, every answer must be traceable to evidence.
- **No secrets in the repo.** Ever.

## Quick Reference

| Topic | Document |
|-------|----------|
| How to write code | [Coding Standards](03-coding-standards.md) |
| How to name things | [Naming Conventions](02-naming-conventions.md) |
| How to test | [Testing Philosophy](05-testing-philosophy.md) |
| How to log | [Logging Philosophy](04-logging-philosophy.md) |
| How to configure | [Configuration Philosophy](06-configuration-philosophy.md) |
| How to document | [Documentation Standards](07-documentation-standards.md) |
| How to think about security | [Security Philosophy](08-security-philosophy.md) |
| How to use git | [Git Workflow](../processes/02-git-workflow.md) |
| How to branch | [Branch Strategy](../processes/03-branch-strategy.md) |
| How to track work | [Task Workflow](../processes/04-task-workflow.md) |
| How to run sprints | [Sprint Workflow](../processes/05-sprint-workflow.md) |
| How agents work | [AI Agent Handbook](../agents/01-ai-agent-handbook.md) |

## Related Documents

- [Development Philosophy](../04-development-philosophy.md) — the values behind these rules.
- [Repository Guide](../architecture/02-repository-guide.md) — where things live.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — how to contribute.

*This handbook is a living document. Significant changes are recorded as ADRs.*