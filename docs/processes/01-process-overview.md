# Process Overview

## Why This Document Exists

This document explains **how the MechAI processes fit together**. It is the entry point for understanding how work flows through the organization — from roadmap to sprint to task to branch to commit.

These processes are designed for a growing team of humans and AI agents. They are lightweight but consistent. The goal is not bureaucracy; it is clarity.

## The Work Flow

```
┌──────────────────────────┐
│   ROADMAP (docs/roadmap/)│
│   What we're building    │
└────────────┬─────────────┘
             │ informs
┌────────────▼─────────────┐
│    SPRINT (weekly)       │
│   What we do this week   │
└────────────┬─────────────┘
             │ breaks into
┌────────────▼─────────────┐
│    TASKS (tasks/)        │
│   Units of work          │
└────────────┬─────────────┘
             │ implemented via
┌────────────▼─────────────┐
│    BRANCHES              │
│   Type/description       │
└────────────┬─────────────┘
             │ committed via
┌────────────▼─────────────┐
│    COMMITS & PRs         │
│   Conventional commits   │
│   Reviewed, CI green     │
└────────────┬─────────────┘
             │ merged into
┌────────────▼─────────────┐
│          MAIN            │
│   The source of truth    │
└──────────────────────────┘
```

## Roles

| Role | Responsibility |
|------|----------------|
| **Maintainer** | Reviews and merges PRs, maintains roadmap, enforces standards. |
| **Contributor** | Any human or agent that proposes changes. |
| **Reviewer** | Reviews PRs; may be a maintainer or a peer. |
| **Product lead** | Owns the roadmap and priorities (may also be a maintainer at seed stage). |

## Key Documents

| Process | Document |
|---------|----------|
| Roadmap | `docs/roadmap/README.md` |
| Sprint | `05-sprint-workflow.md` |
| Task | `04-task-workflow.md` |
| Branch | `03-branch-strategy.md` |
| Git | `02-git-workflow.md` |

## Principles

1. **Small, focused changes.** One task, one branch, one PR.
2. **Main is always releasable.** Never merge broken or incomplete work to main.
3. **Reviews are mandatory.** Every PR gets at least one approval.
4. **Docs change with code.** If behavior changes, docs change in the same PR.
5. **Agents follow the same process.** AI agents use the same workflow as humans.
6. **Fail loudly.** If something is blocked, say so. Don't silently stall.

## Current State (Seed)

At seed stage, the process is lightweight:

- **Sprints:** Optional but recommended (see [Sprint Workflow](05-sprint-workflow.md)).
- **Tasks:** Simple markdown files in `tasks/` (see [Task Workflow](04-task-workflow.md)).
- **Reviews:** At least one approver.
- **CI:** Not yet established; will be added with product code.

The process scales with the team. As we grow, automation (CI) and structure are added without changing the core principles.

## How to Use This Document

1. **New contributors** read this document to understand the flow.
2. **Then read** the specific process docs for your work.
3. **When in doubt**, follow the principles above.

## Related Documents

- [Git Workflow](02-git-workflow.md)
- [Branch Strategy](03-branch-strategy.md)
- [Task Workflow](04-task-workflow.md)
- [Sprint Workflow](05-sprint-workflow.md)
- [Roadmap](../roadmap/README.md)