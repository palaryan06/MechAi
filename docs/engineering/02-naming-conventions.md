# Naming Conventions

## Why This Document Exists

Consistent naming is one of the cheapest ways to keep a codebase maintainable. This document defines the naming conventions for MechAI across files, folders, code, branches, and documentation. It exists so that any contributor — human or AI agent — can name things correctly without guessing.

## General Principles

1. **Be descriptive, not clever.** A name should tell you what something is or does.
2. **Be consistent.** If a pattern exists, follow it.
3. **Prefer clarity over brevity.** `vehicle_state_store` is better than `vss`.
4. **Use the language's conventions.** Python uses `snake_case`; JavaScript uses `camelCase`; etc.

## Folder Naming

| Context | Convention | Example |
|---------|------------|---------|
| Repository folders | `kebab-case` | `docs/architecture/`, `experiments/` |
| Python packages (future) | `snake_case` | `src/mechai/ingestion/` |
| Test folders (future) | Mirror source | `tests/mechai/ingestion/` |

## File Naming

| Context | Convention | Example |
|---------|------------|---------|
| Markdown docs | `NN-name.md` (zero-padded sequence) | `01-vision.md`, `02-mission.md` |
| Python source (future) | `snake_case.py` | `obd_parser.py` |
| Python tests (future) | `test_<module>.py` | `test_obd_parser.py` |
| Config files | `kebab-case` or `snake_case` | `pyproject.toml`, `docker-compose.yml` |
| Environment templates | `.env.example` | `.env.example` |

## Code Naming (Python, Future)

| Construct | Convention | Example |
|-----------|------------|---------|
| Module | `snake_case` | `knowledge_graph.py` |
| Class | `PascalCase` | `KnowledgeGraph` |
| Function | `snake_case` | `extract_entities()` |
| Variable | `snake_case` | `vehicle_state` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Private (module/class) | Leading underscore | `_internal_helper()` |
| Type alias | `PascalCase` | `VehicleId = str` |
| Enum member | `UPPER_SNAKE_CASE` | `FAILURE_MODE.ELECTRICAL` |

## Branch Naming

| Type | Convention | Example |
|------|------------|---------|
| Feature | `feat/<description>` | `feat/obd-parser` |
| Fix | `fix/<description>` | `fix/vector-store-timeout` |
| Docs | `docs/<description>` | `docs/architecture-v2` |
| Refactor | `refactor/<description>` | `refactor/ingestion-pipeline` |
| Test | `test/<description>` | `test/knowledge-graph` |
| Chore | `chore/<description>` | `chore/update-deps` |
| Experiment | `exp/<description>` | `exp/embedding-benchmark` |

Use `kebab-case` for branch descriptions.

## Commit Message Naming

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <description>

[optional body]
```

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

**Examples:**
- `feat(obd): add DTC parser`
- `fix(vector-store): handle timeout on large queries`
- `docs(adr): add ADR-0006 for vector store selection`

## Documentation Naming

- **Docs folders:** `kebab-case` (e.g., `architecture/`, `engineering/`).
- **Doc files:** `NN-name.md` with zero-padded sequence numbers for ordering.
- **ADRs:** `NNNN-name.md` (e.g., `0001-knowledge-graph-core.md`). See [ADR System](../adr/README.md).
- **Experiments:** `NN-name/` folders (e.g., `01-embedding-benchmark/`).
- **Prompts:** `NN-name.md` (e.g., `01-diagnosis-prompt.md`).
- **Tasks:** `NN-name.md` (e.g., `01-setup-ci.md`).

## Database / Data Naming (Future)

| Construct | Convention | Example |
|-----------|------------|---------|
| Table | `snake_case`, plural | `vehicles`, `diagnostic_codes` |
| Column | `snake_case` | `vehicle_id`, `dtc_code` |
| Index | `idx_<table>_<column>` | `idx_vehicles_vin` |
| Foreign key | `<singular>_id` | `vehicle_id` |
| Graph node label | `PascalCase` | `Component`, `FailureMode` |
| Graph relationship | `UPPER_SNAKE_CASE` | `CAUSES`, `PART_OF` |

## API Naming (Future)

| Construct | Convention | Example |
|-----------|------------|---------|
| Endpoint | `kebab-case` | `/api/v1/vehicles/{id}/diagnostics` |
| JSON field | `snake_case` | `"diagnostic_code"` |
| Query param | `snake_case` | `?include_sources=true` |

## Environment Variable Naming

| Convention | Example |
|------------|---------|
| `UPPER_SNAKE_CASE` with `MECHAI_` prefix | `MECHAI_DB_HOST`, `MECHAI_LOG_LEVEL` |
| No secrets in `.env.example` | Document the variable, not the value |

## What to Avoid

- **Abbreviations** unless universally understood (`id`, `db`, `api`).
- **Hungarian notation** (`strName`, `intCount`).
- **Inconsistent casing** within the same context.
- **Overly generic names** (`data`, `info`, `temp`, `thing`).
- **Names that lie** — a name must match what the thing actually is.

## How to Use This Document

1. **Before naming anything**, check this document for the relevant convention.
2. **When in doubt**, prefer the more descriptive name.
3. **When you see a violation**, fix it in a small, focused PR.

## Related Documents

- [Coding Standards](03-coding-standards.md) — how code is structured.
- [Git Workflow](../processes/02-git-workflow.md) — commit conventions.
- [Branch Strategy](../processes/03-branch-strategy.md) — branch naming.
- [Documentation Standards](07-documentation-standards.md) — doc naming.