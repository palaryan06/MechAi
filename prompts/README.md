# Prompts

## Why This Folder Exists

This folder is the **curated, versioned prompt library** for MechAI. It exists because prompts are a critical part of an AI product — they are code. They must be versioned, reviewed, and tested like any other code.

Prompts are used in two contexts:
1. **Product prompts:** Prompts that drive the MechAI product (diagnosis, reasoning, grounding).
2. **Agent prompts:** Prompts that guide AI coding agents working in this repository.

## How Prompts Work

### 1. Create a Prompt

Each prompt gets its own file with a descriptive name:

```
prompts/
├── README.md
├── 01-diagnosis-prompt.md       # Product: generate a diagnosis
├── 02-evidence-extraction.md    # Product: extract evidence from sources
└── 03-agent-code-review.md      # Agent: guide code review
```

### 2. Document the Prompt

Each prompt file includes:

- **Purpose:** What this prompt is for.
- **Version:** The current version (semver).
- **Changelog:** What changed in each version.
- **Usage:** How and where this prompt is used.
- **The prompt:** The actual prompt text.

### 3. Version and Review

- Prompts are **versioned** (semver).
- Prompt changes go through **PR review** like code.
- Prompt changes are **tested** (see [Testing Philosophy](../docs/engineering/05-testing-philosophy.md)).

## Prompt Structure

```markdown
# Prompt: <Name>

## Purpose
<What this prompt is for>

## Version
<Current version, e.g., 1.0.0>

## Changelog
- 1.0.0 (2026-08-03): Initial version.

## Usage
<How and where this prompt is used>

## Prompt
<The actual prompt text>
```

## Rules for Prompts

- **No secrets in prompts.** Never put API keys, tokens, or credentials in a prompt.
- **No PII or vehicle data in prompts.** Use placeholders for user/vehicle data.
- **Prompts are versioned.** Every change is a new version.
- **Prompts are reviewed.** Changes go through PR review.
- **Prompts are tested.** Test that prompts produce the expected structure and respect constraints.
- **Keep prompts focused.** One prompt does one thing well.

## Prompt Injection Awareness

Prompts that process external content (user input, retrieved documents) must be designed with **prompt injection** in mind:

- Separate instructions from data.
- Treat external content as untrusted.
- Never put secrets in prompts.
- Validate and sanitize inputs.

See [Security Philosophy](../docs/engineering/08-security-philosophy.md).

## How to Use This Folder

1. **Writing a new prompt?** Create a file following the structure above.
2. **Changing a prompt?** Bump the version and document the change.
3. **Using a prompt?** Reference the versioned file, don't copy it into code.

## Related Documents

- [Security Philosophy](../docs/engineering/08-security-philosophy.md) — prompt injection.
- [Testing Philosophy](../docs/engineering/05-testing-philosophy.md) — testing prompts.
- [AI Agent Handbook](../docs/agents/01-ai-agent-handbook.md) — agent prompts.