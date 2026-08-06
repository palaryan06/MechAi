# Priorities

## Why This Document Exists

This document defines **how we prioritize work** at MechAI. It exists so that the team — humans and AI agents — knows what matters most and can make consistent prioritization decisions.

Without explicit priorities, teams optimize for different things and drift from the mission. This document keeps us aligned.

## The Prioritization Framework

We use a **mission-aligned, impact-first** framework:

1. **Does it serve the mission?** Work that advances the mission comes first.
2. **What is the impact?** Work that unblocks the most future work is high priority.
3. **What is the cost?** Work that is cheap and de-risks a decision is worth doing now.
4. **What is the risk?** Work that reduces uncertainty early is prioritized.

## Priority Levels

| Priority | Meaning | Example |
|----------|---------|---------|
| **P0** | Critical; blocks everything. Do now. | A security fix, a broken main, a blocked pipeline. |
| **P1** | High; important for the current milestone. | A roadmap milestone for the current phase. |
| **P2** | Medium; do when ready. | Research that informs a future phase. |
| **P3** | Low; nice to have. | Polish, nice-to-have docs, ideal improvements. |

## How We Prioritize

### 1. Seed Stage (Now)

At seed stage, we prioritize:

- **Foundation first.** The repository, standards, and processes come first.
- **Research over features.** The hard questions (knowledge representation) come before the product.
- **De-risking over demos.** We validate assumptions early rather than build on unproven ones.

### 2. As We Grow

As we grow:

- **Product milestones** from the roadmap drive priorities.
- **Customer needs** (once we have customers) weigh heavily.
- **Technical debt** is handled deliberately, not ignored.

## Prioritization Rules of Thumb

1. **P0 always wins.** Nothing takes priority over a P0.
2. **Unblock the team.** If something blocks others, it goes up in priority.
3. **De-risk early.** Prototyping the risky assumption beats polishing the safe path.
4. **Say no.** Not everything is a priority. Saying no protects the mission.
5. **Record the decision.** If a priority is contentious, record it (task or ADR).

## Agent Prioritization

AI agents are expected to:

- **Check priorities** in this document and the [Roadmap](01-roadmap.md) before starting work.
- **Work on the highest-priority task** assigned to them.
- **Raise conflicts.** If a task seems misaligned with priorities, raise it with a human.

## How to Use This Document

1. **When planning**, use this framework to set priorities.
2. **When proposing work**, state the priority and rationale.
3. **When deprioritizing**, explain why.

## Related Documents

- [Roadmap](01-roadmap.md) — the milestones.
- [Mission](../02-mission.md) — the near-term direction.
- [Task Workflow](../processes/04-task-workflow.md) — how tasks are prioritized.
- [Sprint Workflow](../processes/05-sprint-workflow.md) — how priorities become sprints.