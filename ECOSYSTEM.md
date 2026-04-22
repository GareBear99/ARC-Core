# The ARC Ecosystem — ARC-Core as Authority

ARC-Core is the **root authority** in the seven-repo ARC governed-AI ecosystem. Every other repository either embeds ARC-Core's event-and-receipt discipline directly or produces artifacts that conform to its doctrine.

This document is the canonical index of **where ARC-Core is used and exactly what each sibling uses it for**.

---

## Quick map

| # | Repo | Role | Consumes ARC-Core for |
|---|---|---|---|
| 1 | **[ARC-Core](https://github.com/GareBear99/ARC-Core)** *(you are here)* | Event / receipt / authority spine | — |
| 2 | [arc-lucifer-cleanroom-runtime](https://github.com/GareBear99/arc-lucifer-cleanroom-runtime) | Deterministic operator kernel | Kernel event log shape, replay semantics |
| 3 | [arc-cognition-core](https://github.com/GareBear99/arc-cognition-core) | Model-growth lab | Promotion gate authority, training-run receipts |
| 4 | [ARC-Neuron-LLMBuilder](https://github.com/GareBear99/ARC-Neuron-LLMBuilder) | Governed build loop | Gate v2 receipts, conversation pipeline events |
| 5 | [arc-language-module](https://github.com/GareBear99/arc-language-module) | Canonical lexical truth | Self-fill arbitration, provenance flow |
| 6 | [omnibinary-runtime](https://github.com/GareBear99/omnibinary-runtime) | Binary mirror / runtime ledger | Receipts-first execution model |
| 7 | [Arc-RAR](https://github.com/GareBear99/Arc-RAR) | Archive / rollback bundles | Manifest receipts, extraction audit |

---

## 1. arc-lucifer-cleanroom-runtime

**Cleanroom's deterministic kernel is ARC-Core's discipline running at machine speed.**

### What Cleanroom uses ARC-Core for

- **Event-log shape** — Cleanroom's `KernelEngine` uses the same append-only, proposal-then-evidence-then-receipt shape that ARC-Core defines. Every kernel operation is an ARC-Core-style event with a SHA-256 identity.
- **`state_at(event_id)` replay** — the point-in-time replay semantics mirror ARC-Core's ability to reconstruct state by replaying the event log.
- **Policy evaluation** — Cleanroom's policy engine rejects operations before they execute; this is ARC-Core's authority-gating pattern pushed down into the runtime.
- **Branch planning** — speculative forks of the event log are ARC-Core receipts that haven't been committed; merging a branch promotes its receipts into the main chain.
- **Receipt recording** — every operation that executes leaves a receipt in the log.

### Where the boundary sits

- **ARC-Core owns**: the receipt format, proposal/evidence/authority contract, SHA-256 identity rules, audit-log semantics.
- **Cleanroom owns**: the deterministic execution shell, the branch/merge logic, the policy enforcement, the per-process resilience primitives.

---

## 2. arc-cognition-core

**Cognition Core treats every training run as an ARC-Core event.**

### What Cognition Core uses ARC-Core for

- **Training-run receipts** — each `lora_train`, `merge`, `gguf_export` stage writes a manifest that follows ARC-Core's receipt discipline (inputs, outputs, SHA-256 identity, authority).
- **Promotion gate v1 authority** — the original promotion gate used ARC-Core's authority-gating pattern: who may promote a candidate, under what conditions, with what evidence.
- **Benchmark schema** — tasks carry `id`, `capability`, `domain`, `difficulty`, `prompt`, `reference`, `scoring`, `tags` — all traceable via ARC-Core-style addressable identity.
- **Experiment tracking** — every run manifest is a receipt-producing event.

### Where the boundary sits

- **ARC-Core owns**: the receipt primitive, authority definition, evidence contract.
- **Cognition Core owns**: the training pipeline, the benchmark corpus, the scorer, the model-family lineage.

---

## 3. ARC-Neuron-LLMBuilder

**LLMBuilder's Gate v2 is ARC-Core's authority pattern applied to model promotion.**

### What LLMBuilder uses ARC-Core for

- **Gate v2 promotion receipts** — every promotion decision (`promote` / `archive_only` / `reject`) produces a JSON receipt with the same fields ARC-Core mandates: candidate, incumbent, evidence (scored outputs), authority (Gate v2 doctrine), SHA-256 identity.
- **Conversation pipeline events** — every `ConversationRecord` is an ARC-Core event type. The canonical conversation pipeline (`runtime/conversation_pipeline.py`) mirrors ARC-Core's ingest-then-receipt flow.
- **OBIN v2 indexed ledger** — LLMBuilder's Omnibinary ledger is structurally an ARC-Core-shaped event log with binary framing and a sidecar index.
- **Arc-RAR bundle contracts** — promoted candidate bundles are receipt-verified packages; the manifest inside each bundle is an ARC-Core-verifiable artifact.
- **Floor model updates** — floor lock operations are audit-producing events.

### Where the boundary sits

- **ARC-Core owns**: receipt shape, event identity, authority gating, evidence contract.
- **LLMBuilder owns**: the conversation pipeline, Gate v2 logic, reflection loop, language absorption, the canonical build loop.

---

## 4. arc-language-module

**The Language Module's governance is ARC-Core's provenance flow for words.**

### What the Language Module uses ARC-Core for

- **Provenance-aware ingestion** — every lemma, variant, concept, pronunciation, transliteration carries an ARC-Core-shaped provenance record: source, trust rank, timestamp, authority.
- **Self-fill arbitration** — when two sources disagree on a term, the arbitration flow follows ARC-Core's dual-record discipline (flag the contradiction, preserve both, require receipt-based resolution).
- **Release integrity** — language data ships in governed snapshots; every snapshot is an ARC-Core-verifiable release artifact.
- **Evidence export** — language data exports use the same evidence-pack format ARC-Core defines.

### Where the boundary sits

- **ARC-Core owns**: provenance record shape, trust-rank doctrine, contradiction handling.
- **Language Module owns**: the canonical language graph, ingestion services, translation abstraction.

---

## 5. omnibinary-runtime

**OmniBinary's execution ledger is ARC-Core's receipt-first discipline applied to binaries.**

### What OmniBinary uses ARC-Core for

- **Receipts-first observability** — every binary operation (intake, classification, decode, dispatch, JIT, lane execution) produces a receipt **before** producing a result, mirroring ARC-Core's stance.
- **Runtime ledger** — the indexed binary mirror is an ARC-Core-shaped event log applied to binary state changes.
- **Execution lanes** — managed, native, and DBT lanes are each ARC-Core authority-gated: who may execute in which lane under what policy.
- **Cache integrity** — block-cache and translation-cache policies prioritize correctness (ARC-Core discipline) over raw throughput.

### Where the boundary sits

- **ARC-Core owns**: the receipt, the authority, the identity rules.
- **OmniBinary owns**: the binary intake pipeline, the JIT backends, the execution lanes, the cache policy, the personality contract.

---

## 6. Arc-RAR

**Arc-RAR's archives are ARC-Core-verifiable restoration bundles.**

### What Arc-RAR uses ARC-Core for

- **Manifest receipts** — every Arc-RAR bundle carries a manifest with SHA-256 identity that ARC-Core's receipt chain can verify.
- **Evidence-producing extraction** — extracting a bundle produces an ARC-Core-style receipt: what was extracted, where, by whom, with what authority.
- **Rollback semantics** — restoring from an Arc-RAR bundle is an event with its own receipt chain.
- **Cross-repo trust** — any system can verify an Arc-RAR bundle against the ARC-Core receipt chain without trusting Arc-RAR's tooling directly.

### Where the boundary sits

- **ARC-Core owns**: the receipt format, SHA-256 identity rules, evidence-export spec.
- **Arc-RAR owns**: the bundle format, CLI/FFI/IPC surfaces, native-app controls, rollback execution.

---

## The frozen-roles contract

The core rule across the whole ecosystem: **roles never swap**. ARC-Core's role is **authority over events and receipts**. Nothing else in the stack may claim that role.

- Cleanroom enforces deterministic execution, not event truth.
- Cognition Core owns the model-growth doctrine, not the receipt primitive.
- LLMBuilder assembles the governed build loop, not the authority layer.
- Language Module owns lexical truth, not the general authority contract.
- OmniBinary owns the binary substrate, not the event-identity rules.
- Arc-RAR owns archive bundles, not the receipt-chain verification logic.

If any new capability is proposed that would require a sibling to own ARC-Core semantics, the correct answer is to extend ARC-Core itself — not to duplicate the authority layer elsewhere.

---

## Integration direction

The full cross-repo integration is described in the [LLMBuilder roadmap v1.3.0 "Multi-Repo Integration" milestone](https://github.com/GareBear99/ARC-Neuron-LLMBuilder/blob/main/ROADMAP.md). Key milestones that involve ARC-Core directly:

- **Co-signed receipts** — LLMBuilder Gate v2 decisions co-signed with an ARC-Core signing key so external parties can verify a promotion happened inside a governed lab.
- **OmniBinary ↔ LLMBuilder federation** — OmniBinary subscribing to LLMBuilder's OBIN v2 events via the ARC-Core event bus.
- **Cleanroom kernel hosting** — LLMBuilder's canonical conversation pipeline running inside Cleanroom's kernel with ARC-Core receipts as the shared audit trail.
- **Language Module canonicalization** — LLMBuilder's terminology store syncing with the Language Module via ARC-Core provenance events.

---

## Sponsoring the ecosystem

All seven repositories share a single author and a single funding target:

- **GitHub Sponsors**: https://github.com/sponsors/GareBear99
- **Direct contribution**: open issues and PRs in whichever repo owns the change

Sponsorship funds hardening across all seven repos — ARC-Core governance, sibling integration contracts, and the production documentation.

---

## One-line summary

**Every receipt in the ARC ecosystem derives from the discipline defined in ARC-Core. Nothing in this stack is trustworthy without it.**
