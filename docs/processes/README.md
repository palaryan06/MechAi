# Processes

## Why This Folder Exists

This folder contains the **processes and workflows** for MechAI. It defines *how we work*: how we use git, how we branch, how we track tasks, and how we run sprints. These processes exist so that a growing team of humans and AI agents can work together consistently.

## Documents in This Folder

| Document | Purpose |
|----------|---------|
| [`01-process-overview.md`](01-process-overview.md) | How the processes fit together. |
| [`02-git-workflow.md`](02-git-workflow.md) | How we use git: commits, PRs, and merges. |
| [`03-branch-strategy.md`](03-branch-strategy.md) | How we create and manage branches. |
| [`04-task-workflow.md`](04-task-workflow.md) | How we track and complete units of work. |
| [`05-sprint-workflow.md`](05-sprint-workflow.md) | How we run sprints. |

## How the Processes Fit Together

```
Roadmap (docs/roadmap/)
    │
    ▼
Sprint (05-sprint-workflow.md)
    │
    ▼
Tasks (04-task-workflow.md)
    │
    ▼
Branches (03-branch-strategy.md)
    │
    ▼
Commits & PRs (02-git-workflow.md)
    ▼
Merge to main
```

## How to Use This Folder

1. **New contributors** read the [Process Overview](01-process-overview.md) first.
2. **Working on code?** Read the [Git Workflow](02-git-workflow.md) and [Branch Strategy](03-branch-strategy.md).
3. **Tracking work?** Read the [Task Workflow](04-task-workflow.md).
4. **Running a sprint?** Read the [Sprint Workflow](05-sprint-workflow.md).

## Relationship to Other Folders

- **Engineering standards** ([`../engineering/`](../engineering/)) define *how we build*. Processes define *how we work*.
- **Documents** ([`../architecture/`](../architecture/)) explain the system. Processes explain how we change it.
- **ADRs** ([`../adr/`](../adr/)) record significant decisions. Process changes are ADRs if significant.

*Processes are living. They evolve as the team learns. Significant changes are recorded as ADRs.*