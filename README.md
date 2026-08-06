# MechAI

**The world's most intelligent AI mechanic.**

MechAI is an early-stage startup building an AI system capable of *reasoning* over automotive knowledge — moving beyond simple chatbots toward true understanding of workshop manuals, vehicle diagnosis, and OBD-II data.

This repository is the engineering foundation upon which all future MechAI product work will be built. It is designed for years of development by a growing team of human engineers and AI coding agents.

---

## What This Repository Contains

This is **not** a prototype and it does **not** yet contain product logic. It is the professional foundation of an engineering organization:

| Area | Location | Purpose |
|------|----------|---------|
| Product direction | [`docs/01-vision.md`](docs/01-vision.md), [`docs/02-mission.md`](docs/02-mission.md) | Why MechAI exists and what we will become |
| Architecture | [`docs/architecture/`](docs/architecture/) | How the system is designed and will scale |
| Engineering standards | [`docs/engineering/`](docs/engineering/) | How we write, test, log, configure, and secure software |
| Processes | [`docs/processes/`](docs/processes/) | How we work: git, branches, tasks, sprints |
| AI agent guidance | [`docs/agents/`](docs/agents/) | How AI coding agents collaborate in this repository |
| Decision records | [`docs/adr/`](docs/adr/) | The ADR system for recording technical decisions |
| Research | [`docs/research/`](docs/research/) | Domain research and exploration |
| Roadmap | [`docs/roadmap/`](docs/roadmap/) | Where we are headed |
| Risk & assumptions | [`docs/risk/`](docs/risk/) | What could go wrong and what we assume |
| Experiments | [`experiments/`](experiments/) | Scratch space for throwaway investigation |
| Prompts | [`prompts/`](prompts/) | Curated, versioned prompt library |
| Task management | [`tasks/`](tasks/) | Lightweight task tracking for agents |
| Project glossary | [`docs/reference/01-project-glossary.md`](docs/reference/01-project-glossary.md) | Shared vocabulary |

## Quick Navigation

- **New human engineer?** Start with the [Engineering Handbook](docs/engineering/01-engineering-handbook.md) and the [Repository Guide](docs/architecture/02-repository-guide.md).
- **New AI agent?** Read the [AI Agent Handbook](docs/agents/01-ai-agent-handbook.md).
- **Want to contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md).
- **Deciding the tech stack?** Review the [Decision Records](docs/adr/README.md).

## Tenets

These principles guide every decision in this repository:

1. **Reason, don't parrot.** MechAI must reason over automotive knowledge, never act as a shallow chatbot.
2. **Long-term maintainability over short-term speed.** Every file, folder, and decision should still make sense in five years.
3. **Documentation is code.** Documentation is maintained, reviewed, and held to the same quality bar as source code.
4. **Agents are part of the team.** The repository must support humans and AI agents working side by side.
5. **Favor clarity over cleverness.** Readable, boring, well-structured code outlives clever hacks.
6. **Decisions are recorded.** If it matters, it gets an ADR.

## Repository Status

- **Phase:** Foundation (Seed)
- **Product logic:** None (intentionally)
- **Language scaffolding:** Python (declared, not yet implemented)
- **Status badge:** *(add CI badge once CI is established)*

## Getting Started

There is no product code to run yet. To explore the foundation:

```bash
# List the documentation index
cat docs/README.md

# View the engineering handbook
cat docs/engineering/01-engineering-handbook.md
```

When product code arrives, build and run instructions will live here.

## License

See [LICENSE](LICENSE).

## Security

See [SECURITY.md](SECURITY.md).