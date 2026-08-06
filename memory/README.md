# Agent Memory System

## Why This Folder Exists

This folder is the **committed, shared memory system** for AI coding agents working in the MechAI repository. It exists so that agents retain context across sessions and coordinate with each other.

This is the *shared* memory system — it is committed to the repository so all agents and humans share the same context. It is distinct from local agent state (`.memory/`), which is gitignored.

## How to Use This Folder

1. **Before starting work**, read the relevant memory file(s):
   - `01-project-context.md` — always skim.
   - `02-architecture-notes.md` — if touching architecture.
   - `03-engineering-notes.md` — if writing code.
   - `04-domain-knowledge.md` — if working on automotive domains.
   - `05-agent-sessions.md` — to check for prior related work.
   - `06-open-questions.md` — for questions related to your task.
2. **After completing work**, update the relevant memory file(s) and append to the session log.
3. **Never store secrets, PII, or vehicle data** in memory files.

## Memory Files

| File | Purpose |
|------|---------|
| [`01-project-context.md`](01-project-context.md) | High-level project context: mission, key documents, current priorities. |
| [`02-architecture-notes.md`](02-architecture-notes.md) | Architecture decisions and notes. |
| [`03-engineering-notes.md`](03-engineering-notes.md) | Engineering conventions, tooling, and gotchas. |
| [`04-domain-knowledge.md`](04-domain-knowledge.md) | Automotive domain knowledge the team has learned. |
| [`05-agent-sessions.md`](05-agent-sessions.md) | Log of agent work sessions. |
| [`06-open-questions.md`](06-open-questions.md) | Open questions awaiting resolution. |

## Rules

- **Memory is committed.** Changes go through PRs like code.
- **Memory is concise and factual.** No fluff, no secrets.
- **Memory is curated.** Update stale entries; don't accumulate noise.
- **Memory is shared.** All agents read and write the same files.

## Related Documents

- [Memory System](docs/agents/02-memory-system.md) — the full memory system documentation.
- [AI Agent Handbook](docs/agents/01-ai-agent-handbook.md) — how agents work.
- [Security Policy](../SECURITY.md) — what never goes in memory.
