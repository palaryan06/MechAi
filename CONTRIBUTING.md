# Contributing to MechAI

Thank you for contributing to MechAI. This document explains how to contribute to this repository — whether you are a human engineer or an AI coding agent.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Roles](#roles)
3. [Getting Started](#getting-started)
4. [Before You Start](#before-you-start)
5. [Making Changes](#making-changes)
6. [Commit & Pull Request Guidelines](#commit--pull-request-guidelines)
7. [Review Expectations](#review-expectations)
8. [Documentation Contribution](#documentation-contribution)
9. [AI Agent Contributions](#ai-agent-contributions)
10. [Definition of Done](#definition-of-done)

## Code of Conduct

Be respectful, constructive, and professional. We are building an engineering organization. Disagreements are welcome; personal attacks are not. Harassment of any kind is unacceptable.

## Roles

| Role | Responsibility |
|------|----------------|
| **Maintainer** | Reviews and merges pull requests, enforces standards, maintains the roadmap |
| **Contributor** | Any human or AI agent that proposes changes via a pull request |
| **Reviewer** | Someone who reviews a pull request; may be a maintainer or a peer |

## Getting Started

1. Read the [README](README.md) and the [Repository Guide](docs/architecture/02-repository-guide.md).
2. Read the [Engineering Handbook](docs/engineering/01-engineering-handbook.md).
3. Read the [AI Agent Handbook](docs/agents/01-ai-agent-handbook.md) if you are an agent.
4. Clone the repository and create a working branch (see [Git Workflow](docs/processes/02-git-workflow.md)).

## Before You Start

- **Check the roadmap** ([docs/roadmap/](docs/roadmap/)) to ensure your work aligns with priorities.
- **Check existing issues/tasks** if an issue tracker exists. Avoid duplicating work.
- **For significant changes**, open a discussion or draft an ADR before implementing. Significant means: changing the architecture, adding a major dependency, altering the data model, or changing public interfaces.

## Making Changes

1. **Branch:** Create a descriptive branch from `main` (e.g. `feat/obd-parser`, `docs/architecture-v2`).
2. **Small, focused changes:** Prefer small pull requests. A single PR should do one thing well.
3. **Follow standards:** Read [Coding Standards](docs/engineering/03-coding-standards.md). Formatting, naming, and style must be consistent.
4. **Write tests:** New product logic must include unit tests. See [Testing Philosophy](docs/engineering/05-testing-philosophy.md).
5. **Update documentation:** If behavior changes, update the relevant docs. If a decision is important, add an ADR.

## Commit & Pull Request Guidelines

See the full [Git Workflow](docs/processes/02-git-workflow.md) and [Branch Strategy](docs/processes/03-branch-strategy.md).

In brief:

- Use [Conventional Commits](docs/processes/02-git-workflow.md#conventional-commits): `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`.
- Keep commit messages imperative and descriptive.
- One logical change per commit.
- Write a PR description that explains **what** and **why**.

## Review Expectations

- **All PRs require at least one approval** from a maintainer before merge.
- **Reviewers:** Be kind, specific, and provide rationale. Use inline comments.
- **Authors:** Be responsive. Address feedback or explain disagreements.

## Documentation Contribution

Documentation is part of the codebase. When contributing docs:

- Follow the style in [Documentation Standards](docs/engineering/07-documentation-standards.md).
- Place docs in the correct folder (see [Repository Guide](docs/architecture/02-repository-guide.md)).
- Keep explanations clear and purposeful. Avoid fluff.
- Include diagrams where they clarify.

## AI Agent Contributions

AI coding agents (e.g. Cline, Copilot, other tooling) are first-class contributors.

- **Agents must read** the [AI Agent Handbook](docs/agents/01-ai-agent-handbook.md) before starting work.
- **Agents must record task context** in the [Memory System](docs/agents/02-memory-system.md).
- **Agents must never** commit secrets, large binaries, or local state.
- **Agents must follow** the same coding standards, git conventions, and review process as humans.

## Definition of Done

A contribution is "done" when:

- [ ] Code compiles and passes all tests
- [ ] New code has unit tests (where applicable)
- [ ] Coding standards are followed
- [ ] Documentation is updated if behavior changed
- [ ] No secrets, binaries, or local state are committed
- [ ] Commit messages follow Conventional Commits
- [ ] Pull request is approved by at least one maintainer
- [ ] Branch is up-to-date with `main`
- [ ] (If applicable) An ADR entry exists for significant decisions

*Thank you for helping build the world's most intelligent AI mechanic.*