# Research: Evaluation and Benchmarks

## Why This Document Exists

This document addresses **how we measure whether MechAI actually works**. It exists because "the system gives an answer" is not the same as "the system reasons correctly." For a product whose entire value is evidence-based reasoning, evaluation is foundational.

This doc defines the research direction for benchmarks: how we measure diagnostic accuracy, reasoning quality, grounding, and uncertainty. Without good evaluation, we can't know if we're building an intelligent mechanic or a confident chatbot.

## The Research Question

> How do we build evaluation and benchmark systems that measure whether MechAI **correctly reasons** over automotive knowledge — with evidence, grounding, and appropriate uncertainty — rather than just producing plausible text?

## Why Evaluation Is Hard (for AI Systems)

- **Non-determinism:** LLM outputs vary. A single pass doesn't prove correctness.
- **Ground truth is hard to define:** What is the "correct" diagnosis for a set of symptoms? Experts often disagree.
- **Reasoning vs. recall:** Getting the right answer isn't the same as reasoning correctly. We need to evaluate *both* the answer and the reasoning.
- **Safety matters:** Wrong diagnoses can lead to unsafe actions. Evaluation must catch dangerous errors.
- **Grounding is subtle:** An answer can be correct but ungrounded (lucky guess), or grounded but wrong (conflicting sources).

## What We Need to Measure

### 1. Diagnostic Accuracy

**Question:** Does the system identify the correct fault, given the evidence?

**Metrics:**
- **Top-1 accuracy:** Is the top-ranked diagnosis correct?
- **Top-K accuracy:** Is the correct diagnosis in the top K?
- **Ranked list quality:** How well does the system rank the true cause vs. alternatives?
- **Confusion analysis:** What types of faults does it get wrong, and how?

### 2. Reasoning Quality

**Question:** Does the system justify its diagnosis with sound reasoning?

**Metrics:**
- **Causal validity:** Is the reasoning chain from evidence to conclusion physically sound?
- **Completeness:** Does it consider the relevant evidence and alternative hypotheses?
- **Explainability:** Can a human review the reasoning trace and understand *why*?

### 3. Grounding & Provenance

**Question:** Are the claims traceable to sources?

**Metrics:**
- **Citation accuracy:** Does each claim have a correct, relevant source?
- **Hallucination rate:** How often does the system make claims unsupported by sources?
- **Grounding coverage:** What fraction of the answer is grounded vs. inferred?

### 4. Uncertainty Calibration

**Question:** When the system says it's 80% confident, is it right 80% of the time?

**Metrics:**
- **Calibration error:** How well does confidence match actual accuracy?
- **Abstention accuracy:** When the system says "I don't know," is it correct to be unsure?
- **Confident-error rate:** How often is the system confidently wrong?

### 5. Safety

**Question:** Does the system behave safely when it encounters safety-critical topics?

**Metrics:**
- **Safety warning rate:** Does it warn and escalate on safety-critical topics?
- **Dangerous advice rate:** How often does it give advice that could be physically unsafe?

## Benchmark Construction

### Sources of Benchmark Data

- **Expert-curated cases:** Automotive technicians create realistic diagnostic cases with ground-truth faults.
- **Synthetic cases:** Generated from known fault-symptom relationships in the knowledge graph.
- **Real-world data (future):** Anonymized, consented diagnostic sessions (requires privacy processes).

### Benchmark Design Principles

1. **Held-out data:** Benchmarks must not overlap with training/development data. We only get to measure this once.
2. **Multiple difficulty levels:** From simple (single DTC, clear cause) to hard (conflicting evidence, concurrent faults).
3. **Coverage:** Benchmarks cover multiple vehicle systems (engine, braking, charging, cooling, etc.).
4. **Vetted ground truth:** Every case has a verified correct diagnosis.
5. **Versioned:** Benchmarks are versioned like code. Changes to a benchmark are a reviewable change.

## Evaluation Process

### 1. Define the Evaluation

- Define the metric(s) before running. Avoid "moving the goalposts."
- Specify the benchmark version and the model/system under test.

### 2. Run the Evaluation

- Run the system against the benchmark with a fixed seed and configuration.
- Record outputs, reasoning traces, and confidence.
- Repeat if non-deterministic (measure variance).

### 3. Analyze

- Compute the metrics.
- Analyze failures: why did the system get this wrong?
- Look for patterns: is it bad at a specific system, type of evidence, or uncertainty level?

### 4. Document & Decide

- Record findings in research docs.
- If the evaluation reveals a design problem, iterate (research loop).
- If a metric meets the target, record the threshold as a standard.

## The Diagnostic Benchmark (Planned)

We will build a **held-out diagnostic benchmark** — the MechAI ability benchmark — that measures:

- Diagnostic accuracy (Top-1, Top-K).
- Reasoning quality (causal validity, completeness).
- Grounding (citation accuracy, hallucination rate).
- Uncertainty calibration.

This benchmark is the objective measure of whether we're approaching the vision of "an intelligent mechanic."

### Benchmark Checklist

- [ ] Expert-curated cases with verified ground truth.
- [ ] Multiple vehicle systems covered.
- [ ] Multiple difficulty levels.
- [ ] Synthetic cases for coverage.
- [ ] Held-out from development.
- [ ] Versioned.
- [ ] Documented evaluation protocol.

## How to Use This Document

1. **Building a benchmark?** Follow the design principles.
2. **Evaluating a system?** Follow the evaluation process.
3. **Making a measurement claim?** Cite the benchmark version and protocol.

## Related Documents

- [Research Overview](01-research-overview.md) — how we research.
- [Knowledge Representation](02-knowledge-representation.md) — what we're evaluating.
- [Testing Philosophy](../engineering/05-testing-philosophy.md) — code-level testing.
- [Product Philosophy](../03-product-philosophy.md) — the principles we're measuring against.