# Security Philosophy

## Why This Document Exists

This document defines **how we think about security** in MechAI. It exists because MechAI will eventually process vehicle diagnostic data, personal information, and connected-car data. Security is not a feature — it is a foundation. This document explains the security mindset every contributor should have.

## Core Principles

1. **Assume breach.** Design every layer as if the layer below has been compromised.
2. **Least privilege.** Services, users, and agents get the minimum permissions required.
3. **Fail secure.** When something fails, it fails closed, not open.
4. **Secrets never enter the repository.** Ever.
5. **Defense in depth.** Multiple layers of protection; no single point of failure.
6. **Security is everyone's job.** Not just the "security person" — everyone.

## The Threat Model

MechAI faces several categories of threats. Understanding them shapes our design.

### 1. Prompt Injection

**Threat:** An attacker crafts input (a user prompt, a document, an image) that causes the LLM to behave maliciously — leak data, ignore instructions, or produce harmful output.

**Mitigations:**
- Treat all external content (user prompts, retrieved documents, images) as **untrusted**.
- Separate instructions from data in prompts.
- Validate and sanitize all inputs at the boundary.
- Never put secrets in prompts.
- Design the reasoning engine to ground answers in trusted sources, not raw model output.

### 2. Data Exfiltration

**Threat:** Sensitive data (vehicle data, customer PII, proprietary knowledge) leaks out of the system.

**Mitigations:**
- Least privilege on data access.
- No PII or vehicle identifiers in logs (see [Logging Philosophy](04-logging-philosophy.md)).
- On-premises deployment keeps data local.
- Access controls on all data stores.

### 3. Supply Chain

**Threat:** A compromised dependency (library, model, container image) introduces a vulnerability.

**Mitigations:**
- Pin dependencies. No `latest` tags in production.
- Review dependencies before adding them (see [Engineering Handbook](01-engineering-handbook.md)).
- Scan dependencies for known vulnerabilities (future CI step).
- Use pinned base images for containers.

### 4. Infrastructure

**Threat:** An attacker gains access to the infrastructure (servers, databases, cloud accounts).

**Mitigations:**
- Least privilege on all cloud IAM roles.
- Network segmentation; default-deny egress.
- No container runs as root unless unavoidable.
- Secrets managed outside the repository.

### 5. Model & Reasoning Integrity

**Threat:** The system produces unsafe or incorrect diagnoses, or is manipulated to do so.

**Mitigations:**
- Ground every claim in evidence (see [Product Philosophy](../03-product-philosophy.md)).
- Quantify uncertainty; say "I don't know" when appropriate.
- Safety-critical topics (brakes, airbags, fuel) trigger conservative behavior.
- Reasoning traces are inspectable.

## Security in the Development Lifecycle

| Stage | Security Practice |
|-------|-------------------|
| **Design** | Threat model new features; record security decisions in ADRs |
| **Implementation** | Input validation, no secrets in code, secure logging |
| **Testing** | Security tests: injection attempts, malformed input, auth bypass |
| **Review** | Security checklist in code review |
| **Deployment** | Least privilege, secrets manager, network segmentation |
| **Operations** | Monitoring, alerting, incident response |

## Security Checklist for Code Review

- [ ] No secrets, keys, or credentials in code or config
- [ ] All external input is validated and sanitized
- [ ] No PII or vehicle identifiers in logs
- [ ] Least privilege on data access
- [ ] Dependencies are pinned and justified
- [ ] Error messages don't leak internal details
- [ ] Authentication/authorization is enforced (where applicable)
- [ ] Prompt injection is considered (for AI features)

## Security for AI Agents

AI coding agents working in this repository must:

- **Never write secrets to files.** Use environment variables.
- **Never commit** `.env`, `*.pem`, `*.key`, or credential files.
- **Never log** tokens, passwords, API keys, PII, or vehicle data.
- **Never include** real customer data or real VINs in tests, examples, or docs.

See the [AI Agent Handbook](../agents/01-ai-agent-handbook.md) for agent-specific rules.

## Incident Response

When a security incident occurs:

1. **Contain.** Stop the bleeding. Isolate affected systems.
2. **Assess.** Determine scope and impact.
3. **Report.** Notify the team and, if required, affected parties.
4. **Remediate.** Fix the root cause.
5. **Learn.** Write a post-mortem; update this document and relevant ADRs.

## Related Documents

- [Security Policy](../../SECURITY.md) — the formal security policy.
- [Logging Philosophy](04-logging-philosophy.md) — what not to log.
- [Configuration Philosophy](06-configuration-philosophy.md) — secrets management.
- [Product Philosophy](../03-product-philosophy.md) — evidence and safety.
- [AI Agent Handbook](../agents/01-ai-agent-handbook.md) — agent security rules.