# ADR-0002: Python as Primary Language

- **Status:** Proposed
- **Date:** 2026-08-03
- **Author:** Founding Engineering Team

## Context

MechAI is building an AI system that reasons over automotive knowledge. The system will involve machine learning, knowledge graphs, retrieval, and multi-modal inputs (text, OBD-II, images, voice).

The repository is being established as the engineering foundation. A primary implementation language needs to be chosen early so the foundation (coding standards, tooling, project structure) is consistent.

The selection criteria are:
- Strength of the AI/ML ecosystem.
- Ability to build a maintainable, production-grade codebase.
- Team familiarity and talent availability.
- Long-term viability and community support.

## Decision

We adopt **Python** as the primary implementation language for MechAI.

Python is chosen for:
- Its **dominant AI/ML ecosystem** (PyTorch, scikit-learn, LangChain, graph libraries, etc.).
- Its **strong data tooling** (pandas, numpy, structured data handling).
- Its **readability** and alignment with our documentation-is-code, clarity-first philosophy.
- **Team familiarity** and the availability of Python engineers.

## Consequences

### Positive Consequences

- Access to the strongest **AI/ML and data ecosystem**.
- **Fast iteration** on research and prototypes.
- **Readable code** that aligns with our clarity-first standards.
- **Large talent pool** for hiring.

### Negative Consequences

- **Performance** is not Python's strength for hot paths; compute-intensive work may need native extensions or external services.
- **Runtime typing** is not enforced; we require strict static typing (mypy) to compensate.
- **Dependency management** requires discipline; we will pin dependencies and use a lockfile.

## Alternatives Considered

### Alternative 1: TypeScript / Node.js

Strong for web services, but the AI/ML ecosystem is weaker. Would require significant bridge work for ML dependencies. **Rejected** for the core system.

### Alternative 2: Go

Excellent performance and tooling, but the AI/ML ecosystem is immature. Would require heavy custom implementation of ML/data components. **Rejected** for the core system. (Go or Rust may be considered for performance-critical subcomponents later.)

### Alternative 3: Rust

Bleeding-edge performance and safety, but slower development velocity and a less mature AI/data ecosystem. **Rejected** for the primary language, though noted as a possible future choice for high-performance components.

## Rationale

Python's unmatched AI/ML and data ecosystem directly serves MechAI's technical needs (knowledge graphs, retrieval, multi-modal AI). Its readability and clarity align with our engineering philosophy. While performance and typing require discipline, those costs are manageable with strict tooling (mypy, Ruff) and opportunistic use of native extensions where needed.

This decision is **proposed**. It is the working assumption for the foundation. It will be revisited if later research or prototyping reveals fundamental blockers.

## Implementation Notes

- Coding standards are defined in [Coding Standards](../engineering/03-coding-standards.md).
- Tooling (Ruff, mypy, pytest) is specified in the standards, to be installed when the Python project is scaffolded.
- The `src/` structure follows the conventions in the [Repository Guide](../architecture/02-repository-guide.md).

## References

- [Coding Standards](../engineering/03-coding-standards.md)
- [Repository Guide](../architecture/02-repository-guide.md)
- [Future Scaling Philosophy](../engineering/09-future-scaling-philosophy.md)
