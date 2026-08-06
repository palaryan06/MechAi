# Known Assumptions

## Why This Document Exists

This document records the **assumptions** we are making as we build MechAI. It exists so that assumptions are explicit, testable, and challengeable. An unexamined assumption is a hidden risk.

When an assumption is validated or invalidated, it should be updated here and, if significant, recorded in an ADR.

## How Assumptions Are Recorded

Each assumption has:

- **Statement:** What we assume.
- **Why we assume it:** The reasoning.
- **Status:** Active | Validated | Invalidated | Under Review
- **Risk if wrong:** What happens if the assumption is false.

## Current Assumptions

### A-001: Knowledge Graph Is the Right Reasoning Substrate

- **Statement:** A knowledge graph is the best way to enable causal, explainable reasoning over automotive knowledge.
- **Why:** The product philosophy requires reasoning, not just retrieval. A graph enables causal paths and explainable diagnoses.
- **Status:** Under Review (being validated in Phase 1 research)
- **Risk if wrong:** We invest in the wrong architecture. Mitigated by prototyping before committing.

### A-002: Python Is the Right Primary Language

- **Statement:** Python is the best primary language for MechAI.
- **Why:** Strong AI/ML ecosystem, readability, talent availability.
- **Status:** Active (proposed, ADR-0002)
- **Risk if wrong:** Performance or ecosystem gaps. Mitigated by strict typing and native extensions where needed.

### A-003: We Can Access Sufficient Automotive Knowledge

- **Statement:** We can obtain enough workshop manuals, TSBs, and other knowledge to build a useful system.
- **Why:** The product depends on automotive knowledge.
- **Status:** Under Review (data access is a known risk, R-002)
- **Risk if wrong:** We cannot build a useful product. Mitigated by researching data sources early.

### A-004: The Reasoning Approach Can Be Evaluated

- **Statement:** We can build reliable benchmarks that measure whether the system reasons correctly.
- **Why:** Without evaluation, we can't know if we're making progress.
- **Status:** Under Review (being researched)
- **Risk if wrong:** We can't measure progress. Mitigated by investing in evaluation early.

### A-005: The Product Serves Multiple Audiences

- **Statement:** The same reasoning engine can serve DIY users, professional technicians, and fleet operators.
- **Why:** The mission requires serving the full spectrum of users.
- **Status:** Active
- **Risk if wrong:** We build a product that doesn't fit any audience well. Mitigated by designing the core to be audience-agnostic.

### A-006: On-Premises and SaaS Can Share a Core

- **Statement:** The same core reasoning engine can run in SaaS and on-premises without forking.
- **Why:** The mission requires serving privacy-sensitive customers.
- **Status:** Active
- **Risk if wrong:** We build a SaaS-only architecture that can't be deployed on-premises. Mitigated by keeping the core deployment-agnostic.

### A-007: AI Agents Can Contribute Safely and Effectively

- **Statement:** With the right structure (handbook, memory, standards), AI agents can be productive, safe contributors.
- **Why:** The future team includes multiple AI agents.
- **Status:** Active (system in place)
- **Risk if wrong:** Agent chaos breaks the repository. Mitigated by the agent handbook, memory system, and mandatory review.

### A-008: The Team Can Build This

- **Statement:** We can attract and retain the talent needed to build MechAI.
- **Why:** The project is technically ambitious.
- **Status:** Active
- **Risk if wrong:** We can't execute. Mitigated by a clear mission and strong engineering culture.

## How to Use This Document

1. **Before making a decision**, check if it relies on an assumption.
2. **When you validate or invalidate an assumption**, update its status.
3. **When you identify a new assumption**, add it here.

## Related Documents

- [Risk Register](01-risk-register.md) — the risks.
- [Known Unknowns](03-known-unknowns.md) — what we don't know.
- [ADR System](../adr/README.md) — where validated assumptions become decisions.