# Source Code

## Overview

This folder contains the core `mechai` Python package, implementing the engineering foundation for the MechAI Automotive Diagnostic Reasoning Engine.

## Package Layout

```
src/mechai/
├── __init__.py           # Package version and root exports
├── __main__.py           # Module execution entry point (python -m mechai)
├── cli.py                # Command-line interface and argument parsing
├── main.py               # Application entry point
├── common/               # Shared foundational utilities
│   ├── __init__.py       # Foundation utilities exports
│   ├── config.py         # Pydantic Settings configuration loader
│   ├── exceptions.py     # Root MechAI exception hierarchy
│   └── logging.py        # Structlog structured logging setup
└── ingestion/            # (Future) Automotive knowledge ingestion subsystem
```

## Standards

All code in `src/` adheres strictly to:
- [Coding Standards](../docs/engineering/03-coding-standards.md)
- [Naming Conventions](../docs/engineering/02-naming-conventions.md)
- [Logging Philosophy](../docs/engineering/04-logging-philosophy.md)
- [Configuration Philosophy](../docs/engineering/06-configuration-philosophy.md)