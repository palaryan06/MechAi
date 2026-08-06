# Repository Guide

## Why This Document Exists

This document is the **map of the MechAI repository**. It explains every top-level folder, its purpose, and how to navigate the codebase. It is the first document a new contributor (human or AI agent) should read to understand where things live and where new things should go.

## Repository Layout

```
MechAI/
├── README.md                  # Project overview and entry point
├── LICENSE                    # Proprietary license (TBD)
├── SECURITY.md                # Security policy
├── CONTRIBUTING.md            # How to contribute
├── .gitignore                 # What not to commit
│
├── docs/                      # All documentation (single source of truth)
│   ├── README.md              # Documentation index
│   ├── 01-vision.md           # Product vision
│   ├── 02-mission.md          # Product mission
│   ├── 03-product-philosophy.md  # Product principles
│   ├── 04-development-philosophy.md  # Development principles
│   │
│   ├── architecture/          # System architecture
│   ├── engineering/           # Engineering standards & philosophies
│   ├── processes/             # Git, branch, task, sprint workflows
│   ├── agents/                # AI agent handbook & memory system
│   ├── adr/                   # Architectural Decision Records
│   ├── research/              # Domain research
│   ├── roadmap/               # Product & engineering roadmap
│   ├── reference/             # Glossaries & reference material
│   └── risk/                  # Risk register, assumptions, unknowns
│
├── src/                       # (Future) Product source code
│   └── README.md              # Source code conventions
│
├── tests/                     # (Future) Test suite
│   └── README.md              # Test conventions
│
├── experiments/               # Throwaway research & prototyping
│   └── README.md              # Experiment conventions
│
├── prompts/                   # Curated, versioned prompt library
│   └── README.md              # Prompt conventions
│
├── tasks/                     # Lightweight task tracking for agents
│   └── README.md              # Task conventions
│
└── memory/                    # AI agent memory system (committed)
    └── README.md              # Memory conventions
```

## Top-Level Folders

### `docs/`

**Purpose:** The single source of truth for all MechAI knowledge.

**How to use:** Start with [`docs/README.md`](../README.md) for the index. Each subfolder has its own README explaining its purpose. Documentation is code: it is reviewed, maintained, and held to a high standard.

### `src/`

**Purpose:** (Future) Product source code. This folder does not yet contain product logic — the repository is intentionally foundation-only.

**How to use:** When product code arrives, it will live here. The `src/README.md` will document the module structure and conventions. Until then, do not create product code in this repository.

### `tests/`

**Purpose:** (Future) Test suite.

**How to use:** When tests arrive, they will live here, mirroring the `src/` structure. See [Testing Philosophy](../engineering/05-testing-philosophy.md).

### `experiments/`

**Purpose:** Scratch space for throwaway research, prototyping, and investigation.

**How to use:** Experiments are **not** production code. They are for answering questions ("does this approach work?") quickly. Each experiment gets its own subfolder with a README explaining the question, approach, and findings. See [`experiments/README.md`](../../experiments/README.md).

### `prompts/`

**Purpose:** A curated, versioned library of prompts used by the product and by AI agents.

**How to use:** Prompts are treated as code: versioned, reviewed, and tested. Each prompt has a clear purpose and version history. See [`prompts/README.md`](../../prompts/README.md).

### `tasks/`

**Purpose:** Lightweight task tracking for AI agents and humans.

**How to use:** Tasks are simple markdown files describing a unit of work. They are the bridge between the roadmap and the work. See [`tasks/README.md`](../../tasks/README.md).

### `memory/`

**Purpose:** The committed AI agent memory system.

**How to use:** This folder stores persistent knowledge that AI agents write and read across sessions. It is committed to the repository so all agents share the same context. See [Memory System](../agents/02-memory-system.md).

## Naming Conventions

- **Folders:** `kebab-case` (e.g., `architecture-overview`, `data-flows`).
- **Markdown files:** `NN-name.md` where `NN` is a zero-padded sequence number for ordering (e.g., `01-vision.md`, `02-mission.md`).
- **Source files (future):** Follow the language conventions (Python: `snake_case.py`).
- **Branches:** `type/description` (e.g., `feat/obd-parser`, `docs/architecture-v2`). See [Branch Strategy](../processes/03-branch-strategy.md).

## Where Should New Things Go?

| If you are... | Put it in... |
|---------------|--------------|
| Writing a new standard or philosophy | `docs/engineering/` |
| Recording a significant technical decision | `docs/adr/` |
| Exploring a research question | `docs/research/` or `experiments/` |
| Writing a prompt for the product or agents | `prompts/` |
| Tracking a unit of work | `tasks/` |
| Writing agent guidance | `docs/agents/` |
| Writing product direction | `docs/` (top-level numbered docs) |
| Writing about risk or assumptions | `docs/risk/` |
| Writing about the roadmap | `docs/roadmap/` |
| Writing about the architecture | `docs/architecture/` |

## How to Navigate as a New Contributor

1. Read the [README](../../README.md) for the project overview.
2. Read this document to understand the layout.
3. Read the [Engineering Handbook](../engineering/01-engineering-handbook.md) for how we work.
4. Read the [AI Agent Handbook](../agents/01-ai-agent-handbook.md) if you are an agent.
5. Read the [Documentation Standards](../engineering/07-documentation-standards.md) before writing any doc.

## Related Documents

- [Architecture Overview](01-architecture-overview.md) — the system design.
- [Engineering Handbook](../engineering/01-engineering-handbook.md) — how we work.
- [AI Agent Handbook](../agents/01-ai-agent-handbook.md) — how agents work here.
