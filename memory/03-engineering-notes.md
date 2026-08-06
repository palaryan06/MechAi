# Engineering Notes

## Why This File Exists

This file stores **engineering conventions, tooling, and gotchas** for AI agents. It captures the practical knowledge that makes working in this repository efficient. Agents should read this before writing code.

## Conventions

- **Naming:** Follow [Naming Conventions](../docs/engineering/02-naming-conventions.md). Folders are `kebab-case`; docs are `NN-name.md`; branches are `type/description`.
- **Commits:** Use [Conventional Commits](../docs/processes/02-git-workflow.md#conventional-commits). One logical change per commit.
- **Branches:** Never work directly on `main`. Use a branch + PR.
- **Docs:** Documentation is code. Update docs when behavior changes.

## Tooling (Planned)

The Python tooling is specified in [Coding Standards](../docs/engineering/03-coding-standards.md) but not yet installed (no product code yet):

| Tool | Purpose |
|------|---------|
| Ruff | Linter + formatter |
| mypy | Type checker (strict) |
| pytest | Test runner |
| Poetry / uv | Dependency management |

## Gotchas

- **The repository is foundation-only.** No product code exists yet. Don't create product code in `src/` until the Python project is scaffolded.
- **Use `experiments/` for prototypes**, not `src/`.
- **Never commit secrets, PII, or vehicle data.** Use synthetic data.
- **Mermaid diagrams** render on GitHub — use them for architecture docs.
- **Relative links** in docs must be correct. A broken link is a bug.

## Status

- **Last updated:** 2026-08-03
- **Status:** Active