# Tasks

## Why This Folder Exists

This folder is the **lightweight task tracking system** for MechAI. It exists so that work is visible, prioritized, and traceable across a growing team of humans and AI agents.

Tasks are the bridge between the roadmap (what we want) and the code (what we build). A well-defined task makes work clear, reviewable, and completable by any contributor.

## How Tasks Work

### 1. Create a Task

Each task gets its own file with a descriptive name:

```
tasks/
├── README.md
├── 01-setup-ci.md
├── 02-research-knowledge-graph.md
└── 03-prototype-obd-parser.md
```

### 2. Document the Task

Each task file follows the structure defined in the [Task Workflow](../docs/processes/04-task-workflow.md):

```markdown
# Task: <Title>

## Why
<Why does this task exist?>

## What
<What needs to be done?>

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Out of Scope
<Optional>

## Related
- Link to relevant docs, ADRs, or issues
```

### 3. Track the Task

Tasks move through states:

```
Backlog → Ready → In Progress → Review → Done
```

Track the state in the task file (e.g., a status line at the top).

## Task States

| State | Description |
|-------|-------------|
| **Backlog** | Defined but not planned for the current sprint. |
| **Ready** | Defined, prioritized, and ready to be picked up. |
| **In Progress** | A contributor is working on it. |
| **Review** | Work is done; PR is under review. |
| **Done** | Merged to main and verified. |

## Priority

Tasks have a priority (see [Priorities](../docs/roadmap/02-priorities.md)):

| Priority | Meaning |
|----------|---------|
| **P0** | Critical; blocks everything. Do now. |
| **P1** | High; important for the current milestone. |
| **P2** | Medium; do when ready. |
| **P3** | Low; nice to have. |

## Rules for Tasks

- **One task = one unit of work.** A task should be completable in hours to a few days.
- **Tasks are specific.** Clear acceptance criteria, not vague goals.
- **Tasks link to the roadmap.** Every task serves a roadmap item.
- **Tasks are updated.** Move them through states as work progresses.
- **Agents use tasks.** AI agents pick up tasks from the Ready backlog.

## How to Use This Folder

1. **Creating a task?** Follow the structure above.
2. **Picking up a task?** Move it to In Progress, create a branch, do the work.
3. **Completing a task?** Open a PR, get review, mark Done.

## Related Documents

- [Task Workflow](../docs/processes/04-task-workflow.md) — the full task process.
- [Sprint Workflow](../docs/processes/05-sprint-workflow.md) — how tasks become sprints.
- [Roadmap](../docs/roadmap/01-roadmap.md) — what we're building.
- [AI Agent Handbook](../docs/agents/01-ai-agent-handbook.md) — how agents use tasks.