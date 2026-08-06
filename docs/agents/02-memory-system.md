# Memory System for AI Agents

## Why This Document Exists

This document defines the **persistent memory system** for AI coding agents in the MechAI repository. It exists because AI agents do not retain context between sessions. Without a memory system, every agent session starts from scratch — re-reading the entire repository, re-discovering conventions, and re-learning what previous agents already figured out.

The memory system gives agents a durable, shared knowledge store. It makes agents more effective, reduces duplicated work, and improves coordination between multiple agents and humans.

## Design Principles

1. **Agent-readable and human-readable.** Memory is Markdown — readable by both agents and humans.
2. **Committed to the repository.** Memory lives in git, so all agents share the same context and history.
3. **Concise and factual.** Memory entries state facts and decisions, not vague musings.
4. **No secrets.** Memory files never contain API keys, tokens, credentials, PII, or vehicle data.
5. **Curated, not exhaustive.** Memory captures the *important* things — not everything.
6. **Structured by topic.** Memory is organized so agents can find what they need quickly.

## Where Memory Lives

Memory lives in the [`memory/`](../../memory/) folder at the repository root. This folder is **committed to the repository**, so it is shared across all agents and humans.

```
memory/
├── README.md                  # This system's entry point
├── 01-project-context.md      # High-level project context
├── 02-architecture-notes.md   # Architecture decisions & notes
├── 03-engineering-notes.md    # Engineering conventions & gotchas
├── 04-domain-knowledge.md     # Automotive domain knowledge
├── 05-agent-sessions.md       # Log of agent work sessions
└── 06-open-questions.md       # Open questions awaiting resolution
```

## Memory File Types

### 1. Persistent Knowledge (01-04)

These files store **durable knowledge** that doesn't change often:

- **Project context:** Mission, key documents, current priorities.
- **Architecture notes:** Why the system is shaped this way, key ADRs, component map.
- **Engineering notes:** Conventions, tooling details, gotchas, things that surprised us.
- **Domain knowledge:** Automotive domain facts the team has learned.

### 2. Session Log (05-agent-sessions.md)

This file logs **what agents did** in each session:

- Session date and agent/tool.
- Task worked on.
- Key findings and learnings.
- Files created or changed.
- Open questions left behind.

This prevents multiple agents from re-doing the same exploration.

### 3. Open Questions (06-open-questions.md)

This file tracks **unresolved questions**:

- The question.
- Why it matters.
- What's been tried.
- Who/what might resolve it.

Open questions are the seed for future research and tasks.

## How Agents Use Memory

### Before Starting Work

1. **Read** the relevant memory file(s):
   - Always skim `01-project-context.md`.
   - Read `02-architecture-notes.md` if touching architecture.
   - Read `03-engineering-notes.md` if writing code.
   - Read `04-domain-knowledge.md` if working on automotive domains.
   - Read `05-agent-sessions.md` to check for prior related work.
2. **Check** `06-open-questions.md` for questions related to your task.

### During Work

- **Reference** memory entries rather than re-deriving knowledge.
- **Note** new findings as you go (add to a session log).

### After Completing Work

1. **Update** the relevant memory file(s) with new knowledge.
2. **Append** to `05-agent-sessions.md` with a session entry.
3. **Add** any unresolved questions to `06-open-questions.md`.

## Memory Entry Format

Each entry follows a consistent format:

```markdown
### <Topic/Date> (<Date>)

- **What:** A concise statement of the fact, decision, or finding.
- **Why it matters:** Why a future agent needs to know this.
- **Source:** Where this came from (file, ADR, conversation, experiment).
- **Status:** Active | Superseded | Open | Resolved
```

## Example Entries

### Persistent Knowledge

```markdown
### Knowledge Graph Architecture (2026-08-03)

- **What:** The reasoning engine uses a knowledge graph as the primary reasoning substrate; the vector store is a complement for retrieval, not the core.
- **Why it matters:** New components must integrate with the knowledge graph, not just a vector store.
- **Source:** docs/architecture/01-architecture-overview.md
- **Status:** Active
```

### Session Log

```markdown
### Agent Session: 2026-08-03

- **Agent:** Cline
- **Task:** Establish repository foundation
- **What was done:** Created the full documentation structure (docs/), root files, and foundation folders.
- **Learnings:** Mermaid diagrams render on GitHub; use them for architecture docs.
- **Files created:** README.md, docs/**/*.md, memory/**, prompts/**, tasks/**.
- **Open questions:** Vector store technology not yet chosen; pending research.
```

### Open Question

```markdown
### Which vector store should we use? (2026-08-03)

- **Why it matters:** This is a foundational dependency for retrieval.
- **What's been tried:** Research not yet started.
- **Status:** Open
```

## Rules for Memory

### What to Store

- Durable facts and decisions.
- Architecture and engineering conventions.
- Gotchas and "things that surprised us."
- Session logs of agent work.
- Open questions.

### What NOT to Store

- **Secrets** (API keys, tokens, credentials).
- **PII or vehicle identifiers** (VINs, plates, customer data).
- **Transient state** (temporary file paths, scratch notes).
- **Large content** (link to docs rather than duplicating).
- **Unverified claims** (mark as "unverified" if speculative).

### Keeping Memory Healthy

- **Update, don't accumulate.** If a memory entry is stale, update it. Don't append "the old thing is wrong" forever.
- **Mark superseded entries.** When a decision changes, mark the old entry `Status: Superseded` and add a new Active entry.
- **Keep entries concise.** A memory file is a reference, not a report.
- **Link instead of duplicating.** If a fact lives in a doc, link to it.

## Coordination Between Agents

Because memory is committed to the repository:

- **All agents share the same memory.** This is the point.
- **Write access requires a PR** (like any code change) — unless you have explicit permission.
- **Memory changes are reviewed** for accuracy, conciseness, and security.
- **Check the session log** before exploring a topic — another agent may have already mapped it.

## Working With Local Agent State

- **Local agent state** (`.memory/`, tool-specific caches) is gitignored. This is *not* the shared memory system.
- **Shared, committed memory** lives in `memory/`. This is what agents read and write for cross-session context.
- Agents should use the committed system for anything that future agents need.

## How to Use This Document

1. **Agents:** Read the [AI Agent Handbook](01-ai-agent-handbook.md) and this document before work.
2. **Agents:** Read relevant memory entries before starting a task.
3. **Agents:** Update memory after completing work.
4. **Humans:** Review memory changes in PRs to ensure quality and security.

## Related Documents

- [AI Agent Handbook](01-ai-agent-handbook.md) — how agents work.
- [Agent Task Guide](03-agent-task-guide.md) — how agents execute tasks.
- [Repository Guide](../architecture/02-repository-guide.md) — the `memory/` folder.
- [Security Policy](../../SECURITY.md) — what never goes in memory.