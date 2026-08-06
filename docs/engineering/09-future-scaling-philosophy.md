# Future Scaling Philosophy (Engineering)

## Why This Document Exists

This document describes **how our engineering practices will scale** as the MechAI team grows from a few engineers to 20+ engineers and multiple AI agents. It complements the architectural [Future Scaling](../architecture/04-future-scaling.md) document, but focuses on the *engineering practices*, not the system design.

It answers: *What will we need to change about how we work as we grow?*

## Current State (Seed)

- 1-3 engineers
- No CI/CD yet
- No deployment infrastructure
- Simple task tracking
- Documentation-first repository

## Scaling Dimensions

| Dimension | Now | Growth (20+ engineers + agents) |
|-----------|-----|---------------------------------|
| Team size | 1-3 | 20+ humans + multiple agents |
| Codebase | No product code | Multi-module Python service(s) |
| CI/CD | None | Full pipeline: lint, type, test, build, deploy |
| Environments | Local dev | dev, staging, production |
| Observability | None | Logs, metrics, traces, alerts |
| Reviews | Ad hoc | Formal PR review with automation |
| Onboarding | One-on-one | Structured docs + agent handbook |

## Principles That Stay the Same

These principles do **not** change as we scale:

1. **Documentation is code.** More engineers means more need for clear docs.
2. **Evidence over opinion.** More decisions means more need for ADRs.
3. **Agents are first-class contributors.** More agents means more need for structure.
4. **Quality is non-negotiable.** Tests and reviews protect the codebase as velocity increases.
5. **Simplicity scales better than cleverness.** Operational complexity is the enemy.

## What Will Change

### 1. CI/CD

- Introduce CI as soon as there is product code.
- CI runs: lint (Ruff), type check (mypy), tests (pytest), coverage.
- CD (deployment) follows once there is something to deploy.
- Every PR must pass CI before merge.

### 2. Environments

- Establish dev, staging, and production environments.
- Configuration differences are handled through [Configuration Philosophy](06-configuration-philosophy.md).
- No environment-specific code forks.

### 3. Observability

- Structured logging (see [Logging Philosophy](04-logging-philosophy.md)).
- Metrics for operations: query latency, retrieval success, model cost.
- Distributed tracing as the system grows.
- Alerting on critical patterns.

### 4. Review Process

- Formal PR review: at least one approval, CI green, docs updated.
- Automated checks (lint, type, tests) before human review.
- Security checklist in review (see [Security Philosophy](08-security-philosophy.md)).

### 5. Onboarding

- Onboarding is documentation-first.
- New engineers read the [Engineering Handbook](01-engineering-handbook.md) and the [Repository Guide](../architecture/02-repository-guide.md).
- New agents read the [AI Agent Handbook](../agents/01-ai-agent-handbook.md).
- The [Memory System](../agents/02-memory-system.md) persists agent context across sessions.

### 6. Decision Making

- More people means more decisions.
- The [ADR System](../adr/README.md) becomes critical.
- Significant decisions are discussed in the team and recorded.

### 7. Code Ownership

- As the codebase grows, consider code ownership:
  - Each module has a designated owner.
  - Owners review changes in their module.
  - Ownership is documented in the module's README.

## Scaling Risks

| Risk | Mitigation |
|------|------------|
| Review bottleneck | Automation (lint/type/tests), small PRs, code ownership |
| Doc drift | Documentation is code; agents help maintain it |
| Onboarding debt | Doc-first onboarding; handbook is always current |
| Decision fog | ADRs are mandatory for significant decisions |
| Agent chaos | Clear agent handbook; memory system; review process applies to agents |

## How to Use This Document

1. **Planning engineering process changes?** This document is the north star.
2. **Worried about a scaling risk?** Add it to the [Risk Register](../risk/01-risk-register.md).
3. **Making a significant process change?** Write an ADR.

## Related Documents

- [Future Scaling (Architecture)](../architecture/04-future-scaling.md) — the system scaling plan.
- [Engineering Handbook](01-engineering-handbook.md) — the core rules.
- [ADR System](../adr/README.md) — how decisions are recorded.
- [Risk Register](../risk/01-risk-register.md) — known risks.