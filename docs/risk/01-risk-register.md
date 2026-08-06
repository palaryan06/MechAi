# Risk Register

## Why This Document Exists

This is the **MechAI risk register**. It tracks the risks that could affect the project's success, their likelihood, their impact, and the mitigations we have planned. It exists so that risks are visible, tracked, and addressed — rather than ignored until they become problems.

## Risk Scoring

Each risk is scored on two dimensions:

- **Likelihood (L):** 1 (rare) to 5 (almost certain).
- **Impact (I):** 1 (minor) to 5 (catastrophic).

**Risk score = L × I.** Higher is more urgent.

| Score | Priority |
|-------|----------|
| 15-25 | Critical — active mitigation required |
| 8-14 | High — mitigation planned |
| 4-7 | Medium — monitor |
| 1-3 | Low — accept and watch |

## Risk Register

### R-001: Knowledge Graph Approach Is Not Viable

- **Category:** Technical
- **Likelihood:** 3
- **Impact:** 5
- **Score:** 15 (Critical)
- **Description:** The knowledge graph approach (ADR-0001) proves too hard to build or maintain — extraction is too error-prone, coverage too costly, or reasoning too weak.
- **Mitigation:** Validate through research and prototyping in Phase 1/2 before committing the architecture. Keep the vector store as a complement. Revisit the ADR if research shows a problem.
- **Status:** Monitoring (will be actively addressed in Phase 1)

### R-002: Data Access & Licensing

- **Category:** Business/Legal
- **Likelihood:** 3
- **Impact:** 4
- **Score:** 12 (High)
- **Description:** We cannot access sufficient workshop manuals, TSBs, or other automotive knowledge due to licensing, cost, or availability constraints.
- **Mitigation:** Research data sources early. Explore licensing agreements and synthetic data generation. The architecture should not depend on a single data source.
- **Status:** Monitoring

### R-003: Evaluation Is Too Hard / Benchmarks Unreliable

- **Category:** Technical
- **Likelihood:** 3
- **Impact:** 4
- **Score:** 12 (High)
- **Description:** We cannot build reliable benchmarks that measure whether the system actually reasons correctly. Without evaluation, we can't know if we're making progress.
- **Mitigation:** Invest early in the evaluation framework (see [Research: Evaluation](../research/04-evaluation-and-benchmarks.md)). Develop expert-curated cases. Start small and grow.
- **Status:** Monitoring (being researched)

### R-004: Model / LLM Hallucination Undermines Trust

- **Category:** Technical/Product
- **Likelihood:** 4
- **Impact:** 4
- **Score:** 16 (Critical)
- **Description:** The LLM components produce confidently wrong or ungrounded diagnoses, destroying user trust and potentially causing unsafe actions.
- **Mitigation:** Ground every claim in sources. Quantify uncertainty. Design the reasoning engine to prioritize evidence over raw model output. Conservative handling of safety-critical topics. Evaluation of hallucination rate.
- **Status:** Active design consideration

### R-005: On-Premises Deployment Diverges From SaaS

- **Category:** Technical
- **Likelihood:** 3
- **Impact:** 3
- **Score:** 9 (High)
- **Description:** The on-premises deployment becomes a separate fork, doubling maintenance and violating the deployment-agnostic principle.
- **Mitigation:** Keep the core deployment-agnostic (see [Future Scaling](../architecture/04-future-scaling.md)). Test both deployment modes in CI. Reject environment-specific code.
- **Status:** Monitoring

### R-006: Security / Privacy Incident

- **Category:** Security
- **Likelihood:** 3
- **Impact:** 5
- **Score:** 15 (Critical)
- **Description:** A security incident exposes vehicle data, customer PII, or proprietary knowledge, causing legal, financial, and reputational damage.
- **Mitigation:** Follow the [Security Policy](../../SECURITY.md) and [Security Philosophy](../engineering/08-security-philosophy.md). Least privilege, no secrets in repo, prompt injection mitigations, no PII in logs, on-prem data isolation.
- **Status:** Active (foundation in place)

### R-007: Team / Talent Constraints

- **Category:** Business
- **Likelihood:** 3
- **Impact:** 3
- **Score:** 9 (High)
- **Description:** We cannot attract or retain the right talent (AI engineers, automotive domain experts, data engineers).
- **Mitigation:** Clear mission, strong engineering culture, documented standards. Automotive domain expertise can be augmented through partnerships or consultants.
- **Status:** Monitoring

### R-008: Agent / Tooling Chaos

- **Category:** Engineering Process
- **Likelihood:** 3
- **Impact:** 3
- **Score:** 9 (High)
- **Description:** Multiple AI agents create conflicting changes, duplicate work, or break the repository.
- **Mitigation:** Clear [AI Agent Handbook](../agents/01-ai-agent-handbook.md), [Memory System](../agents/02-memory-system.md), task coordination, and mandatory review. Agents follow the same process as humans.
- **Status:** Active (system in place)

### R-009: Regulatory / Liability Risk

- **Category:** Business/Legal
- **Likelihood:** 2
- **Impact:** 5
- **Score:** 10 (High)
- **Description:** Regulatory or liability issues arise from providing diagnostic advice (especially safety-related).
- **Mitigation:** Conservative product philosophy (amplify, don't replace technicians). Warnings and disclaimers for safety-critical topics. Legal review before product launch. Recorded in the [Product Philosophy](../03-product-philosophy.md).
- **Status:** Monitoring (will address before MVP)

### R-010: Technology Churn

- **Category:** Technical
- **Likelihood:** 3
- **Impact:** 3
- **Score:** 9 (High)
- **Description:** The rapidly changing AI ecosystem (models, vector stores, graph DBs) makes our early technology choices obsolete.
- **Mitigation:** Prefer boring, well-understood technology. Record decisions as ADRs. Keep components modular and replaceable. Benchmark before committing.
- **Status:** Monitoring

## Risk Review

- The risk register is **reviewed at least monthly** (or at each sprint review).
- New risks are added as identified.
- Mitigations are tracked to completion.
- When a risk materializes, it becomes an incident (or problem) and is handled immediately.

## How to Use This Document

1. **Before a significant decision**, check if the decision increases or decreases any risk.
2. **When you identify a new risk**, add it to this register.
3. **When a risk changes**, update its likelihood, impact, or mitigations.

## Related Documents

- [Known Assumptions](02-known-assumptions.md) — what we assume.
- [Known Unknowns](03-known-unknowns.md) — what we don't know.
- [Security Policy](../../SECURITY.md) — security mitigations.
- [Roadmap](../roadmap/01-roadmap.md) — how risks affect priorities.