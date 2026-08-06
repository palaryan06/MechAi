# Branch Strategy

## Why This Document Exists

This document defines **how we create and manage branches** in MechAI. It exists to keep the repository history clean, to make work parallelizable across a growing team of humans and AI agents, and to ensure `main` is always releasable.

## The Model: Trunk-Based Development

We use a **lightweight trunk-based development** model:

- **`main`** is the trunk. It is always releasable.
- **Short-lived feature branches** branch from `main` and merge back quickly.
- **No long-running branches.** Work is kept small and merged frequently.

```
main:  ──●──●──●──●──●──●──
           \        /
feat:       ●──●──●
           feat-x

main:  ──●──●──●──●──●──●──
           \        /
fix:        ●──●
           fix-y
```

## Protected Branches

| Branch | Protected? | Notes |
|--------|------------|-------|
| `main` | Yes | Only merged via reviewed PRs. Never force-pushed. |

## Branch Types and Naming

| Type | Prefix | Example | Description |
|------|--------|---------|-------------|
| Feature | `feat/` | `feat/obd-parser` | A new feature |
| Fix | `fix/` | `fix/vector-store-timeout` | A bug fix |
| Docs | `docs/` | `docs/architecture-v2` | Documentation changes |
| Refactor | `refactor/` | `refactor/ingestion-pipeline` | Code refactoring |
| Test | `test/` | `test/knowledge-graph` | Adding/updating tests |
| Chore | `chore/` | `chore/update-deps` | Maintenance tasks |
| Experiment | `exp/` | `exp/embedding-benchmark` | Research/experimentation |

Use `kebab-case` for the description. Branch names should be short but descriptive.

## Branch Lifecycle

### 1. Create

Branch from the latest `main`:

```bash
git checkout main
git pull
git checkout -b feat/obd-parser
```

### 2. Work

Make small, focused commits (see [Git Workflow](02-git-workflow.md)).

### 3. Keep Updated

Frequently rebase onto `main` to avoid drift:

```bash
git fetch origin
git rebase origin/main
```

Prefer `rebase` over `merge` to keep history linear. If a rebase is complex and you need to collaborate with others on the branch, coordinate with the team.

### 4. Push and Open PR

Push the branch and open a PR to `main`.

### 5. Merge and Delete

After approval and green CI:

- Prefer **squash merge** (clean history).
- **Delete the branch** after merging.

## Branch Rules

1. **Never commit directly to `main`.** Always go through a PR.
2. **Keep branches short-lived.** Target a few days or less. Split large work into smaller PRs.
3. **One branch = one logical piece of work.** Don't mix unrelated changes.
4. **Rebase onto `main` frequently.** Avoid long-lived branches that diverge.
5. **Never force-push to shared branches.** You may force-push to your own feature branch before review.

## Hotfixes

In an emergency (e.g., a critical security fix on main):

1. Create a branch from `main`: `fix/critical-security`.
2. Fix, test, open a PR.
3. Get maintainer approval and merge quickly.

Hotfixes are rare and should never be the norm. The goal is to keep `main` healthy so normal workflow is fast.

## Working With AI Agents

- **Agents follow the same branch strategy.**
- Agents must **never commit directly to `main`.**
- Agents must create a branch, open a PR, and wait for review like any human.
- If an agent needs to force-push, it should be on its own feature branch only.

## How to Use This Document

1. **Before starting work**, create a correctly named branch.
2. **While working**, keep the branch small, focused, and rebased.
3. **After merging**, delete the branch.

## Related Documents

- [Git Workflow](02-git-workflow.md) — commits and PRs.
- [Task Workflow](04-task-workflow.md) — how work is tracked.
- [Naming Conventions](../engineering/02-naming-conventions.md) — branch naming.
- [Process Overview](01-process-overview.md) — how it all fits together.