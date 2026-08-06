# Task Workflow

## Why This Document Exists

This document defines **how we track and complete units of work** in MechAI. It exists so that work is visible, prioritized, and traceable across a growing team of humans and AI agents.

Tasks are the bridge between the roadmap (what we want) and the code (what we build). A well-defined task makes work clear, reviewable, and completable by any contributor.

## What Is a Task?

A task is a **single unit of work** that can be completed by one contributor in a reasonable timeframe (hours to a few days). Tasks live as markdown files in [`tasks/`](../../tasks/).

## Task Structure

Each task file follows this structure:

```markdown
# Task: <Title>

## Why
<Why does this task exist? What problem does it solve?>

## What
<What needs to be done? Describe the work clearly and specifically.>

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Out of Scope
<Optional: what is explicitly NOT part of this task?>

## Related
- Link to relevant docs, ADRs, or issues
```

## Task Lifecycle

```
Backlog → Ready → In Progress → Review → Done
```

| State | Description |
|-------|-------------|
| **Backlog** | Task is defined but not planned for the current sprint. |
| **Ready** | Task is defined, prioritized, and ready to be picked up. |
| **In Progress** | A contributor is working on it. |
| **Review** | Work is done; PR is under review. |
| **Done** | Merged to main and verified. |

Task state is tracked in the task file (e.g., a status line) or in an issue tracker when one is adopted.

## Creating a Task

To create a task:

1. Create a file in `tasks/` with a descriptive name (see [Naming Conventions](../engineering/02-naming-conventions.md)).
2. Fill in the structure above.
3. Link it to the roadmap item it serves (see [Roadmap](../roadmap/README.md)).
4. Add it to the backlog.

When to create a task:
- A roadmap item needs to be broken down.
- A bug needs fixing.
- A piece of research needs to be done.
- Documentation needs writing.

## Picking Up a Task

1. Choose a task from the **Ready** backlog.
2. Move it to **In Progress**.
3. Create a branch (see [Branch Strategy](03-branch-strategy.md)).
4. Complete the work.
5. Open a PR (see [Git Workflow](02-git-workflow.md)).
6. Move the task to **Review**.
7. After merge, verify and move to **Done**.

## Task Sizing

Tasks should be **sizable but completable**:

- A task that takes a few hours to a few days.
- If a task is too big (weeks), break it into subtasks.
- If a task is tiny (minutes), consider bundling related tiny tasks.

## Writing Good Acceptance Criteria

Good acceptance criteria are:

- **Specific:** "The parser returns a `DiagnosticCode` for valid PIDs."
- **Testable:** "Unit tests cover valid and malformed frames."
- **Focused:** "The `docs/` folder is updated for the new behavior."

Avoid vague criteria like "make it work" or "improve performance."

## Working With AI Agents

- **Agents pick up tasks** from the **Ready** backlog like humans.
- **Agents create a branch**, do the work, and open a PR.
- **Agents update the task file** as they make progress.
- **Agents record context** in the [Memory System](../agents/02-memory-system.md) for future sessions.

## Priority

Tasks have a priority:

| Priority | Meaning |
|----------|---------|
| **P0** | Critical; blocks everything. Do now. |
| **P1** | High; important for the current milestone. |
| **P2** | Medium; do when ready. |
| **P3** | Low; nice to have. |

Priority is set by the product lead / maintainer and reviewed at sprint planning.

## How to Use This Document

1. **Before creating a task**, read the structure above.
2. **Before picking up a task**, move it to Ready/In Progress.
3. **While working**, update the task state.
4. **After merging**, move it to Done.

## Related Documents

- [Sprint Workflow](05-sprint-workflow.md) — how tasks are planned into sprints.
- [Branch Strategy](03-branch-strategy.md) — creating a branch for a task.
- [Git Workflow](02-git-workflow.md) — PRs and merges.
- [Repository Guide](../architecture/02-repository-guide.md) — the `tasks/` folder.