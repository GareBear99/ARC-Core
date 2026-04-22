<!-- Thanks for contributing to ARC-Core. Please fill this out fully. -->

## Summary

<!-- One sentence. -->

## Type of change

- [ ] Bug fix
- [ ] New feature (new event type, new service, new API, new UI page)
- [ ] Receipt format change (requires explicit call-out)
- [ ] Authority / role change
- [ ] Documentation
- [ ] Cross-repo integration (link the sibling issue/PR)

## Role-boundary preservation

ARC-Core owns **authority, events, and receipts** — nothing else.

- [ ] This PR does not push execution logic into ARC-Core (that's Cleanroom).
- [ ] This PR does not push model doctrine into ARC-Core (that's Cognition Core).
- [ ] This PR does not push lexical truth into ARC-Core (that's Language Module).
- [ ] This PR does not push archive-bundle logic into ARC-Core (that's Arc-RAR).
- [ ] This PR does not push binary-execution logic into ARC-Core (that's OmniBinary).

See [ECOSYSTEM.md](../ECOSYSTEM.md).

## Evidence

- [ ] `pytest -q` passes in `ARC_Console/`.
- [ ] If this changes the receipt format, a migration note is added and downstream repos are flagged.
- [ ] New public endpoints / event types have tests.

## Documentation

- [ ] README, ECOSYSTEM, docs/ARCHITECTURE, docs/STACK, or CHANGELOG updated as needed.

## Linked issues

<!-- Closes #123, Related to #456 -->

## Cross-repo impact

<!-- Does this change affect Cleanroom / Cognition Core / LLMBuilder / Language Module / OmniBinary / Arc-RAR? List the sibling PRs/issues. -->
