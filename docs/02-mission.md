# MechAI Mission

## Why This Document Exists

The vision describes the long-term goal: *the world's most intelligent AI mechanic that reasons over automotive knowledge*. The mission is the **near-term, actionable translation** of that vision. It answers: *What are we doing right now, and why does our daily work matter?*

Where the vision is aspirational, the mission is concrete. It is the document a contributor reads to understand the current focus of the company and to align their day-to-day work.

## The Mission

> **To build the foundation for an AI system that reasons over automotive knowledge — grounding every diagnosis in evidence, understanding the physical reality of vehicles, and serving every person who needs to know why their car is failing.**
>
> Our near-term mission is to construct the engineering infrastructure, research pipeline, and knowledge-first architecture that makes that reasoning system possible — starting with the foundation we are laying in this repository.

## What the Mission Means in Practice

### 1. Foundation First

We are a seed-stage company. Our first mission is not "ship a chatbot." It is to build:

- A rigorous engineering foundation (this repository).
- A research program into automotive knowledge representation and reasoning.
- A data strategy for workshop manuals, TSBs, wiring diagrams, and OBD-II.
- A team culture where correctness, evidence, and long-term maintainability are non-negotiable.

### 2. Evidence-Based Reasoning

The mission is to move past "plausible-sounding text" toward **reasoning with evidence**. Every claim the system makes should be traceable. That mission shapes our research: knowledge graphs over naive RAG, causal fault models over keyword search.

### 3. Serving the Full Spectrum of Users

We believe the same underlying reasoning engine should serve:

- A **DIY homeowner** asking "why is my brake light on?"
- A **professional technician** diagnosing a fault with a scope and a wiring diagram.
- A **fleet operator** monitoring thousands of vehicles and needing a prioritized repair queue.
- A **privacy-sensitive customer** who wants the system to run entirely on-premises.

This mission shapes the architecture: core reasoning capability now, multiple surfaces later.

## Our Shared Values in Action

| Value | What It Looks Like Day to Day |
|-------|-------------------------------|
| **Evidence over assertion** | We cite sources; we refuse to guess when we don't know. |
| **Reasoning over retrieval** | We build toward understanding *why*, not just finding *what*. |
| **Quality over speed** | We write tests, maintain docs, and review thoroughly — even at seed stage. |
| **Agents as teammates** | We build so both humans and AI agents can contribute safely. |
| **Transparency** | We record decisions (ADRs), keep the roadmap public to the team, and document assumptions. |

## How This Mission Evolves

This mission document is near-term by design. It will be reviewed and updated as we move from foundation → research prototype → product. When we shift focus (e.g., from infrastructure to a specific customer segment), that shift is a significant decision and should be recorded as an ADR and reflected in this document.

## The Relationship Between Mission and Vision

```
                    ┌─────────────────────────┐
                    │        VISION           │
                    │  World's most intelligent│
                    │  AI mechanic (decade)    │
                    └────────────┬────────────┘
                                 │ informs
                    ┌────────────▼────────────┐
                    │        MISSION          │
                    │  Build the foundation & │
                    │  reasoning architecture │
                    │  (now → near-term)       │
                    └────────────┬────────────┘
                                 │ informs
                    ┌────────────▼────────────┐
                    │      ROADMAP            │
                    │  Concrete milestones    │
                    └────────────┬────────────┘
                                 │ breaks into
                    ┌────────────▼────────────┐
                    │    SPRINT / TASKS       │
                    │  Weekly work            │
                    └─────────────────────────┘
```

In short: **vision** gives direction, **mission** gives focus, **roadmap** gives milestones, and **tasks** give this week's work. Every layer is traceable up to the vision.

## Reading This Document

1. **New team members** read this to understand current focus and how their work connects to the mission.
2. **AI agents** read this to ensure their contributions align with the company's current priorities.
3. **Leadership** uses this document, along with the roadmap, to make prioritization decisions.