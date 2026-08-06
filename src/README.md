# Source Code

## Why This Folder Exists

This folder is the **future home of MechAI's product source code**. It exists as a placeholder to establish the structure before product code arrives.

**The repository is intentionally foundation-only.** No product code exists yet. This folder is reserved for when the Python project is scaffolded (Phase 0/1).

## When Product Code Arrives

When the Python project is scaffolded, this folder will contain the `mechai` package following the [Coding Standards](../docs/engineering/03-coding-standards.md) and the [Repository Guide](../docs/architecture/02-repository-guide.md).

The planned structure (from the [Coding Standards](../docs/engineering/03-coding-standards.md)):

```
src/mechai/
├── __init__.py
├── ingestion/
├── knowledge/
├── reasoning/
└── common/
```

## Rules

- **Do not create product code here yet.** The Python project has not been scaffolded.
- **Use `experiments/` for prototypes** until the project is scaffolded.
- **Follow the [Coding Standards](../docs/engineering/03-coding-standards.md)** when code arrives.

## Related Documents

- [Coding Standards](../docs/engineering/03-coding-standards.md)
- [Repository Guide](../docs/architecture/02-repository-guide.md)
- [Roadmap](../docs/roadmap/01-roadmap.md)