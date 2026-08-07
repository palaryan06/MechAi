# Tests

## Purpose

This directory contains the automated test suite for MechAI.

## Test Structure

```
tests/
├── __init__.py           # Test package marker
├── conftest.py           # Shared fixtures (env isolation, cache resets)
├── test_cli.py           # CLI and entry point tests
├── test_config.py        # Configuration loading and validation tests
├── test_exceptions.py    # Custom exception hierarchy tests
├── test_logging.py       # Structured logging setup tests
└── test_version.py       # Version format and export tests
```

## Running Tests

Run all unit tests with coverage:

```bash
python -m pytest tests/ -v --cov=mechai --cov-report=term-missing
```

Run specific test files:

```bash
python -m pytest tests/test_config.py -v
python -m pytest tests/test_cli.py -v
```

## Testing Rules

1. **Test behavior, not implementation.** (See [`docs/engineering/05-testing-philosophy.md`](../docs/engineering/05-testing-philosophy.md)).
2. **Never use real customer data or real vehicle VINs in tests.** Use synthetic data.
3. **Keep tests isolated and fast.** Use fixtures in `conftest.py` for isolation.