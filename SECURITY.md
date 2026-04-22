# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities **privately** via GitHub Security Advisories:

**https://github.com/GareBear99/ARC-Core/security/advisories/new**

Do not open a public issue for security matters.

## What qualifies

ARC-Core is the **authority layer** for the ARC ecosystem. Security issues include:

- **Receipt forgery** — any way to produce a receipt that references state that did not actually exist, or any bypass of the SHA-256 identity check on the audit-log chain.
- **Authority bypass** — any way to execute a privileged action without the role / session / token check firing.
- **Case or proposal tampering** — any way to modify a case or proposal without producing a corresponding event + receipt.
- **Audit-log corruption** — any way to write to the audit log that escapes the verify endpoint.
- **Connector / ingest injection** — any way a filesystem JSONL source (or future connector) could inject unintended events or mutate state without a receipt.
- **Geospatial path traversal** — blueprint, evidence-pack, or track-import endpoints that accept user-controlled paths.
- **Session handling** — session fixation, token replay, or auth flow weaknesses.
- **Known dependency CVEs** that affect ARC-Core's actual attack surface.

## What does NOT qualify

- The receipt chain correctly rejecting your tampering attempt — that's the system working as designed.
- Feature requests dressed as security issues.
- Findings that only apply inside a local demo SQLite with no real authority boundary configured.

## Response

1. Acknowledge within 72 hours.
2. Triage severity.
3. Develop and test a fix privately.
4. Publish a coordinated advisory with credit (unless anonymous preferred).

## Cross-repo scope

Vulnerabilities that cross into sibling repos should be reported against the sibling's home:

- Deterministic execution / kernel → [Cleanroom Runtime](https://github.com/GareBear99/arc-lucifer-cleanroom-runtime/security/advisories/new)
- Cognition / model doctrine → [Cognition Core](https://github.com/GareBear99/arc-cognition-core/security/advisories/new)
- Governed build loop / Gate v2 → [LLMBuilder](https://github.com/GareBear99/ARC-Neuron-LLMBuilder/security/advisories/new)
- Language / lexical truth → [Language Module](https://github.com/GareBear99/arc-language-module/security/advisories/new)
- Binary mirror → [OmniBinary](https://github.com/GareBear99/omnibinary-runtime/security/advisories/new)
- Archive bundles → [Arc-RAR](https://github.com/GareBear99/Arc-RAR/security/advisories/new)

If in doubt, file here and we'll route.

## Dependencies

ARC-Core depends on FastAPI, Starlette, SQLite (stdlib), and the Python stdlib. Vulnerabilities in upstream packages are tracked via Dependabot security updates.
