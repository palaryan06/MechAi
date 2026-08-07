# ADR-0008: 2D Spatial Reading-Order Graph (DAG)

- **Status:** Accepted
- **Date:** 2026-08-07
- **Author:** Chief Document Intelligence Architect

## Context

Standard PDF text extraction linearizes pages using top-to-bottom $y$-coordinate sorting. In multi-column technical documents (such as automotive workshop manuals with two-column procedures and full-width diagram spans), naive $y$-sorting produces severe text interleaving where line 1 of column A is immediately followed by line 1 of column B.

## Decision

We model document reading order as a **Directed Acyclic Graph (DAG)** (`ReadingOrderDAG`) resolved via recursive XY-cut whitespace projection and column gutter analysis:
1. Horizontal and vertical projection profiles ($H(y)$, $V(x)$) partition pages into homogeneous column blocks.
2. Intra-column regions are ordered top-to-bottom.
3. Column transitions flow strictly from the bottom of column $k$ to the top of column $k+1$.
4. Full-width spanning entities (tables, diagrams, warning banners) act as topological synchronization barriers, halting column flows, visiting the spanning entity, and resuming below its baseline.

## Consequences

### Positive Consequences
- **Elimination of Text Interleaving**: Resolves RFC-005 Gap G-02 completely.
- **Support for Complex Layouts**: Handles mixed 1-column, 2-column, and floating sidebar pages deterministically.
- **Topological Integrity**: Enables downstream chunkers and extractors to walk a coherent linear reading stream.

### Negative Consequences
- Slightly higher computational cost per page compared to raw unsorted token dumping ($O(N \log N)$ vs $O(N)$).

## References

- [RFC-006: Document Intelligence Layer](file:///c:/Users/palar/PycharmProjects/MechAi/docs/architecture/rfc/RFC-006-document-intelligence-layer.md)
