# Documentation Standards

## Why This Document Exists

This document defines **how we write documentation** in MechAI. It exists because documentation is a first-class artifact in this repository — it is code. Consistent, purposeful documentation is what makes the repository navigable for 20+ engineers and multiple AI agents.

## Core Principles

1. **Purpose first.** Every document states its purpose up front.
2. **No fluff.** If a sentence doesn't help a reader make a decision or take an action, remove it.
3. **Explain why, not just what.** The "why" is what future contributors need.
4. **Diagrams where useful.** A good diagram is worth a thousand words.
5. **Living documents.** Docs are maintained as the code changes. Stale docs are a bug.

## Document Structure

Every document follows this structure:

1. **Title** — `# Document Name`
2. **Why This Document Exists** — the purpose, up front.
3. **Body** — the content, organized with clear headings.
4. **How to Use This Document** — who should read it and when.
5. **Related Documents** — links to related docs.

## The "Why This Document Exists" Section

Every document starts with a section explaining:

- **Why** this document exists.
- **Who** it is for.
- **What** question it answers.

This ensures readers can quickly determine if a document is relevant to them.

## Writing Style

- **Be concise.** Prefer short sentences and clear language.
- **Be specific.** Use concrete examples over abstract descriptions.
- **Use active voice.** "The system retrieves documents" not "Documents are retrieved by the system."
- **Use tables** for comparisons and structured data.
- **Use code blocks** for code, commands, and configuration.
- **Use Mermaid** for diagrams where possible.

## Diagrams

- Use [Mermaid](https://mermaid.js.org/) syntax for diagrams so they render on GitHub.
- Use ASCII art for simple diagrams or when Mermaid is overkill.
- Keep diagrams focused. A diagram that tries to show everything shows nothing.

## Naming & Placement

- Follow the [Naming Conventions](02-naming-conventions.md).
- Place docs in the correct folder (see [Repository Guide](../architecture/02-repository-guide.md)).
- Use `NN-name.md` for ordered documents.

## Links

- Use **relative links** between docs.
- Link to the **specific document**, not just the folder.
- Keep links correct. A broken link is a bug.

## Documentation as Code

- **Docs are reviewed** in PRs like code.
- **Docs are updated** when behavior changes, in the same PR.
- **Docs are tested** — broken links and stale content are caught in review.

## What to Document

| When | Document |
|------|----------|
| A new standard or philosophy | `docs/engineering/` |
| A significant technical decision | `docs/adr/` (an ADR) |
| A research question or finding | `docs/research/` |
| A product direction | `docs/` (top-level numbered docs) |
| A unit of work | `tasks/` |
| A prompt for the product or agents | `prompts/` |
| Agent guidance | `docs/agents/` |
| Architecture | `docs/architecture/` |
| Risk or assumptions | `docs/risk/` |

## Documentation Checklist

Before merging a doc, check:

- [ ] States its purpose up front
- [ ] Is concise and free of fluff
- [ ] Explains the "why"
- [ ] Uses diagrams where they help
- [ ] Follows naming and placement conventions
- [ ] Links are correct
- [ ] Is up to date with the current state of the system

## How to Use This Document

1. **Before writing a doc**, read this document.
2. **When reviewing a doc**, use the checklist above.
3. **When you see stale docs**, fix them in a small, focused PR.

## Related Documents

- [Naming Conventions](02-naming-conventions.md) — how to name docs.
- [Repository Guide](../architecture/02-repository-guide.md) — where docs live.
- [ADR System](../adr/README.md) — how to write ADRs.
- [Engineering Handbook](01-engineering-handbook.md) — the core rules.