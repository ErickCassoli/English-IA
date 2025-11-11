# Security Policy

## Supported Versions

The `main` branch is actively supported. Older releases receive security fixes on a best-effort basis.

## Reporting a Vulnerability

1. **Do not** open a public issue.
2. Email security concerns to `security@english-ia.dev` with:
   - A detailed description of the vulnerability and potential impact.
   - Steps to reproduce and proof-of-concept if possible.
   - Your suggested remediation or mitigation ideas.
3. The core team will acknowledge receipt within 3 business days and coordinate the fix, disclosure timeline, and CVE (if applicable).

We follow responsible disclosure and appreciate coordinated reports. Please avoid testing in ways that would degrade the service for other contributors.

## Handling Secrets

- Never commit credentials, API keys, or production data.
- Use `.env` (see `.env.example`) for local secrets and rotate keys regularly.
- CI and Docker images intentionally avoid embedding secrets.
