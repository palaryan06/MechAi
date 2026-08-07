# Testing Philosophy

## Why This Document Exists

This document defines **how we test** in MechAI. It exists because testing is how we ensure the system is correct, safe, and maintainable. For an AI product that will eventually provide vehicle diagnoses, testing is not optional — it is a safety requirement.

## Core Principles

1. **Test behavior, not implementation.** Tests verify what the system does, not how it does it.
2. **Tests are code.** They are reviewed, maintained, and held to the same standard as production code.
3. **Test the important things.** Prioritize tests that protect correctness, safety, and the product philosophy (evidence, grounding, uncertainty).
4. **Fast feedback.** Tests run quickly and are part of CI.
5. **No real data in tests.** Use synthetic data. Never use real VINs, PII, or customer data.

## The Testing Pyramid

```
        ┌─────────┐
        │  E2E    │   Few — full system flows
        ├─────────┤
        │Integr.  │   Some — component interactions
        ├─────────┤
        │  Unit   │   Many — individual functions/classes
        └─────────┘
```

| Layer | What | How Many | Speed |
|-------|------|----------|-------|
| **Unit** | Individual functions/classes in isolation | Many | Fast |
| **Integration** | Component interactions (e.g., ingestion → storage) | Some | Medium |
| **E2E** | Full user flows (e.g., question → diagnosis) | Few | Slow |

## What to Test

### Always Test

- **Core logic:** parsers, extractors, reasoning steps, confidence calculations.
- **Error handling:** failures, retries, timeouts, malformed input.
- **Edge cases:** empty input, boundary values, conflicting evidence.
- **Data validation:** invalid DTCs, malformed documents, bad sensor values.
- **Provenance:** every output claim has a source.

### Test With Care (AI-Specific)

- **Prompt behavior:** Test that prompts produce the expected structure and respect constraints.
- **Retrieval quality:** Test that retrieval returns relevant, grounded results.
- **Uncertainty:** Test that the system expresses appropriate confidence and says "I don't know" when appropriate.
- **Safety:** Test that safety-critical topics (brakes, airbags, fuel) trigger conservative behavior.

### Don't Test

- **Implementation details** that can change without changing behavior.
- **Third-party libraries** (test our usage, not the library).
- **Trivial getters/setters** unless they have logic.

## Test Structure

- Tests live in `tests/`, mirroring `src/`.
- Test files: `test_<module>.py`.
- Test functions: `test_<behavior>`.

```python
# tests/mechai/ingestion/test_obd_parser.py


def test_decode_valid_frame_returns_value():
    result = decode_frame(b"\x41\x0c\x33\x34")
    assert result == 820


def test_decode_malformed_frame_raises():
    with pytest.raises(DocumentParseError):
        decode_frame(b"\x00")
```

## Test Data

- **Use synthetic data.** Never use real VINs, license plates, customer names, or real vehicle data.
- **Fixtures** are shared, documented, and versioned.
- **Synthetic data must be realistic** enough to exercise the logic (e.g., valid DTC formats, realistic sensor ranges).

## Mocking & Fakes

- **Mock external dependencies** (LLM APIs, databases, network calls) at the unit level.
- **Use fakes** (in-memory implementations) for integration tests where possible.
- **Never mock what you don't own** (e.g., don't mock the standard library).
- **Keep mocks minimal** — a test with too many mocks tests the mocks, not the code.

## AI-Specific Testing Challenges

| Challenge | Approach |
|-----------|----------|
| **Non-determinism** | Use seeded models where possible; assert on structure, not exact text |
| **Hallucination** | Test that claims are grounded in provided sources |
| **Prompt drift** | Version prompts; test prompt outputs against expected structure |
| **Model changes** | Pin model versions; re-run evaluation suites on upgrade |
| **Evaluation** | Build a held-out diagnostic benchmark (see [Research](../research/README.md)) |

## Test-Driven Development

We prefer **TDD** for core logic: write the test first, watch it fail, then implement. This ensures:

- Tests are written for the right reasons.
- Code is designed to be testable.
- Behavior is specified before implementation.

TDD is a default, not a dogma. For exploratory research code, tests may come after the prototype stabilizes.

## Coverage

- **Aim for high coverage on core logic** (parsers, reasoning, confidence).
- **Coverage is a signal, not a goal.** 100% coverage of trivial code is worse than 80% coverage of critical code.
- **CI enforces a minimum coverage threshold** (to be defined when CI is established).

## CI Integration

When CI is established:

- Tests run on every PR.
- Linting and type checking run alongside tests.
- Coverage is reported.
- A failing test blocks the merge.

## How to Use This Document

1. **Before writing code**, think about what tests are needed.
2. **When writing tests**, follow the structure and principles above.
3. **When reviewing code**, check that tests are meaningful and cover the important cases.

## Related Documents

- [Coding Standards](03-coding-standards.md) — how code is structured.
- [Engineering Handbook](01-engineering-handbook.md) — the core rules.
- [Research](../research/README.md) — evaluation and benchmarks.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — the contribution process.