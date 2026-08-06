# ADR-0001: Knowledge Graph as Reasoning Core

- **Status:** Proposed
- **Date:** 2026-08-03
- **Author:** Founding Engineering Team

## Context

MechAI's mission is to build an AI mechanic that **reasons over automotive knowledge** rather than acting as a simple chatbot. The product philosophy requires that every answer be grounded in evidence, traceable to a source, and causally sound.

A naive retrieval-augmented generation (RAG) approach can retrieve relevant text passages, but it cannot *reason* about why a symptom implies a fault. It cannot model the physical relationships between components or explain a causal chain. Without a reasoning structure, MechAI would be a clever chatbot, not an intelligent mechanic.

The core question is: **how do we represent automotive knowledge so the system can reason causally over it?**

## Decision

We adopt a **knowledge graph as the primary reasoning substrate**, with a vector store as a complementary retrieval layer for grounding in source text.

- The **knowledge graph** models automotive entities (components, systems, symptoms, failure modes, procedures) and their relationships (PART_OF, CAUSES, SYMPTOM_OF, REQUIRES), enabling causal reasoning and explainable diagnostic paths.
- The **vector store** provides semantic retrieval of source documents for grounding and provenance. It complements, but does not replace, the graph.

## Consequences

### Positive Consequences

- Enables **causal reasoning**: the graph can traverse "fault → symptom" paths and explain *why*.
- Enables **explainable diagnoses**: the reasoning path is the evidence trail.
- Models the **physical structure** of vehicles and systems.
- Supports **structured queries** ("what can cause this symptom?") that retrieval cannot.
- Aligns with the product philosophy of evidence-based, reasoning-first answers.

### Negative Consequences

- **Extraction is hard and error-prone.** Building the graph from manuals and TSBs requires robust knowledge extraction.
- **Coverage is a risk.** An incomplete graph gives wrong answers. We must invest in coverage and validation.
- **Maintenance cost.** Vehicles change; the graph must stay current.
- **Higher complexity** than a naive RAG approach. Requires careful integration of graph and vector layers.

## Alternatives Considered

### Alternative 1: Vector Retrieval Only (RAG)

Embed documents and retrieve relevant chunks by similarity. **Rejected** because retrieval is not reasoning — it finds text but cannot explain *why* or model causal relationships. Violates the product philosophy.

### Alternative 2: Pure LLM Reasoning (No External Structure)

Rely on the model's parametric knowledge. **Rejected** because it is unreliable (hallucination), provides no provenance, and violates the evidence-is-everything requirement.

### Alternative 3: Hybrid (Graph + Vector)

Adopted. The graph provides reasoning; the vector store provides grounding.

## Rationale

The product philosophy (**reason, don't parrot; evidence is everything**) requires a system that can explain *why* a symptom implies a fault. Only a structured representation — a knowledge graph — enables causal, explainable reasoning. The vector store is retained for the essential grounding and provenance requirement.

This decision is **proposed** and will be validated through research and prototyping (see [Research: Knowledge Representation](../research/02-knowledge-representation.md)). If research shows the graph approach is not viable, this ADR will be updated or superseded.

## Implementation Notes

- The knowledge graph is a core component of the [Architecture Overview](../architecture/01-architecture-overview.md).
- The data model (graph schema, entity types, relationship types) is an open research question.
- The vector store is a complement for retrieval and grounding, not the reasoning core.

## References

- [Product Philosophy](../03-product-philosophy.md)
- [Research: Knowledge Representation](../research/02-knowledge-representation.md)
- [Architecture Overview](../architecture/01-architecture-overview.md)