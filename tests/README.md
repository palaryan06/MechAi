# Tests

## Why This Folder Exists

This folder is the **future home of MechAI's test suite**. It exists as a placeholder to establish the structure before product code arrives.

**The repository is intentionally foundation-only.** No product code or tests exist yet. This folder is reserved for when the Python project is scaffolded (Phase 0/1).

## When Tests Arrive

When the Python project is scaffolded, tests will live here, mirroring the `src/` structure:

```
tests/
├── mechai/
│   ├── ingestion/
│   ├── knowledge/
│   ├── reasoning/
│   └── common/
```

Tests follow the [Testing Philosophy](../docs/engineering/05-testing-philosophy.md).

## Rules

- **Do not create tests here yet.** The Python project has not been scaffolded.
- **Use `experiments/` for prototypes** until the project is scaffolded.
- **Follow the [Testing Philosophy](../docs/engineering/05-testing-philosophy.md)** when tests arrive.
- **Never use real customer data or VINs in tests.** Use synthetic data.

## Related Documents

- [Testing Philosophy](../docs/engineering/05-testing-philosophy.md)
- [Coding Standards](../docs/engineering/03-coding-standards.md)
- [Repository Guide](../docs/architecture/02-repository-guide.md)