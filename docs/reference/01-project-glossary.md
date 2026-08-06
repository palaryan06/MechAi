# Project Glossary

## Why This Document Exists

This is the **shared vocabulary** of the MechAI project. It exists so that everyone — humans and AI agents — uses the same terms with the same meanings. Consistent vocabulary prevents confusion and miscommunication.

## How to Use This Glossary

- **Look up a term** you're unsure about.
- **When writing docs or code**, use the canonical terms defined here.
- **When you introduce a new term**, add it to this glossary.

## Glossary

### A

**ADR (Architectural Decision Record)**
A document that records a significant technical decision, its context, and its rationale. See [ADR System](../adr/README.md).

**Agent (AI Coding Agent)**
An AI system that writes code, edits files, and contributes to the repository. Agents are first-class contributors. See [AI Agent Handbook](../agents/01-ai-agent-handbook.md).

**Agentic RAG**
A retrieval-augmented generation approach where an agent reasons over retrieved knowledge, rather than just retrieving and regurgitating. MechAI's goal is to go beyond naive RAG toward agentic reasoning.

### C

**Causal Reasoning**
Reasoning over cause-and-effect relationships. In MechAI, this means explaining *why* a symptom implies a fault by traversing the knowledge graph.

**Confidence**
The system's quantified certainty in a diagnosis or claim. The product philosophy requires honest, calibrated confidence.

### D

**DTC (Diagnostic Trouble Code)**
A standardized code (e.g., P0301) that indicates a detected fault in a vehicle. A key OBD-II evidence source.

**Diagnosis**
The system's ranked, evidence-backed identification of the likely fault(s) given the evidence.

### E

**Evidence**
Any piece of data that supports a claim: a manual page, a DTC, a sensor value, an image. The product philosophy requires every claim to be grounded in evidence.

**Evaluation**
The process of measuring whether the system reasons correctly. See [Research: Evaluation](../research/04-evaluation-and-benchmarks.md).

### F

**Failure Mode**
A way in which a component or system can fail (e.g., "alternator fails to charge").

**Freeze-Frame Data**
A snapshot of sensor values at the moment a fault was detected. OBD-II evidence.

### G

**Grounding**
The property of an answer being traceable to a source. A grounded answer cites its evidence.

### K

**Knowledge Graph**
A structured representation of automotive knowledge: entities (components, systems, symptoms, failure modes) connected by relationships (PART_OF, CAUSES). The core reasoning substrate. See [ADR-0001](../adr/0001-knowledge-graph-core.md).

### L

**LLM (Large Language Model)**
A large neural network trained on text. Used in MechAI for understanding and generation, but grounded in evidence.

### M

**Memory System**
The committed, shared knowledge store for AI agents. See [Memory System](../agents/02-memory-system.md).

**Mission**
The near-term, actionable translation of the vision. See [Mission](../02-mission.md).

### O

**OBD-II (On-Board Diagnostics, second generation)**
The standardized diagnostic system in vehicles. Provides DTCs, live sensor data, and freeze-frame data. See [Research: OBD-II](../research/03-obd-ii-and-telemetry.md).

**Open Question**
A question we know we need to answer. Tracked in [Open Questions](03-open-questions.md) and [Known Unknowns](../risk/03-known-unknowns.md).

### P

**PID (Parameter ID)**
An identifier for a specific sensor value in OBD-II (e.g., engine RPM, coolant temperature).

**Provenance**
The record of where a piece of data came from. Every claim must have provenance.

**Prompt**
A set of instructions given to an LLM. Prompts are versioned and curated in the [`prompts/`](../../prompts/) folder.

### R

**RAG (Retrieval-Augmented Generation)**
An approach that retrieves relevant documents and feeds them to an LLM to generate an answer. MechAI goes beyond naive RAG toward reasoning.

**Reasoning Trace**
The inspectable chain of reasoning from evidence to conclusion. A key output for explainability.

**Roadmap**
The plan of phases and milestones. See [Roadmap](../roadmap/01-roadmap.md).

### S

**Symptom**
A user-observable sign of a fault (e.g., "engine misfires", "brake light on").

### T

**TSB (Technical Service Bulletin)**
A manufacturer-issued notice about a known issue and its fix. A knowledge source.

### U

**Uncertainty**
The system's expression of how sure it is. The product philosophy requires honest uncertainty.

### V

**Vector Store**
A database for semantic search over embeddings. A complement to the knowledge graph for grounding. See [ADR-0001](../adr/0001-knowledge-graph-core.md).

**Vision**
The long-term aspirational goal: the world's most intelligent AI mechanic. See [Vision](../01-vision.md).

## How to Add a Term

When adding a term:

1. Add it alphabetically.
2. Define it clearly and concisely.
3. Link to the relevant doc if one exists.

## Related Documents

- [Useful Links](02-useful-links.md) — external resources.
- [Open Questions](03-open-questions.md) — the open questions tracker.
- [Vision](../01-vision.md) — the long-term goal.