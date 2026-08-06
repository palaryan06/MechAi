# Documentation Home

This folder is the **single source of truth** for MechAI knowledge. Everything a contributor (human or AI agent) needs to understand the product, the architecture, the standards, and the processes lives here.

## How to Use This Index

Start with the documents that are relevant to you:

```
If you are new to MechAI and want to understand why we exist:
    → 01-vision.md, 02-mission.md

If you are starting to work on code:
    → architecture/02-repository-guide.md
    → engineering/01-engineering-handbook.md
    → engineering/03-coding-standards.md

If you want to propose a change to how we work:
    → Read the relevant process doc, then write an ADR if it is a significant decision.
```

## Folder Overview

| Folder | Purpose |
|--------|---------|
| `01-vision.md` | The long-term product vision: what MechAI will become. |
| `02-mission.md` | The mission: what we do every day to get closer to the vision. |
| `03-product-philosophy.md` | Product principles: how we build products that reason, don't parrot. |
| `04-development-philosophy.md` | How we write software at MechAI: discipline, quality, and intentionality. |
| `architecture/` | System architecture, repository guide, data flows, and scaling. |
| `engineering/` | Engineering handbook, coding standards, philosophies (testing, logging, config, security, scaling). |
| `processes/` | Git workflow, branch strategy, task workflow, sprint workflow. |
| `agents/` | AI Agent Handbook, Memory System, and related agent docs. |
| `adr/` | Architectural Decision Records (the "why" behind key choices). |
| `research/` | Domain research notes and exploration. |
| `roadmap/` | The product and engineering roadmap. |
| `reference/` | Glossaries, links, and reference material. |
| `risk/` | Risk register, known assumptions, known unknowns. |

## Documentation Standards

All documentation must follow the [Documentation Standards](engineering/07-documentation-standards.md). Key points:

- **Purpose first:** Every document states its purpose up front.
- **No fluff:** If a sentence doesn't help a reader make a decision or take an action, remove it.
- **Diagrams where useful:** Architecture is explained visually; text supplements.
- **Living documents:** Docs are maintained as the code changes. Stale docs are a bug.

## How Future Contributors Should Use This

1. **Before starting work**, read the documents that apply to your task (see the table above).
2. **When a decision is significant**, add an ADR rather than only changing code.
3. **When you change behavior**, update the affected docs in the same PR.
4. **When you write a new doc**, explain *why* it exists and *how* to use it, just like these documents do.

If a document is missing and should exist, create it following the naming conventions and add a link here.