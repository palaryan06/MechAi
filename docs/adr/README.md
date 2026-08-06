# Architectural Decision Records (ADRs)

## Why This Folder Exists

This folder contains the **Architectural Decision Records (ADRs)** for MechAI. An ADR is a short document that records a significant technical decision, the context that led to it, and the rationale. ADRs preserve the *why* behind the codebase.

ADRs exist because "future engineers" — including AI agents — need to understand why the system is shaped the way it is, without having to reverse-engineer it from the code. When a future contributor wonders *why did they choose this?*, the answer is in this folder.

## When to Write an ADR

Write an ADR when a decision is **significant** — when a future engineer would want to know why we chose this. Examples:

- Choosing a technology (vector store, graph database, language).
- Changing the architecture (adding a component, changing data flows).
- Defining a data model (schema of the knowledge graph).
- Adopting a process that significantly changes how we work.

**General rule:** If a future engineer would ask "why did we do this?", write an ADR.

## When NOT to Write an ADR

- Small, obvious decisions (naming a variable, formatting).
- Reversible decisions with low cost to change.
- Decisions that are purely about implementation details.

For small decisions, document in the PR. For significant decisions, write an ADR.

## ADR Lifecycle

```
Proposed → Accepted → Replaced → Superseded
```

| Status | Description |
|--------|-------------|
| **Proposed** | The decision is under review, not yet adopted. |
| **Accepted** | The decision is adopted and implemented. |
| **Replaced** | The decision was replaced by a newer ADR. |
| **Superseded** | The decision is no longer current; a newer ADR or decision has moved on. |

An ADR starts as **Proposed**, moves to **Accepted** when adopted, and is marked **Replaced** or **Superseded** when a newer ADR changes course.

## How to Write an ADR

### 1. Create the File

Use the naming convention: `NNNN-short-description.md` (e.g., `0001-knowledge-graph-core.md`).

### 2. Use the Template

Copy the [ADR Template](template.md) and fill in the sections.

### 3. Number It

ADRs are numbered sequentially: `0001`, `0002`, `0003`, ...

The [ADR Index](index.md) tracks all ADRs and their status.

### 4. Review It

Significant decisions are reviewed by the team. For the highest-confidence decisions, a review session (or PR review) serves as the approval.

### 5. Link It

- Link the ADR from the code/docs it affects.
- Add the ADR to the [Index](index.md).

## ADR Template

See [template.md](template.md). The template includes:

- **Status:** Proposed/Accepted/Replaced/Superseded.
- **Date:** When the decision was made.
- **Context:** The problem and constraints.
- **Decision:** The choice we made.
- **Consequences:** What it costs us, what it gains us.
- **Alternatives considered:** What we could have done instead.
- **References:** Related docs, research, or links.

## The ADR Index

The [Index](index.md) is the table of contents for all ADRs. It tracks:
- ADR number.
- Title.
- Status.
- Date.
- Brief summary.

## How to Use This Folder

1. **Search here first** before making a significant decision — the answer may already be recorded.
2. **Write an ADR** when you make a significant decision.
3. **Update the index** when you add, accept, or supersede an ADR.
4. **For agents:** Read relevant ADRs before touching affected code.

## Related Documents

- [Development Philosophy](../04-development-philosophy.md) — why we record decisions.
- [Repository Guide](../architecture/02-repository-guide.md) — where things live.
- [Documentation Standards](../engineering/07-documentation-standards.md) — how to write docs.
- [Research](../research/README.md) — where decisions are explored before being recorded.