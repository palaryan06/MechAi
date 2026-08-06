# Security Policy for MechAI

MechAI is building infrastructure that will eventually process vehicle diagnostic data, personal information, and connected-car data. Security is a foundational concern. This document explains how we handle security in this repository.

## Scope

This policy applies to all code, documentation, configuration, and infrastructure associated with the MechAI project. It is relevant to both human engineers and AI coding agents contributing to this repository.

## Guiding Principles

1. **Assume breach.** Every layer is designed as if the layer below has been compromised. We plan for defense-in-depth.
2. **Least privilege.** Services, users, and agents get the minimum permissions required.
3. **Fail secure.** When something fails, it fails closed, not open.
4. **Secrets never enter the repository.** Secrets are managed outside of git.
5. **Log, monitor, alert, respond.** We can't protect what we can't see.

## Reporting a Vulnerability

If you discover a security vulnerability in MechAI code, infrastructure, or documentation:

- **Do NOT open a public issue or PR.**
- **Email** security@mechai.example.com with a clear description.
- Include: affected component, version/commit where identified, reproduction steps, and any suggested impact assessment.

We will acknowledge receipt within 5 business days and work to triage and release a fix. We ask researchers to allow a reasonable disclosure window before public announcement.

## Handling Security for Agents

AI coding agents that work in this repository must:

- **Never write secrets to files.** Use environment variables or a secrets manager.
- **Never commit** `.env`, `*.pem`, `*.key`, service account JSON, or credential files. `.gitignore` excludes these; agents must respect that.
- **Never log** tokens, passwords, API keys, PII, or diagnostic data at any log level.
- **Never include** real customer data or real vehicle VINs in tests, examples, fixtures, or docs. Use synthetic data at all times.

## Secret Management: Current & Future

| Stage | Approach |
|-------|----------|
| **Now (seed)** | Environment variables only. No secret files in the repo. `.env.example` documents needed variables without values. |
| **Future (post-MVP)** | Move to a secrets manager (e.g., cloud KMS / Vault). Secrets become first-class config, injected at runtime. See [Configuration Philosophy](docs/engineering/06-configuration-philosophy.md). |

## Secure Development Practices

- **Input validation:** All external input (vehicle data, user prompts, uploaded images) must be validated and sanitized at the boundary.
- **Prompt injection:** As an AI product, we must treat LLM prompts and external content as untrusted. See [Security Philosophy](docs/engineering/08-security-philosophy.md) for the agentic RAG threat model.
- **Dependencies:** Dependencies are pinned and reviewed. We add a dependency only when it serves a clear purpose (see [Engineering Handbook](docs/engineering/01-engineering-handbook.md)).
- **Docker:** No container runs as root unless unavoidable. Images are rebuilt from pinned base images; no `latest` tags in production.
- **Network:** Default-deny egress. Services only reach what they need.

## Compliance & Future Notes

MechAI will eventually handle personal data. Before handling real customer PII or vehicle data:

1. A **privacy ADR** must document the data flows, storage locations, and retention policies.
2. Data processing agreements and legal review apply.
3. Regional data-residency requirements (e.g. GDPR, CCPA) will be addressed in the [Future Scaling Philosophy](docs/engineering/09-future-scaling-philosophy.md).

This policy will evolve. Significant changes will be recorded as ADRs.