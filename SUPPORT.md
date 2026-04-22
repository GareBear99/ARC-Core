# Support

## Before you ask

Start here:

- **[README.md](./README.md)** — overview and current state
- **[ECOSYSTEM.md](./ECOSYSTEM.md)** — how ARC-Core integrates with the six sibling repos
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** — internal design
- **[docs/STACK.md](./docs/STACK.md)** — full ecosystem stack
- **[docs/CODE_SURFACE_AUDIT.md](./docs/CODE_SURFACE_AUDIT.md)** — code inventory

## First-run diagnostics

```bash
cd ARC_Console
pytest -q            # should say: 13 passed
python run_arc.py    # starts FastAPI
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/manifest
```

If any of these fail, include the output when you ask for help.

## Where to ask

| Channel | Use for |
|---|---|
| [💬 Discussions](https://github.com/GareBear99/ARC-Core/discussions) | General questions, architecture discussion, ecosystem integration |
| [🐛 Bug report](./.github/ISSUE_TEMPLATE/01_bug_report.yml) | Something is broken |
| [✨ Feature request](./.github/ISSUE_TEMPLATE/02_feature_request.yml) | Propose a new capability |
| [📚 Docs issue](./.github/ISSUE_TEMPLATE/03_docs.yml) | A doc is wrong / missing / confusing |
| [🔒 Security advisory](https://github.com/GareBear99/ARC-Core/security/advisories/new) | Private vulnerability disclosure |

## Cross-repo routing

If your question really belongs to a sibling repo, file there:

- Deterministic kernel → [Cleanroom Runtime](https://github.com/GareBear99/arc-lucifer-cleanroom-runtime)
- Cognition / model growth → [Cognition Core](https://github.com/GareBear99/arc-cognition-core)
- Governed build loop / Gate v2 → [LLMBuilder](https://github.com/GareBear99/ARC-Neuron-LLMBuilder)
- Language / lexical truth → [Language Module](https://github.com/GareBear99/arc-language-module)
- Binary mirror → [OmniBinary](https://github.com/GareBear99/omnibinary-runtime)
- Archive bundles → [Arc-RAR](https://github.com/GareBear99/Arc-RAR)

## Sponsor

Single funding target for all seven ARC repos:

**[github.com/sponsors/GareBear99](https://github.com/sponsors/GareBear99)**
