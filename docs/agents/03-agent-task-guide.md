# Agent Task Guide

## Why This Document Exists

This document is the **step-by-step guide for AI agents executing a task** in the MechAI repository. It complements the [AI Agent Handbook](01-ai-agent-handbook.md) (the rules) by providing the concrete workflow (the how). Use this when you have been given a task and need to execute it properly.

## The Agent Task Lifecycle

```
Receive → Understand → Prepare → Execute → Submit → Persist
```

## Step 1: Receive the Task

Tasks come from:

- A human assigning you a task directly.
- A task file in [`tasks/`](../../tasks/README.md) marked **Ready**.
- A roadmap item broken down into a task.

If the task is ambiguous, **ask for clarification** before starting.

## Step 2: Understand the Task

1. **Read** the task description and acceptance criteria.
2. **Check** the [Memory System](02-memory-system.md) for related prior work.
3. **Read** the relevant docs:
   - [Engineering Handbook](../engineering/01-engineering-handbook.md)
   - [Repository Guide](../architecture/02-repository-guide.md)
   - Domain-specific docs as needed.
4. **Identify** files and areas that will be touched.
5. **Confirm** the task aligns with the [Roadmap](../roadmap/README.md).

## Step 3: Prepare

### Create a Branch

```bash
git checkout main
git pull
git checkout -b feat/obd-parser
```

Use the correct branch type prefix (see [Branch Strategy](../processes/03-branch-strategy.md)).

### Plan the Work

- Break the task into small, logical steps.
- Identify what tests, docs, and ADRs are needed.
- Identify any unknowns; resolve them before starting.

## Step 4: Execute

### Follow the Standards

- [Coding Standards](../engineering/03-coding-standards.md)
- [Naming Conventions](../engineering/02-naming-conventions.md)
- [Testing Philosophy](../engineering/05-testing-philosophy.md)

### Make Focused Commits

Use [Conventional Commits](../processes/02-git-workflow.md#conventional-commits):

```
feat(obd): add DTC parser
```

### Test Your Work

- Write tests for new logic.
- Run the test suite and linting.
- Ensure the tests pass.

### Update Docs

- If behavior or architecture changed, update the relevant docs.
- If a significant decision was made, write an ADR (see [ADR System](../adr/README.md)).

## Step 5: Submit

### Open a PR

- Push your branch.
- Open a PR to `main`.
- Write a clear description: **what**, **why**, **how tested**, **docs changed**, **ADR needed**.

### Wait for Review

- **Do not merge without approval.**
- Address feedback promptly.
- If feedback requires significant rework, coordinate with the reviewer.

## Step 6: Persist Context

After the work is complete:

1. **Update** relevant memory files (see [Memory System](02-memory-system.md)).
2. **Append** to `memory/05-agent-sessions.md` with a session log.
3. **Add** any open questions to `memory/06-open-questions.md`.
4. **Update** the task file to **Done** (if it's a tracked task).

## Task-Specific Considerations

### Documentation Task

- Read [Documentation Standards](../engineering/07-documentation-standards.md).
- Follow the doc structure and naming conventions.
- Ensure links are correct.

### Research Task

- Record findings in [`docs/research/`](../research/README.md) or an experiment (see [`experiments/`](../../experiments/README.md)).
- Be explicit about what was tested, what was found, and what remains open.

### Bug Fix Task

- Reproduce the bug first (write a failing test).
- Fix the bug.
- Confirm the test passes and the bug is resolved.

### Feature Task

- Understand the acceptance criteria.
- Design the implementation (consider an ADR if significant).
- Implement, test, and document.

## Handling Blockers

If you are blocked:

1. **Identify** the blocker (missing information, access, conflicting work, unclear requirement).
2. **Try** to resolve it yourself (read docs, check memory, check PRs).
3. **Escalate** to a human with a clear, specific question.
4. **Do not** guess or work around a blocker destructively.

## Definition of Done

A task is done when:

- [ ] Acceptance criteria met
- [ ] Code follows standards
- [ ] Tests written and passing
- [ ] Docs updated if behavior changed
- [ ] PR opened, reviewed, and approved
- [ ] Memory updated
- [ ] Task marked Done

## Related Documents

- [AI Agent Handbook](01-ai-agent-handbook.md) — the rules.
- [Memory System](02-memory-system.md) — how to persist context.
- [Task Workflow](../processes/04-task-workflow.md) — how tasks are tracked.
- [Git Workflow](../processes/02-git-workflow.md) — commits and PRs.