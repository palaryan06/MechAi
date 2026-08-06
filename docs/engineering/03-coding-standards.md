# Coding Standards

## Why This Document Exists

This document defines **how code should look and be structured** in the MechAI codebase. It exists so that any contributor — human or AI agent — writes code that is consistent, readable, and maintainable.

The repository currently contains no product code. This document defines the standards that will apply when product code arrives. It is Python-focused because Python is the declared primary language (see [Architecture Overview](../architecture/01-architecture-overview.md)).

## General Principles

1. **Readability over cleverness.** Code is written for humans (and agents) to read.
2. **Consistency over preference.** Follow the existing patterns.
3. **Small, focused modules.** One module does one thing well.
4. **Type hints everywhere.** Python code is fully typed.
5. **No dead code.** Delete what isn't used.

## Language & Tooling (Python)

| Tool | Purpose | Standard |
|------|---------|----------|
| **Python** | Language | 3.11+ (pin exact version in tooling) |
| **Ruff** | Linter + formatter | Default rules + project config |
| **Mypy** | Type checker | Strict mode |
| **Pytest** | Test runner | Standard pytest conventions |
| **Poetry / uv** | Dependency management | Pin dependencies; lock file committed |

*Exact tool versions and config will be defined when the Python project is scaffolded (see ADR-0005, planned).*

## Code Structure

### Module Layout

```
src/mechai/
├── __init__.py
├── ingestion/
│   ├── __init__.py
│   ├── document_parser.py
│   └── obd_parser.py
├── knowledge/
│   ├── __init__.py
│   ├── graph.py
│   └── extraction.py
├── reasoning/
│   ├── __init__.py
│   ├── query.py
│   └── causal.py
└── common/
    ├── __init__.py
    ├── logging.py
    └── config.py
```

### File Structure

Every Python file follows this order:

1. Module docstring (what this module does, why it exists).
2. Imports (stdlib, third-party, local — grouped and sorted).
3. Constants.
4. Types / type aliases.
5. Classes.
6. Functions.

### Docstrings

- **Every module** has a docstring explaining its purpose.
- **Every public function/class** has a docstring explaining what it does, its parameters, and its return value.
- Use Google-style docstrings.

```python
def extract_entities(text: str) -> list[Entity]:
    """Extract automotive entities from text.

    Args:
        text: The source text to analyze.

    Returns:
        A list of extracted entities.

    Raises:
        ExtractionError: If the text cannot be parsed.
    """
```

## Naming

Follow the [Naming Conventions](02-naming-conventions.md). Key points:

- `snake_case` for modules, functions, variables.
- `PascalCase` for classes.
- `UPPER_SNAKE_CASE` for constants.
- Leading underscore for private members.

## Type Hints

- **All** function signatures have type hints.
- **All** public APIs are fully typed.
- Use `list[...]`, `dict[...]`, `Optional[...]` (or `X | None` in 3.10+).
- Use `TypeAlias` for complex types.

```python
from typing import TypeAlias

VehicleId: TypeAlias = str
DiagnosticCode: TypeAlias = str

def get_dtc(vehicle_id: VehicleId) -> DiagnosticCode | None:
    ...
```

## Error Handling

- **Raise specific exceptions.** Never `raise Exception`.
- **Define custom exceptions** in a `exceptions.py` module per package.
- **Catch specific exceptions.** Never bare `except:`.
- **Fail loudly.** Don't swallow errors silently.

```python
class IngestionError(Exception):
    """Base error for ingestion failures."""

class DocumentParseError(IngestionError):
    """Raised when a document cannot be parsed."""
```

## Logging

- Use the project's structured logging setup (see [Logging Philosophy](04-logging-philosophy.md)).
- Never `print()` for logging.
- Include context: `logger.info("parsed document", doc_id=doc_id, pages=count)`.

## Testing

- Tests live in `tests/`, mirroring `src/`.
- Test files: `test_<module>.py`.
- Test functions: `test_<behavior>`.
- Follow the [Testing Philosophy](05-testing-philosophy.md).

## Configuration

- Configuration is read from environment variables (see [Configuration Philosophy](06-configuration-philosophy.md)).
- Never hardcode secrets or environment-specific values.

## Comments

- **Comments explain why, not what.** The code should be self-explanatory for *what*.
- **Use comments for non-obvious decisions**, trade-offs, and gotchas.
- **Avoid commented-out code.** Delete it.

## What to Avoid

- **Global mutable state.** Prefer dependency injection.
- **Magic numbers.** Use named constants.
- **Deep nesting.** Refactor into smaller functions.
- **Long functions.** If a function exceeds ~50 lines, consider splitting it.
- **Premature optimization.** Write clear code first; optimize with evidence.

## Code Review Checklist

When reviewing code, check:

- [ ] Follows naming conventions
- [ ] Fully typed
- [ ] Has docstrings
- [ ] Handles errors specifically
- [ ] Logs with context
- [ ] Has tests
- [ ] No secrets or hardcoded config
- [ ] No dead code
- [ ] Readable and simple

## How to Use This Document

1. **Before writing code**, read this document.
2. **When reviewing code**, use the checklist above.
3. **When you see a violation**, fix it in a small, focused PR.

## Related Documents

- [Naming Conventions](02-naming-conventions.md) — how to name things.
- [Testing Philosophy](05-testing-philosophy.md) — how to test.
- [Logging Philosophy](04-logging-philosophy.md) — how to log.
- [Configuration Philosophy](06-configuration-philosophy.md) — how to configure.
- [Engineering Handbook](01-engineering-handbook.md) — the core rules.