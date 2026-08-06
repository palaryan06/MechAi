# AI Agent Documentation

## Why This Folder Exists

This folder contains the **documentation for AI coding agents** working in the MechAI repository. It exists because AI agents are first-class contributors to this project. For agents to work safely and effectively alongside human engineers, they need clear guidance and a persistent memory system.

## Documents in This Folder

| Document | Purpose |
|----------|---------|
| [`01-ai-agent-handbook.md`](01-ai-agent-handbook.md) | The core handbook: how agents work in this repository, what they must do, and what they must never do. |
| [`02-memory-system.md`](02-memory-system.md) | The persistent memory system agents use to retain context across sessions. |
| [`03-agent-task-guide.md`](03-agent-task-guide.md) | How agents pick up, execute, and complete tasks. |

## How to Use This Folder

1. **Every AI agent** must read the [AI Agent Handbook](01-ai-agent-handbook.md) before starting any work.
2. **Agents that need to persist context** use the [Memory System](02-memory-system.md).
3. **Agents executing a task** follow the [Agent Task Guide](03-agent-task-guide.md).

## Why This Matters

MechAI is designed for a future where **multiple AI agents and human engineers work side by side**. For this to work:

- **Agents must follow the same standards** as humans (code, git, docs, security).
- **Agents must not interfere** with each other or with human work.
- **Agents must persist context** so knowledge isn't lost between sessions.
- **Agents must be safe** — never commit secrets, never break main, never act without review.

This folder makes those requirements explicit and actionable.

## Relationship to Other Folders

- **Engineering standards** ([`../engineering/`](../engineering/)) apply to agents as much as to humans.
- **Processes** ([`../processes/`](../processes/)) define the workflow agents follow.
- The **memory system** ([`memory/`](../../memory/)) is the committed storage for agent context.

*This folder is a living part of the repository. Agent guidance evolves as our tools and practices evolve.*