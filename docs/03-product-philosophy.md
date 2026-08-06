# MechAI Product Philosophy

## Why This Document Exists

The **product philosophy** defines the principles by which we design, build, and evaluate MechAI's products. It sits between the vision (what we aspire to be) and the engineering standards (how we build). It answers: *When we make product decisions, what do we optimize for?*

Both human engineers and AI agents should read this before making product design choices. This is the document that prevents us from drifting into "just another automotive chatbot."

## The Five Pillars of Our Product Philosophy

### 1. Reason, Don't Parrot

**Principle:** The product must demonstrate *understanding*, not just fluency.

**What it means:**
- Every answer is traceable to evidence (manual, spec, sensor value, known failure mode).
- The product can explain *why* a symptom leads to a diagnosis.
- The product knows what it does **not** know, and says so.

**Implications for design:**
- We always show sources and confidence. A bare, unsourced answer is considered a bug.
- We prefer a slower, well-reasoned answer over a fast, confident-but-wrong one.
- We design the reasoning trace to be inspectable by users and engineers.

### 2. Evidence Is Everything

**Principle:** Without evidence, an answer from an AI mechanic is dangerous.

**What it means:**
- Every claim maps to a citation: a page in a manual, a wiring diagram, a TSB, a DTC spec, a measured value.
- We favor answers that incorporate live data (OBD-II, sensor readings, images) over pure text answers.
- We distinguish "verified fact" from "inference" from "hypothesis."

**Implications for design:**
- The data model must store provenance: *where did this fact come from?*
- The UI must clearly differentiate "known" from "likely" from "needs verification."

### 3. Understand the Physical World

**Principle:** Vehicles obey physics. Our reasoning must respect that.

**What it means:**
- A wiring fault, a failing sensor, and a worn mechanical part are different physical failure classes. The product must model these differences.
- Symptoms propagate through systems (e.g., a bad ground causes voltage drops that mimic sensor faults). The product must reason causally, not pattern-match.

**Implications for design:**
- Research investment in knowledge graphs and causal fault models (see [`docs/research/`](research/)).
- The product handles "conflicting evidence" gracefully, because the physical world often has concurrent faults.

### 4. Help Humans Do Better

**Principle:** MechAI amplifies human expertise; it does not replace it.

**What it means:**
- The product guides a technician through a verification procedure step by step.
- It surfaces the *next best diagnostic step*, not just a final verdict.
- It respects the user's context: a DIY homeowner needs different guidance than a seasoned tech.

**Implications for design:**
- Personas and pacing matter. We won't ship one answer that fits everyone.
- We collect feedback loops ("was this helpful? what did you do?") to improve.

### 5. Earn Trust Through Humility

**Principle:** Confident wrongness destroys trust faster than humble uncertainty.

**What it means:**
- When evidence is thin, the product says "I'm not sure — here are two checks that will help."
- We never invent torque specs, wiring colors, or fault codes.
- We are transparent about the limits of our knowledge (model coverage, data gaps).

**Implications for design:**
- Confidence and uncertainty are first-class outputs, not afterthoughts.
- We design a "I don't know" path that is still useful (triage to a human or to the right manual section).

## What We Are NOT Building

These guardrails protect the product philosophy:

- **Not a general-purpose automotive chatbot** that answers anything with plausible text.
- **Not a replacement for a qualified technician** — we are an amplifier, not a substitute.
- **Not a system that gives unsafe advice** without warning and disclaimers. When safety matters (brakes, airbags, fuel systems), the product must be conservative and escalate to a professional.
- **Not a system that hides its uncertainty** to appear smarter.

## Design Principles in Practice

| Principle | Design Choice |
|-----------|---------------|
| Reason, don't parrot | Show a reasoning trace or "why this answer" section |
| Evidence is everything | Every claim cites a source; data model stores provenance |
| Understand the physical world | Model components, systems, and fault propagation |
| Help humans do better | Offer the next diagnostic step, not just a verdict |
| Earn trust through humility | Show confidence; provide a "not sure" path |

## How This Document Is Used

1. **Product design reviews:** This document is the lens for every product decision.
2. **Research prioritization:** Research that contradicts these pillars is deprioritized.
3. **Agent contributions:** AI agents building product features must respect these pillars. An answer without a source is a violation.

## Related Documents

- [Vision](01-vision.md) — the aspirational goal.
- [Mission](02-mission.md) — what we do now.
- [Development Philosophy](04-development-philosophy.md) — how we build software.
- [Engineering Standards](engineering/README.md) — how we implement.
- [Research](research/README.md) — where we explore the hard problems.

*This philosophy is a living document. Significant changes are recorded as ADRs.*