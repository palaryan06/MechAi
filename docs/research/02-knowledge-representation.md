# Research: Knowledge Representation

## Why This Document Exists

This is the **core research document** for MechAI. It addresses the fundamental question: **How do we represent automotive knowledge so that a system can reason over it — not just retrieve it?**

This is the heart of the "reason, don't parrot" philosophy. If we get knowledge representation right, the rest of the system can be built on a solid foundation. If we get it wrong, we'll have a clever chatbot, not an intelligent mechanic.

## The Research Question

> How do we represent automotive knowledge — components, systems, symptoms, failure modes, procedures — so that a system can:
> 1. Explain *why* a symptom implies a fault.
> 2. Reason over the physical relationships between components.
> 3. Ground every claim in a source.
> 4. Quantify uncertainty.

## Why This Is Hard

Automotive knowledge is:

- **Deeply physical.** Components interact through physics: electricity, fluid, heat, mechanics. A bad ground causes voltage drops that mimic sensor faults.
- **Semi-structured.** Workshop manuals mix text, diagrams, tables, and procedures.
- **Hierarchical.** Systems contain subsystems contain components.
- **Causal.** A failing part causes symptoms; symptoms can indicate multiple causes.
- **Context-dependent.** Behavior differs by make, model, year, and configuration.

A naive text retrieval system cannot capture this. It can find related passages, but it cannot *reason* about why a symptom occurs.

## Candidate Approaches

### 1. Knowledge Graph (Graph-Based)

**What it is:** A graph of entities (components, systems, symptoms, failure modes) connected by typed relationships (PART_OF, CAUSES, PRECEDES, REQUIRES).

**Strengths:**
- Enables causal reasoning: traverse "fault → symptom" paths.
- Captures physical structure: component hierarchies.
- Explainable: the reasoning path is the evidence trail.
- Queryable: structured queries for "what can cause this symptom?"

**Weaknesses:**
- Building the graph (extraction) is hard and error-prone.
- Coverage: an incomplete graph gives wrong answers.
- Maintenance: vehicles change; graphs must stay current.

### 2. Vector / Embedding Retrieval (Retrieval-Augmented Generation)

**What it is:** Embed documents, retrieve relevant chunks by similarity, and feed them to an LLM.

**Strengths:**
- Fast to build, no manual curation.
- Good for "find the relevant passage" tasks.
- Handles unstructured text well.

**Weaknesses:**
- Retrieval is not reasoning. It finds text, it doesn't explain *why*.
- Can retrieve irrelevant or conflicting content.
- Hard to enforce causal understanding.

### 3. Hybrid: Graph + Vector

**What it is:** Use the knowledge graph for structured reasoning and the vector store for grounding in source text.

**Strengths:**
- Graph provides the reasoning structure.
- Vector store provides the source text (provenance).
- Best of both worlds.

**Weaknesses:**
- Most complex to build.
- Requires careful integration of the two systems.

### 4. Pure LLM Reasoning (No External Structure)

**What it is:** Rely on the model's parametric knowledge.

**Strengths:**
- Simplest.
- Flexible.

**Weaknesses:**
- Unreliable (hallucination).
- No provenance or grounding.
- Violates the product philosophy (evidence is everything).

## Current Stance (Pre-Research)

**Our provisional stance is a hybrid approach: knowledge graph as the reasoning substrate, vector store for grounding.** This is captured in the [Architecture Overview](../architecture/01-architecture-overview.md) and will be validated (or revised) through research and prototyping. It is *not* yet a decided ADR.

## Open Questions

### 1. Schema Design

- What are the core entity types? `Component`, `System`, `Symptom`, `FailureMode`, `Procedure`, `Specification`, `VehicleModel`?
- What are the core relationship types? `PART_OF`, `CAUSES`, `SYMPTOM_OF`, `REQUIRES`, `PRECEDES`?
- How do we represent uncertainty and confidence in edges?

### 2. Extraction

- How do we extract a knowledge graph from workshop manuals, TSBs, and diagrams?
- What is the role of LLM-based extraction vs deterministic parsing?
- How do we handle errors in extraction (wrong relationships, missed entities)?

### 3. Reasoning

- How do we traverse the graph to explain symptoms causally?
- How do we rank hypotheses (which fault is most likely given the evidence)?
- How do we handle concurrent faults and conflicting evidence?

### 4. Provenance

- How do we link every fact in the graph to its source (page, section, diagram)?
- How do we track the confidence of each edge?

### 5. Scalability

- How do we partition the graph by vehicle model / system without losing cross-model knowledge?
- How do we keep the graph current as vehicles change?

## What We Know (Working Assumptions)

- **Naive RAG is insufficient** for the product vision. It can retrieve, but not reason.
- **A pure LLM is unacceptable.** It violates the evidence and provenance requirements.
- **The physical/causal model is essential.** Understanding *why* is the product.
- **The graph must be domain-specific.** Generic ontologies won't capture automotive physics.

## Next Steps

1. Prototype a small knowledge graph (e.g., 3-5 systems: charging, braking, cooling) from synthetic or sample data.
2. Test extraction approaches in an experiment (see [Experiments](../../experiments/README.md)).
3. Evaluate reasoning: can the graph explain a known fault-symptom relationship?
4. Record findings and a decision (ADR).

## Related Documents

- [Research Overview](01-research-overview.md) — how we research.
- [Evaluation & Benchmarks](04-evaluation-and-benchmarks.md) — how we measure success.
- [Architecture Overview](../architecture/01-architecture-overview.md) — the target architecture.
- [Open Questions](../reference/03-open-questions.md) — tracked open questions.