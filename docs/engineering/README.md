# Engineering Standards & Philosophies

## Why This Folder Exists

This folder contains the **engineering standards and philosophies** for MechAI. It defines *how* we write, test, log, configure, secure, and document software. It is the concrete implementation of the [Development Philosophy](../04-development-philosophy.md).

Every contributor — human or AI agent — must follow these standards. They exist to keep the codebase maintainable, consistent, and safe as the team grows.

## Documents in This Folder

| Document | Purpose |
|----------|---------|
| [`01-engineering-handbook.md`](01-engineering-handbook.md) | The core handbook: how we work, what we value, and the rules we follow. |
| [`02-naming-conventions.md`](02-naming-conventions.md) | Naming conventions for files, folders, code, branches, and more. |
| [`03-coding-standards.md`](03-coding-standards.md) | How code should look and be structured (Python-focused for now). |
| [`04-logging-philosophy.md`](04-logging-philosophy.md) | How we log: structured, contextual, and useful. |
| [`05-testing-philosophy.md`](05-testing-philosophy.md) | How we test: what to test, how, and why. |
| [`06-configuration-philosophy.md`](06-configuration-philosophy.md) | How we manage configuration and secrets. |
| [`07-documentation-standards.md`](07-documentation-standards.md) | How we write documentation. |
| [`08-security-philosophy.md`](08-security-philosophy.md) | How we think about security in code and architecture. |
| [`09-future-scaling-philosophy.md`](09-future-scaling-philosophy.md) | How our engineering practices scale with the team. |

## How to Use This Folder

1. **New engineers and agents** read the [Engineering Handbook](01-engineering-handbook.md) first.
2. **Writing code?** Read [Coding Standards](03-coding-standards.md) and [Naming Conventions](02-naming-conventions.md).
3. **Writing tests?** Read [Testing Philosophy](05-testing-philosophy.md).
4. **Adding logging?** Read [Logging Philosophy](04-logging-philosophy.md).
5. **Adding configuration?** Read [Configuration Philosophy](06-configuration-philosophy.md).
6. **Writing docs?** Read [Documentation Standards](07-documentation-standards.md).
7. **Thinking about security?** Read [Security Philosophy](08-security-philosophy.md).

## Relationship to Other Folders

- **Processes** ([`../processes/`](../processes/)) define *how we work* (git, branches, tasks, sprints). Engineering standards define *how we build*.
- **ADRs** ([`../adr/`](../adr/)) record significant decisions. If a standard changes significantly, it gets an ADR.
- **Architecture** ([`../architecture/`](../architecture/)) describes the system design. Engineering standards describe how we implement it.

*This folder is a living part of the repository. Standards evolve as the team learns.*