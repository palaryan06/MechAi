# Experiments

## Why This Folder Exists

This folder is the **scratch space for research and prototyping**. It exists so that we can test ideas quickly — "does this approach work?" — without polluting the production codebase.

Experiments are **throwaway by design**. They are for learning, not for production. When an experiment proves an approach, the learning moves to a research doc and the decision to an ADR. The experiment code itself may be deleted.

## How Experiments Work

### 1. Create an Experiment

Each experiment gets its own subfolder with a descriptive name:

```
experiments/
├── README.md
├── 01-embedding-benchmark/
│   ├── README.md          # What, why, how, findings
│   ├── run.py             # The experiment code
│   └── results/           # Output (gitignored)
└── 02-obd-parser-proto/
    ├── README.md
    └── ...
```

### 2. Document the Experiment

Each experiment folder has a README that answers:

- **Question:** What are we trying to learn?
- **Approach:** How are we testing it?
- **Findings:** What did we learn?
- **Status:** Active | Complete | Abandoned
- **Next steps:** What should happen next?

### 3. Run and Learn

- Keep experiments fast and focused.
- Prototype the riskiest assumption first.
- Record findings honestly, including failures.

### 4. Resolve

When an experiment is done:

- **If it worked:** Move the learning to a research doc; record the decision as an ADR.
- **If it failed:** Record the finding (what didn't work and why) — this is valuable too.
- **Mark the experiment** Complete or Abandoned.

## Rules for Experiments

- **Experiments are not production code.** They don't need to follow all production standards, but they should be readable.
- **No secrets in experiments.** Same rules as everywhere.
- **No real customer data or VINs.** Use synthetic data.
- **Keep experiments small.** If an experiment grows into a real component, move it to `src/`.
- **Artifacts are gitignored.** Large outputs, models, and data go in `artifacts/` or `output/` (gitignored).

## Experiments vs Research Docs

| | Experiments | Research docs |
|---|---|---|
| Location | `experiments/` | `docs/research/` |
| Content | Code, data, scratch work | Findings, reasoning, references |
| Lifetime | Short-lived (may be deleted) | Long-lived (a living record) |
| Purpose | Test *does this work* | Explain *what we know and why* |

## How to Use This Folder

1. **Testing an idea?** Create an experiment folder.
2. **Learning something?** Record it in a research doc.
3. **Making a decision?** Record it as an ADR.

## Related Documents

- [Research](../docs/research/README.md) — where findings are documented.
- [ADR System](../docs/adr/README.md) — where decisions are recorded.
- [Repository Guide](../docs/architecture/02-repository-guide.md) — where things live.
