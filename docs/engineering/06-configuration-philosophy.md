# Configuration Philosophy

## Why This Document Exists

This document defines **how we manage configuration** in MechAI. It exists because configuration is where secrets, environment differences, and operational complexity hide. A clear configuration philosophy prevents secrets from leaking, environments from diverging, and deployments from breaking.

## Core Principles

1. **Secrets never enter the repository.** Ever.
2. **Configuration is environment-specific.** Code is the same; configuration differs by environment.
3. **Fail fast on missing config.** A missing required variable is an error, not a silent default.
4. **Document every variable.** `.env.example` documents what exists and why.
5. **Prefer environment variables** for now; move to a secrets manager as we scale.

## Configuration Sources

| Source | Use For | Example |
|--------|---------|---------|
| **Environment variables** | All configuration, including secrets (for now) | `MECHAI_DB_HOST`, `MECHAI_API_KEY` |
| **Config files** | Non-secret, non-environment-specific defaults | `pyproject.toml`, `ruff.toml` |
| **Secrets manager (future)** | Secrets at scale | Cloud KMS, Vault |

## Environment Variables

### Naming

- `UPPER_SNAKE_CASE` with the `MECHAI_` prefix.
- Group by domain: `MECHAI_DB_*`, `MECHAI_LOG_*`, `MECHAI_MODEL_*`.

### Examples

```
# Database
MECHAI_DB_HOST=localhost
MECHAI_DB_PORT=5432
MECHAI_DB_NAME=mechai

# Logging
MECHAI_LOG_LEVEL=INFO

# Model (future)
MECHAI_MODEL_PROVIDER=openai
MECHAI_MODEL_NAME=gpt-4o

# Secrets (never committed)
MECHAI_DB_PASSWORD=...
MECHAI_API_KEY=...
```

### `.env.example`

- Committed to the repository.
- Documents every variable, its purpose, and whether it is required.
- **Never contains real values.** Use placeholders like `...` or `changeme`.

```bash
# .env.example
# Required: database connection
MECHAI_DB_HOST=localhost
MECHAI_DB_PORT=5432
MECHAI_DB_NAME=mechai
MECHAI_DB_USER=mechai
MECHAI_DB_PASSWORD=changeme   # REQUIRED - never commit real value

# Required: logging
MECHAI_LOG_LEVEL=INFO

# Optional: model configuration (defaults apply)
MECHAI_MODEL_PROVIDER=openai
```

## Configuration Loading

- **Load configuration at startup**, centrally, in one module.
- **Validate required variables** at startup. Fail fast with a clear error.
- **Provide typed accessors** (e.g., `config.db_host`, `config.log_level`).
- **Never read `os.environ` directly** in business logic. Go through the config module.

```python
# src/mechai/common/config.py
import os

class Config:
    def __init__(self) -> None:
        self.db_host = self._require("MECHAI_DB_HOST")
        self.db_port = int(self._require("MECHAI_DB_PORT"))
        self.log_level = os.getenv("MECHAI_LOG_LEVEL", "INFO")

    def _require(self, name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value
```

## Environment-Specific Configuration

| Environment | Purpose | Config Source |
|-------------|---------|---------------|
| **Local dev** | Developer machine | `.env` (local, gitignored) |
| **CI** | Test runs | CI secrets + env vars |
| **Staging** | Pre-production | Env vars / secrets manager |
| **Production** | Live service | Env vars / secrets manager |

- **Code is identical across environments.** Only configuration differs.
- **No environment-specific branches or forks.** Ever.

## Secrets Management: Now and Future

| Stage | Approach |
|-------|----------|
| **Now (seed)** | Environment variables. `.env` is gitignored. `.env.example` documents variables. |
| **Post-MVP** | Move to a secrets manager (cloud KMS / Vault). Secrets injected at runtime, never in env files. |

## What to Avoid

- **Hardcoded values** in code (URLs, ports, keys).
- **Config in the repository** that contains real secrets.
- **Silent defaults** for required values.
- **Reading `os.environ` scattered** throughout the codebase.
- **Environment-specific code** (`if env == "production":`).

## How to Use This Document

1. **When adding a new config value**, add it to the config module and `.env.example`.
2. **When adding a secret**, never commit it. Document it in `.env.example` with a placeholder.
3. **When reviewing code**, check that config is centralized and secrets are not hardcoded.

## Related Documents

- [Security Philosophy](08-security-philosophy.md) — secrets and security.
- [Security Policy](../../SECURITY.md) — the security policy.
- [Coding Standards](03-coding-standards.md) — how config code is written.
- [Naming Conventions](02-naming-conventions.md) — env var naming.