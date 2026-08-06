# Git Workflow

## Why This Document Exists

This document defines **how we use git** in MechAI. It exists so that every contributor — human or AI agent — creates clear, reviewable, and reversible history. A consistent git workflow is essential as the team grows and multiple contributors touch the same files.

## Core Rules

1. **`main` is always releasable.** Never merge broken or incomplete work to main.
2. **One logical change per commit.** Each commit does one thing.
3. **Small, focused PRs.** A PR is easier to review when it does one thing well.
4. **Conventional commits.** Commit messages follow the Conventional Commits spec.
5. **Rebase-friendly history.** Prefer clean, readable history over tangled branches.
6. **Never force-push to shared branches.** `main` is protected.

## The Basic Loop

### 1. Create a branch

```bash
git checkout -b feat/obd-parser
```

See [Branch Strategy](03-branch-strategy.md) for naming.

### 2. Make focused commits

```bash
git add src/mechai/ingestion/obd_parser.py
git commit -m "feat(obd): add DTC parser"
```

### 3. Keep your branch up to date

```bash
git fetch origin
git rebase origin/main
```

Prefer `rebase` over `merge` for a clean history. When in doubt, ask a maintainer.

### 4. Push and open a PR

```bash
git push -u origin feat/obd-parser
```

Open a PR to `main` with a clear title and description (see below).

### 5. Review and merge

- Get at least one approval.
- Ensure CI is green (once CI exists).
- Merge (prefer squash merge for a clean history) or ask a maintainer to merge.

## Conventional Commits

Format:

```
<type>(<optional scope>): <description>

[optional body]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes |
| `refactor` | Code change that doesn't fix a bug or add a feature |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks (deps, tooling) |
| `perf` | Performance improvement |
| `build` | Build system or dependency changes |
| `ci` | CI configuration changes |

### Scope

Scope is optional but recommended when it adds clarity:

- `feat(obd): add DTC parser`
- `fix(vector-store): handle timeout on large queries`
- `docs(adr): add ADR-0006`

### Examples

```bash
git commit -m "feat(obd): add DTC parser"

git commit -m "fix(ingestion): handle malformed PDFs

PDF parser now raises DocumentParseError instead of crashing
on corrupt files. Added test coverage for the failure path."
```

## Writing Good Commit Messages

- **Imperative mood:** "add parser", not "added parser" or "adds parser".
- **Describe the why when non-obvious:** the body explains the reasoning.
- **Keep the subject under ~50 characters** when possible.
- **One logical change per commit.**

## Branch Hygiene

- **Delete your branch after merging.**
- **Keep branches short-lived.** Long-running branches drift from main. Prefer small increments.
- **Never commit directly to `main`.** Always go through a PR (except emergency hotfixes with maintainer approval).

## Pull Requests

### PR Title

`<type>(<scope>): <description>` — same as a commit, but describes the whole change.

### PR Description

A good PR description answers:

1. **What** does this change do?
2. **Why** is it needed?
3. **How** was it tested?
4. **Does it change any docs?** (Linked docs updated in this PR.)
5. **Does it need an ADR?** (If significant, link the ADR.)

### PR Checklist

- [ ] CI green (once CI exists)
- [ ] Tests added/updated
- [ ] Docs updated if behavior changed
- [ ] Code follows [Coding Standards](../engineering/03-coding-standards.md)
- [ ] No secrets, binaries, or local state committed
- [ ] At least one approval

## Merge Strategy

Prefer **squash merge** for most PRs. This produces a clean, single commit per feature on `main`, making history readable and revertable.

Rebase merge is acceptable for well-organized multi-commit PRs when a maintainer prefers commit granularity.

## Undoing Work

- **Before push (local):** `git reset --soft HEAD~1` to undo the last commit, keep changes.
- **Before merge (on PR):** fix forward with a new commit, or rebase and amend.
- **After merge (on main):** revert with `git revert <commit>`. Never rewrite shared history.

## What to Never Commit

- **Secrets** (API keys, tokens, `.env`, `*.pem`).
- **Large binaries** (models, data, images).
- **Local state** (IDE config, caches, logs).
- **Sensitive data** (real VINs, PII, customer data).

`.gitignore` covers most of these, but always check your staged files:

```bash
git status
git diff --cached
```

## How to Use This Document

1. **Before making a commit**, review the Conventional Commits types.
2. **Before opening a PR**, go through the checklist.
3. **When you make a mistake**, follow the "Undoing Work" section.

## Related Documents

- [Branch Strategy](03-branch-strategy.md) — how branches are named and managed.
- [Task Workflow](04-task-workflow.md) — how work is tracked.
- [Naming Conventions](../engineering/02-naming-conventions.md) — commit conventions.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — the contribution process.