# Sprint Workflow

## Why This Document Exists

This document defines **how we run sprints** in MechAI. It exists to give the team a regular cadence for planning, executing, and reviewing work. Sprints are the heartbeat that turns the roadmap into weekly, achievable progress.

Sprints are lightweight at seed stage and scale with the team. The goal is cadence and clarity, not bureaucracy.

## What Is a Sprint?

A sprint is a **fixed timebox** (typically one week) during which the team commits to a set of tasks. At the end of the sprint, we review what was done, learn, and plan the next sprint.

## Sprint Cadence

| Element | Default |
|----------|---------|
| Sprint length | 1 week |
| Planning | Start of sprint (Monday) |
| Review | End of sprint (Friday) |
| Retrospective | End of sprint (Friday, after review) |

At seed stage, sprints may be informal (a quick planning session in chat). As the team grows, sprints become more structured.

## The Sprint Cycle

```
┌─────────────┐
│  PLANNING   │  Choose tasks for the sprint from the backlog
└──────┬──────┘
       ▼
┌─────────────┐
│  EXECUTION  │  Work on tasks all week
└──────┬──────┘
       ▼
┌─────────────┐
│   REVIEW    │  Demo/verify what was completed
└──────┬──────┘
       ▼
┌─────────────┐
│  RETRO      │  What went well? What can improve?
└─────────────┘
```

### 1. Planning (Start of Sprint)

- Review the [Roadmap](../roadmap/README.md) and backlog.
- Choose tasks for the sprint based on priority (see [Task Workflow](04-task-workflow.md)).
- Commit to a realistic set of tasks. Quality over quantity.
- Assign each task (or leave unassigned for agents/humans to pick up).

### 2. Execution (During the Sprint)

- Contributors pick up tasks from the sprint board.
- Follow the [Task Workflow](04-task-workflow.md) and [Git Workflow](02-git-workflow.md).
- Update task status as work progresses.
- If a task is blocked, raise it immediately. Fail loudly.

### 3. Review (End of Sprint)

- Demo or summarize completed work.
- Verify acceptance criteria were met.
- Note any incomplete tasks and why (for the retro).

### 4. Retrospective (End of Sprint)

Answer three questions:

1. **What went well?** Keep doing it.
2. **What went poorly?** Fix it.
3. **What should we try next sprint?** Experiment.

Retro outcomes may lead to process changes. Significant process changes are recorded as ADRs.

## Sprint Artifacts

| Artifact | Where | Purpose |
|----------|-------|---------|
| Sprint goal | Sprint planning doc / meeting notes | What we want to achieve |
| Task board | `tasks/` folder or issue tracker | What's in the sprint |
| Sprint notes | `docs/roadmap/sprint-notes/` (optional) | What happened |

## Sprint Goals

Each sprint should have a **goal** — a one-sentence statement of what the sprint aims to achieve. For example:

- "Evaluate vector store options and record an ADR."
- "Prototype the OBD-II parser and ingest pipeline."
- "Establish CI with lint, type, and test checks."

The goal keeps the sprint focused and makes prioritization easier.

## Capacity Planning

- At seed stage, capacity planning is simple: pick a few tasks per person/agent.
- As the team grows, track velocity and use it to plan future sprints.
- Always leave buffer for unexpected work (bugs, research, reviews).

## Working With AI Agents

- **Agents participate in sprints** like humans.
- Agents pick up tasks from the sprint board.
- Agents report progress through PRs and task status updates.
- The sprint review includes agent-contributed work.

## Current State (Seed)

At seed stage:

- Sprints are **optional but recommended.** Even one person benefits from a weekly cadence.
- Sprints can be informal: a short planning note, weekly execution, and a quick review.
- The sprint goal is the most valuable artifact — keep it simple.

## How to Use This Document

1. **At the start of each week**, hold a short planning session and set a sprint goal.
2. **During the week**, execute tasks following the task workflow.
3. **At the end of the week**, review and retrofit.

## Related Documents

- [Task Workflow](04-task-workflow.md) — how tasks are created and completed.
- [Roadmap](../roadmap/README.md) — what we're building toward.
- [Process Overview](01-process-overview.md) — how it all fits together.
- [Future Scaling Philosophy (Engineering)](../engineering/09-future-scaling-philosophy.md) — how processes scale.