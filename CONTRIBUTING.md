# Contributing to ARC-Core

Thank you for contributing. ARC-Core is the **authority layer** for the seven-repo ARC ecosystem. Contributions that preserve role boundaries land fast. Contributions that try to cross them (pushing execution, model doctrine, lexical truth, or archive-bundle logic into ARC-Core) rarely land at all.

## Before you start

1. Read [ECOSYSTEM.md](./ECOSYSTEM.md) to see which repo really owns the change you want to make.
2. Read [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) and [docs/STACK.md](./docs/STACK.md) for ARC-Core's internal design.
3. Browse [open issues](https://github.com/GareBear99/ARC-Core/issues) and [Discussions](https://github.com/GareBear99/ARC-Core/discussions).

## Setup

```bash
git clone https://github.com/GareBear99/ARC-Core.git
cd ARC-Core/ARC_Console

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest -q            # should say: 13 passed
python run_arc.py    # starts FastAPI on 127.0.0.1:8000
```

## Role-boundary rules

ARC-Core owns **authority, events, and receipts**. Any PR that pushes other responsibilities into ARC-Core should instead go to the correct sibling:

- Execution logic → [arc-lucifer-cleanroom-runtime](https://github.com/GareBear99/arc-lucifer-cleanroom-runtime)
- Model doctrine / promotion gates → [arc-cognition-core](https://github.com/GareBear99/arc-cognition-core)
- Governed build loop / Gate v2 → [ARC-Neuron-LLMBuilder](https://github.com/GareBear99/ARC-Neuron-LLMBuilder)
- Lexical / multilingual truth → [arc-language-module](https://github.com/GareBear99/arc-language-module)
- Binary mirror / runtime ledger → [omnibinary-runtime](https://github.com/GareBear99/omnibinary-runtime)
- Archive / rollback bundles → [Arc-RAR](https://github.com/GareBear99/Arc-RAR)

## PR checklist

- [ ] `pytest -q` passes in `ARC_Console/`.
- [ ] Role boundaries preserved (see ECOSYSTEM.md).
- [ ] If the receipt format changes: migration note added, siblings flagged.
- [ ] New public event types or API endpoints have tests.
- [ ] README / ECOSYSTEM / docs updated as needed.
- [ ] CHANGELOG entry added.

## Commit style

- Imperative mood: "Add X", "Fix Y", "Harden Z".
- Wrap body at ~72 columns.
- When changing receipt formats or authority contracts, include evidence in the body: sample receipt, migration path, sibling impact.

## License

By contributing, you agree your contributions are MIT-licensed. See [LICENSE](./LICENSE).

## Questions

- [💬 GitHub Discussions](https://github.com/GareBear99/ARC-Core/discussions)
- [SUPPORT.md](./SUPPORT.md)
- [💖 Sponsor](https://github.com/sponsors/GareBear99)
