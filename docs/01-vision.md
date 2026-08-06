# MechAI Vision

## Why This Document Exists

The vision is the **north star** of the company. It answers the question: *What are we trying to build, ultimately?* It is deliberately aspirational and long-term. It is not a roadmap (see [`roadmap/`](roadmap/)) and not a specification of features this quarter.

Every engineer, product manager, and AI agent should be able to read this document and understand what success looks like a decade from now. When a decision is hard, we return here: *does this move us toward the vision?*

## The Vision

### The World's Most Intelligent AI Mechanic

MechAI will become the world's most intelligent AI mechanic — a system that can **reason over automotive knowledge** the way a master technician reasons over decades of experience.

Today, most "AI mechanics" are chatbots: they pattern-match to text, quote generic troubleshooting lists, and often give confidently wrong answers. They do not *understand* a vehicle, its symptoms, its service history, or the physical relationships between its components.

The vision is different.

### From Chatbot to Reasoning System

| | Typical AI automotive chatbot | MechAI (the vision) |
|---|---|---|
| Knowledge | Generic text scraped from the web | Workshop manuals, wiring diagrams, fault trees, TSBs, service history |
| Reasoning | Pattern-matching on text | Multi-step causal reasoning over a knowledge graph of components and failure modes |
| Context | No memory of the vehicle | Persistent vehicle state: DTCs, sensor data, repair history, wear patterns |
| Evidence | Vague confidence | Traceable, sources cited, uncertainty quantified |
| Action | Suggests text | Guides a mechanic or DIYer through a verification procedure step by step |
| Modality | Text only | Voice, images (photos of parts, dashboards), OBD-II, telemetry |

### What We Will Achieve

1. **Reason over automotive knowledge, not just retrieve it.** The system will explain *why* a symptom implies a fault, using a structured understanding of how vehicle systems interact.

2. **Integrate the full diagnostic loop.** Ingest workshop manuals, read OBD-II codes, accept a photo of a worn component, listen to a described sound, cross-reference service bulletins, and synthesize a ranked, evidence-backed diagnosis.

3. **Serve every audience we can responsibly serve.** From a home mechanic with a phone photo of a brake rotor, to a fleet operator with millions of telemetry points, to a professional technician inside a shop — MechAI should meet people where they are.

4. **Run anywhere.** A SaaS product for consumers and shops today; a locally deployable system for privacy-sensitive fleets and dealers tomorrow. The architecture must permit both.

5. **Become the trust layer for automotive knowledge.** When someone says "MechAI told me it's the alternator," that statement should carry the same weight as a good technician's opinion — because it is grounded in the same kind of evidence and reasoning.

## The Principles That Guide Us Toward the Vision

- **Ground in evidence.** Every answer traces back to a source: a manual page, a spec, a known failure pattern, a live sensor reading. No hallucinated specs.
- **Quantify uncertainty.** A good mechanic says "I'm 70% sure it's the alternator; here's how to check." So must we.
- **Respect the physical world.** Vehicles obey physics. Our reasoning must respect component relationships, torque specs, wiring continuity, and failure propagation — not just text co-occurrence.
- **Make humans better, not replace them.** The system is an amplifier, not a substitute. It frees technicians from lookup drudgery so they can do the hands-on work that only people can do.
- **Earn trust through humility.** When we don't know, we say so, and we route the user to the right next check — just as a good mechanic would.

## What Is Out of Scope (For Now, and Why)

- **Full autonomy** to physically repair vehicles is out of scope. We guide, we recommend, we explain; we do not reach in with a wrench. (The physical safety and liability model is a later ADR.)
- **Consumer-facing mobile first:** Our first product surface may be a web/SaaS experience. Mobile and voice come as modalities, not as the starting point.
- **Regulatory and safety certification:** We take safety extremely seriously, but certification (e.g., for autonomous guidance) is a later-stage business decision, not a seed-stage engineering one.

## Measuring Progress Toward the Vision

We will know we are moving toward the vision when we can demonstrate:

1. A diagnostic conversation that correctly isolates a fault using evidence from a manual **and** an OBD-II signal **and** an image, with cited sources.
2. A reasoning trace that a human engineer can inspect, critique, and improve.
3. Measured accuracy on a held-out diagnostic benchmark that improves over time.
4. A deployment that runs on-premises for a privacy-sensitive customer, unchanged in behavior from the SaaS version.

## This Vision Is a Living Document

The vision will evolve as we learn. It is not frozen. Changes to the vision are significant decisions and should be recorded as ADRs and discussed with the whole team. But the core — *an AI mechanic that reasons over automotive knowledge rather than acting as a simple chatbot* — is the reason MechAI exists, and it will not change lightly.