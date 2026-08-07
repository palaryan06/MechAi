# Logging Philosophy

## Why This Document Exists

This document defines **how we log** in MechAI. It exists because good logging is essential for debugging, monitoring, and operating an AI system that will eventually process vehicle data and provide diagnoses. Logging decisions made today shape our ability to debug tomorrow's production issues.

## Core Principles

1. **Structured logs, not text soup.** Every log entry is structured data (JSON), not a human-readable string with interpolated values.
2. **Context is king.** A log entry is useless without context: which vehicle, which document, which request, which model version.
3. **No secrets, no PII, no sensitive data.** Vehicle data (VINs, plates, customer info) never appears in logs.
4. **Log at the right level.** Use the level that matches the significance.
5. **Fail loudly.** Errors are visible, not swallowed.

## Structured Logging

We use **structured logging**: every log entry is a JSON object with a defined schema.

### Minimal Schema

```json
{
  "timestamp": "2026-08-03T15:00:00Z",
  "level": "INFO",
  "logger": "mechai.ingestion.obd_parser",
  "message": "decoded obd frame",
  "event": "obd.frame_decoded",
  "context": {
    "vehicle_id": "veh_1234",
    "pid": "0x0C",
    "value": "820"
  },
  "trace_id": "abc123",
  "service": "ingestion"
}
```

### Key Fields

| Field | Purpose |
|-------|---------|
| `timestamp` | ISO 8601 UTC |
| `level` | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `logger` | The module that emitted the log |
| `message` | Short, human-readable summary |
| `event` | Machine-readable event name (e.g., `obd.frame_decoded`) |
| `context` | Key-value structured context |
| `trace_id` | Correlation ID for the request/operation |
| `service` | The service that emitted the log |

## Log Levels

| Level | When to Use |
|-------|-------------|
| **DEBUG** | Detailed troubleshooting. Not enabled in production by default. |
| **INFO** | Normal operational events: request completed, document parsed, diagnosis generated. |
| **WARNING** | Something unexpected but non-fatal: retry needed, low-confidence source, degradation. |
| **ERROR** | A failure that prevented an operation from completing: parse failed, query failed, dependency down. |
| **CRITICAL** | A failure that threatens the system: data corruption, security incident, outage. |

## What to Log (and What Not to)

### Log

- Request/operation start and completion (with duration).
- Document/message/query processing lifecycle.
- Retrieval and reasoning steps (for traceability).
- External API calls (provider, model, latency, error).
- Failures, retries, and timeouts.
- Data validation failures (without the sensitive data itself).

### Never Log

- **Secrets:** API keys, tokens, passwords, credentials.
- **PII:** names, emails, phone numbers, addresses.
- **Vehicle identifiers:** VINs, license plates.
- **Full diagnostic data:** raw OBD-II payloads, full images, full sensor dumps.
- **Customer content:** full user prompts, full diagnosis output (unless sanitized and necessary).

## Logging in Code

```python
import structlog

logger = structlog.get_logger("mechai.ingestion.obd_parser")


def decode_frame(frame: bytes, vehicle_id: str) -> int:
    logger.info("decoding obd frame", vehicle_id=vehicle_id, frame_length=len(frame))
    value = _raw_decode(frame)
    logger.debug("decoded value", value=value)
    return value
```

- Use the logger module-level.
- Pass context as keyword arguments.
- Keep messages short and constant — the flavor belongs in context, not the message.

## Error Handling + Logging

- **Log the error where it occurs**, with context.
- **Re-raise or handle** appropriately. Don't both log and swallow.
- **Include the exception** in the log entry (`exc_info=True`).

```python
try:
    parse_document(path)
except DocumentParseError as exc:
    logger.error("document parse failed", path=path, exc_info=exc)
    raise
```

## Traceability

- Every request/operation has a `trace_id`.
- All logs within an operation share the `trace_id`.
- This enables full-stack tracing: user question → retrieval → reasoning → output.

## Logging in Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Level | DEBUG | INFO (ERROR/CRITICAL always) |
| Format | Pretty, colored | Structured JSON |
| Transport | stdout | Structured log sink (future: central log store) |
| PII rules | Same as production | Same |

## Future Considerations

- **Metrics:** We will add metrics (counters, histograms) alongside logs for operations like query latency and retrieval success.
- **Tracing:** We will adopt distributed tracing (e.g., OpenTelemetry) as the system grows.
- **Alerting:** We will build alerts on CRITICAL and ERROR patterns.

## How to Use This Document

1. **When adding logging**, follow the structured format and schema above.
2. **When reviewing code**, check for PII/secret leaks and contextual completeness.
3. **When debugging**, look for the `trace_id` to trace the full operation.

## Related Documents

- [Coding Standards](03-coding-standards.md) — logging in code.
- [Security Philosophy](08-security-philosophy.md) — what not to log.
- [Security Policy](../../SECURITY.md) — data handling requirements.
- [Architecture Overview](../architecture/01-architecture-overview.md) — the system components that will log.