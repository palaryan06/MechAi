# Risk & Assumptions

## Why This Folder Exists

This folder captures the **risks, assumptions, and unknowns** that could affect MechAI's success. It exists so that we are explicit about what could go wrong, what we are assuming, and what we don't yet know.

Being explicit about uncertainty is a core value. It helps us prioritize research, de-risk decisions, and avoid surprises.

## Documents in This Folder

| Document | Purpose |
|----------|---------|
| [`01-risk-register.md`](01-risk-register.md) | The risk register: identified risks, likelihood, impact, and mitigation. |
| [`02-known-assumptions.md`](02-known-assumptions.md) | The assumptions we are making and why. |
| [`03-known-unknowns.md`](03-known-unknowns.md) | The things we don't know yet that could affect the direction. |

## How to Use This Folder

1. **Before a significant decision**, check the risk register and known unknowns.
2. **When you identify a new risk**, add it to the register.
3. **When you challenge an assumption**, document it and discuss.
4. **When you resolve an unknown**, move it to a finding and record it (research doc or ADR).

## Relationship to Other Folders

- **Research** ([`../research/`](../research/)) explores and resolves unknowns.
- **ADRs** ([`../adr/`](../adr/)) record decisions made in response to risks/unknowns.
- **Roadmap** ([`../roadmap/`](../roadmap/)) reflects the impact of risks on priorities.

*This folder is a living part of the repository. Risks, assumptions, and unknowns change as we learn.*