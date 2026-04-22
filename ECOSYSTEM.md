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

## Consumer applications — ARC-Core beyond the governed-AI stack

ARC-Core is also the authority/receipt backbone for several **consumer applications, games, simulators, and commercial product backends** that are not part of the core seven-repo governed-AI ecosystem but depend on ARC-Core's discipline for the same reasons: event truth, receipt chains, and authority gating.

Each of the five consumer repos below now carries its own **🔐 Built on ARC-Core** section with a per-project pattern-mapping table, so the relationship is documented bidirectionally.

| Application | Repository |
|---|---|
| 🎮 Rift Ascent | [RiftAscent](https://github.com/GareBear99/RiftAscent) |
| 🌌 Seeded Universe Recreation Engine | [Seeded-Universe-Recreation-Engine](https://github.com/GareBear99/Seeded-Universe-Recreation-Engine) |
| 🎨 Proto-Synth Grid Engine | [Proto-Synth_Grid_Engine](https://github.com/GareBear99/Proto-Synth_Grid_Engine) |
| 🔭 Neo-VECTR Solar Sim | [Neo-VECTR_Solar_Sim_NASA_Standard](https://github.com/GareBear99/Neo-VECTR_Solar_Sim_NASA_Standard) |
| 🎵 TizWildin Entertainment Hub | [TizWildinEntertainmentHUB](https://github.com/GareBear99/TizWildinEntertainmentHUB) |
| 🏠 RAG Command Center | [RAG-Command-Center](https://github.com/GareBear99/RAG-Command-Center) |
| 🤖 Robotics Master Controller | [Robotics-Master-Controller](https://github.com/GareBear99/Robotics-Master-Controller) |
| 📈 BrokeBot (CEX funding-rate arb) | [BrokeBot](https://github.com/GareBear99/BrokeBot) |
| 📈 Charm (Uniswap v3 spot bot) | [Charm](https://github.com/GareBear99/Charm) |
| 📈 Harvest (multi-TF crypto platform) | [Harvest](https://github.com/GareBear99/Harvest) |
| 📈 One-Shot-Multi-Shot (binary options) | [One-Shot-Multi-Shot](https://github.com/GareBear99/One-Shot-Multi-Shot) |
| 📈 DecaGrid (capital-ladder grid docs) | [DecaGrid](https://github.com/GareBear99/DecaGrid) |
| 📈 EdgeStack_Currency (execution spec) | [EdgeStack_Currency](https://github.com/GareBear99/EdgeStack_Currency) |
| 💸 VALLIS Liquidity (traffic hub + router) | [VALLIS_Liquidity](https://github.com/GareBear99/VALLIS_Liquidity) |
| 💸 ADMENSION (ad monetization + liquidity pools) | [ADMENSION](https://github.com/GareBear99/ADMENSION) |

---

### 🎮 Rift Ascent

**A canvas-based action game with prestige cycles, upgrades, co-op, and procedural audio — coming to iOS and Android.**

#### What Rift Ascent uses ARC-Core for

- **Player-event ledger** — every move, kill, heat-gain, prestige cycle, and upgrade purchase becomes an ARC-Core-shaped event with a SHA-256 identity.
- **Co-op session receipts** — multiplayer sessions produce receipts for every shared state transition, so both clients converge on the same canonical event log.
- **Tamper-evident high-score chain** — leaderboard submissions are signed receipts. Any modification breaks the chain and is detected at verification time.
- **Deterministic replay** — any game session can be replayed by re-applying its event log through the canonical pipeline. Combat outcomes are reproducible.
- **Anti-cheat audit** — client-side actions that skip the receipt flow are rejected by the server. The receipt chain *is* the anti-cheat layer.

#### Where the boundary sits

- **ARC-Core owns**: the event shape, the signing-key contract, the receipt format, the authority-to-act checks.
- **Rift Ascent owns**: the gameplay, the rendering, the procedural audio, the prestige math, the upgrade trees.

---

### 🌌 Seeded Universe Recreation Engine

**A deterministic seed-based universe engine for recreating universes from a single seed with full provenance.**

#### What Seeded-Universe uses ARC-Core for

- **Seed receipts** — every universe-generation event carries a receipt identifying the seed, the generator version, the generation rules applied, and the SHA-256 of the resulting state.
- **Entity resolution for celestial objects** — stars, planets, moons, orbital systems, and galactic structures all flow through ARC-Core's entity-resolution pattern, so the same object has the same canonical identity across any recreation.
- **Deterministic simulation replay** — a universe can be regenerated bit-for-bit from its seed + event log, with every intermediate state addressable by event ID.
- **Authority over "this seed produced this universe"** — a signed receipt chain proves the generation is authentic and not tampered with.

#### Where the boundary sits

- **ARC-Core owns**: seed-receipt contract, entity identity rules, authority-chain verification.
- **Seeded-Universe owns**: the generation algorithm, the universe graph, the rendering, the navigation.

---

### 🎨 Proto-Synth Grid Engine

**An experimental 2D/3D low-weight system for structured grid-based cognition and visualization.**

#### What Proto-Synth uses ARC-Core for

- **Grid-event log** — every grid mutation (cell update, actor move, layer change) is an ARC-Core event with a receipt.
- **Entity tracking for grid actors** — persistent actors carry ARC-Core-style entity identity that survives save/load and network sync.
- **Deterministic state transitions** — grid state is derived by replaying events. The grid never mutates in place.
- **Authority-gated mutations** — who may modify which layer under what policy is decided by ARC-Core's authority primitive.
- **Persistence via receipt chain** — save files are event logs + final-state snapshots, verified by the receipt chain on load.

#### Where the boundary sits

- **ARC-Core owns**: event shape, entity identity, authority gating, receipt chain.
- **Proto-Synth owns**: the grid rendering, the actor behaviors, the layer system, the UI.

---

### 🔭 Neo-VECTR Solar Sim (NASA Standard)

**A low-weight 2D-engine (visually 3D) astronomy simulator that renders only proven celestial objects through a deterministic universe graph. Portable offline client with catalog-driven truth packs.**

#### What Neo-VECTR uses ARC-Core for

- **Truth-pack receipt chain** — every celestial object ships with a provenance receipt citing its NASA-standard source (catalog, identifier, observation run). Truth packs are ARC-Core-verifiable release artifacts.
- **Event-sourced navigation** — camera, zoom, pan, and scale-tier transitions are events. Any viewport state is reconstructable from its event log.
- **Authority over "proven"** — the NASA-standard qualifier is an authority claim backed by ARC-Core's proposal-evidence-receipt flow. Unverified objects are flagged, not silently rendered.
- **Deterministic universe-graph replay** — the universe graph itself is derived from the truth packs + event log. Two users with the same packs see the same universe bit-for-bit.
- **Offline verification** — because receipts are SHA-256-addressable, truth packs can be verified offline without contacting a server.

#### Where the boundary sits

- **ARC-Core owns**: the truth-pack receipt format, the authority-over-provenance contract, the event-sourcing pattern.
- **Neo-VECTR owns**: the catalog ingestion, the orbit math, the rendering, the scale-tier navigation.

---

### 🎵 TizWildin Entertainment Hub — entire plugin ecosystem

**The authority + orchestration backend for the TizWildin plugin ecosystem. FastAPI service managing entitlements, seats, Stripe billing, and GitHub release polling for 14 JUCE audio plugins.**

This is ARC-Core's largest commercial consumer. The TizWildin Hub was built directly on ARC-Core discipline and is the authority layer for a **live 14-plugin commercial ecosystem**.

#### What TizWildin Hub uses ARC-Core for (full surface)

- **Entitlement receipts** — every purchase produces a signed receipt linking a customer identity to a plugin license. Entitlements are ARC-Core events, not mutable rows.
- **Seat-assignment audit trail** — every seat activation, deactivation, and transfer is an event with its own receipt. Seat history is queryable by replaying the event log.
- **Stripe billing event log** — Stripe webhook events are ingested into the ARC-Core event chain. Billing disputes are resolved by replay, not by reconciling external state.
- **GitHub release-polling event chain** — new plugin releases are events. Customers' update-eligibility is derived by replaying the release chain against their entitlement chain.
- **Authority-gated activation** — the activation check is the same authority primitive ARC-Core uses for analyst actions: role, session, proof-of-purchase, machine fingerprint.
- **Support-case management** — support tickets are cases with attached events (purchase, activation attempts, error logs). The same case pattern ARC-Core pioneered.

#### The 14 JUCE plugins served by this Hub

The real plugin roster (as listed in the TizWildin Hub README):

- [FreeEQ8](https://github.com/GareBear99/FreeEQ8) — 8-band parametric EQ with dynamic EQ, linear-phase, match EQ, M/S, spectrum analyzer ✅ Production
- [PaintMask](https://github.com/GareBear99/PaintMask_Free-JUCE-Plugin) — visual paint-based audio processing; brush strokes become MIDI patterns ⚠️ Beta
- [WURP](https://github.com/GareBear99/WURP_Toxic-Motion-Engine_JUCE) — Toxic Motion Engine: formant motion, corrosive saturation, elastic pitch ✅ Production
- [AETHER](https://github.com/GareBear99/AETHER_Choir-Atmosphere-Designer) — choir & atmosphere designer: procedural choirs, pads, evolving textures ⚠️ Beta
- [WhisperGate](https://github.com/GareBear99/WhisperGate_Free-JUCE-Plugin) — procedural whispers and ritual atmospheres via interactive geometry ✅ Production
- [Therum](https://github.com/GareBear99/Therum_JUCE-Plugin) — bootleg Serum: free wavetable synth ✅ Production
- [Instrudio](https://github.com/GareBear99/Instrudio) — 10 fully playable instruments; cross-platform instrument ecosystem ⚠️ Beta
- [BassMaid](https://github.com/GareBear99/BassMaid) — bass enhancement and low-end processing ✅ Production
- [SpaceMaid](https://github.com/GareBear99/SpaceMaid) — spatial audio: depth, width, reverb ✅ Production
- [GlueMaid](https://github.com/GareBear99/GlueMaid) — mix-bus glue and cohesion ✅ Production
- [MixMaid](https://github.com/GareBear99/MixMaid) — spectral balance and mix correction ✅ Production
- [ChainMaid](https://github.com/GareBear99/ChainMaid) — sidechain ducking and pumping effects ✅ Production
- [RiftWave Suite](https://github.com/GareBear99/RiftWaveSuite_RiftSynth_WaveForm_Lite) — modular synth + waveform synthesis ⚠️ Beta
- [FreeSampler](https://github.com/GareBear99/FreeSampler_v0.3) — lightweight audio sampler plugin 🚧 Dev

Each plugin talks to the Hub over HTTPS, and every license check, update check, and activation attempt becomes an ARC-Core event in the Hub's backend.

#### Where the boundary sits

- **ARC-Core owns**: the receipt format, the entitlement-event shape, the authority-over-activation contract, the case-management pattern.
- **TizWildin Hub owns**: the Stripe integration, the FastAPI routes, the customer-facing UI, the plugin-specific activation logic, the GitHub release polling.
- **Individual plugins own**: their DSP, their UI, their JUCE bindings. They consume the Hub, which consumes ARC-Core.

---

### 📈 Trading fleet — six repos, one event spine

**Six public trading / execution-spec repos share a single ARC-Core-compatible doctrine: every market tick is an event, every order is a proposal, every fill is a receipt, every risk limit is an authority check, every backtest is a deterministic replay of the event log.**

Every fleet repo also publishes a live GitHub Pages docs site (served from `main` / `/docs`).

| Repo | Role | Docs site | Stack | ARC-Core mapping |
|---|---|---|---|---|
| [BrokeBot](https://github.com/GareBear99/BrokeBot) | CEX funding-rate arbitrage (small accounts, USDT-TRC20) | [garebear99.github.io/BrokeBot](https://garebear99.github.io/BrokeBot/) | Python, Binance Futures | Funding tick = event · entry decision = proposal · fill = receipt · risk-limit halt = authority refusal · kill switch = manual authority override |
| [Charm](https://github.com/GareBear99/Charm) | On-chain spot bot on Base (Uniswap v3, ≤$12 accounts) | [garebear99.github.io/Charm](https://garebear99.github.io/Charm/) | Node.js, ethers.js | Pool sample = event · mean-reversion trigger = proposal · swap tx = receipt · dedicated-wallet private key = scoped `auth_user` · per-session cap = authority limit |
| [Harvest](https://github.com/GareBear99/Harvest) | Multi-timeframe crypto research platform with grid-search | [garebear99.github.io/Harvest](https://garebear99.github.io/Harvest/) | Python, Web3 | OHLCV ingest = events · strategy selection = proposal w/ evidence · backtest = deterministic replay · data-freshness gate = authority refusal · MetaMask session = scoped auth |
| [One-Shot-Multi-Shot](https://github.com/GareBear99/One-Shot-Multi-Shot) | Binary-options engine with 3-hearts risk lifecycle | [garebear99.github.io/One-Shot-Multi-Shot](https://garebear99.github.io/One-Shot-Multi-Shot/) | JS / HTML5, MetaMask | Prediction tick = event · trade gate = proposal · outcome = receipt · heart depletion = authority halt · daily cap = authority ceiling |
| [DecaGrid](https://github.com/GareBear99/DecaGrid) | Capital-ladder grid docs pack (whitepaper, runbook, DecaScore) | [garebear99.github.io/DecaGrid](https://garebear99.github.io/DecaGrid/) | Static HTML / PDF | DecaScore tier = authority stratum · ladder rung = sizing authority · runbook clause = authority contract · records page = receipt-chain spec |
| [EdgeStack_Currency](https://github.com/GareBear99/EdgeStack_Currency) | Canonical event-sourced multi-currency execution spec | [garebear99.github.io/EdgeStack_Currency](https://garebear99.github.io/EdgeStack_Currency/) | Plain-prose spec | Immutable event ledger = ARC-Core event log · `FILL_PARTIAL` / `FX_CONVERSION` / `FEE` = receipts · `RECONCILIATION_CORRECTION` = authority-gated dual-record event |

#### Where the boundary sits

- **ARC-Core owns**: the event shape, the authority-gating primitive, the receipt chain, deterministic replay, the reconciliation contract.
- **Each bot owns**: its venue adapter, its signal logic, its risk math, its UI. When wired to ARC-Core, decisions become receipts and the spine becomes the auditable journal.
- **DecaGrid** owns the *policy* (how the ladder ought to escalate), [BrokeBot / Charm / Harvest / One-Shot-Multi-Shot] own the *actuator* (what orders to send), and **EdgeStack_Currency** owns the *ledger shape* (how state must move between accounts / venues / currencies). ARC-Core owns the *truth of what happened*.

---

### 💸 Liquidity & monetization infrastructure — VALLIS ecosystem backend

**VALLIS_Liquidity is the traffic hub + router that fronts the VALLIS ecosystem. ADMENSION is the ad-monetization + liquidity-pool application it hosts. Together they form a two-layer stack: VALLIS_Liquidity owns attribution + routing, ADMENSION owns monetization + pools. ARC-Core owns the event truth underneath both.**

#### What VALLIS_Liquidity uses ARC-Core for

- **Hub event log** — every `hub_hit` at the root domain and every `hub_redirect` to a subsystem (`/ADMENSION/`, `/VALLIS/`) is an ARC-Core event with SHA-256 identity.
- **Attribution discipline** — `utm_*`, `referrer`, `adm`, `s`, `seed` params are captured into event provenance (ARC-Core's entity-identity + evidence pattern) and preserved across redirects so downstream systems can attribute revenue share correctly.
- **Routing as proposal + evidence** — the router's decision between ADMENSION vs VALLIS, `auto=1` vs hub UI, is a proposal whose evidence is the captured params and whose receipt is the final redirect.
- **Collector federation** — the optional `ADMENSION_COLLECTOR_URL` shape lets both the hub and ADMENSION emit into the same event collector. ARC-Core normalizes that into a single receipt chain.

#### What ADMENSION uses ARC-Core for

- **Ad-placement event catalog** — 154 placements become a typed event catalog; every impression, click, and contribution is an ARC-Core event.
- **Revenue-share as proposal → evidence → receipt** — contribution calculations, pool deposits, and payouts flow through ARC-Core's canonical proposal/authority/receipt discipline instead of being implicit ledger updates.
- **SENTINEL safety = authority gating** — SENTINEL's policy checks map onto ARC-Core's authority primitive: refuse-then-log instead of log-then-maybe-refuse.
- **SCAR continuity = receipt chain** — SCAR's continuity semantics are ARC-Core's tamper-evident receipt chain by another name.
- **5 liquidity pools + Anunnaki Vault** — pool state is an authority-gated entity in ARC-Core terms; every rebalance is a receipted event.
- **EVE AI chatbot** — each user-visible interaction is an event with provenance, so support and dispute replay is possible.
- **Smart-contract calls** — on-chain transactions become ARC-Core receipts with a second, on-chain proof; the two chains co-sign the same history.

#### Where the boundary sits

- **ARC-Core owns**: event identity, authority primitive, receipt chain, attribution provenance, deterministic replay.
- **VALLIS_Liquidity owns**: the traffic-hub UX, the redirect logic, the param-capture behavior, the `ads.txt` surface.
- **ADMENSION owns**: the ad-placement taxonomy, the revenue-share math, the pool curves, the smart-contract surface, the EVE chatbot, the SENTINEL / SCAR implementations.
- **Relationship**: VALLIS_Liquidity is the backend-of-the-backend (traffic → attribution → route); ADMENSION is the application it hosts; ARC-Core is the receipt-chain both emit into. Neither VALLIS_Liquidity nor ADMENSION owns "the truth" — they own their domain; ARC-Core owns the record.

---

## 🔮 Future development plans — ARC-Core roadmap

These four repos are **research-grade scaffolds** positioned to become ARC-Core's next production integrations. Each one extends the kernel's five primitives (event / entity / edge / proposal / receipt) into a new surface. None of them are in production today; the doctrine and the repos both exist.

### 1. ARC-Turbo-OS — deterministic execution runtime (2×–100× OS speed-ups)

**Repo**: [ARC-Turbo-OS](https://github.com/GareBear99/ARC-Turbo-OS)

**Vision**: Turn every OS task into a **canonical problem graph**, cache resolved outputs by their canonical identity, and reuse them on subsequent runs. Potentially 2× to 100+× faster OS-level execution for workloads with any repeatable structure.

**What ARC-Core will provide**
- **Canonical-graph events** — the hash of a problem graph *is* ARC-Core's event identity. Two identical problem graphs in different runs share one event.
- **Resolved-output reuse = receipt reuse** — cached outputs become receipts addressable by `state_at(event_id)`. A Turbo OS run is either "here's a fresh receipt" or "here's the receipt I produced last time, verifiable against the chain".
- **Authority-gated dispatch** — which execution lane runs a task (native, JIT, sandboxed) is an authority decision with an audit trail.
- **Externally-verifiable speedups** — because every cached answer is a receipt, Turbo OS's speed claims can be verified from outside the runtime without trusting Turbo OS itself.

**Where the boundary sits**
- **ARC-Core owns**: event identity, receipt chain, authority primitive, deterministic replay contract.
- **ARC-Turbo-OS owns**: the canonical-graph transformer, the resolved-output cache, the dispatch lanes, the OS-level integration.

---

### 2. Proto-AGI — persistent, memory-backed, tool-using loop

**Repo**: [Proto-AGI](https://github.com/GareBear99/Proto-AGI)

**Vision**: A practical architecture for moving from a local assistant/controller toward a **persistent, memory-backed, tool-using proto-AGI loop** — the bridge between a stateless chatbot and a governed long-running agent.

**What ARC-Core will provide**
- **Persistent memory = event log** — the agent's memory is an ARC-Core append-only event log. Memory never mutates in place; it accumulates.
- **Tool calls = proposals** — every tool invocation carries arguments, an authority claim, and enters the proposal pipeline before it executes.
- **Tool returns = receipts** — every return value is a receipt linked back to its proposal. Failure modes are receipts too.
- **Session replay** — any session can be reconstructed by replaying its slice of the event log, with authority pinned to the originating session's role.
- **No forged history** — because the chain is tamper-evident, the agent cannot rewrite its own past to escape a governance decision.

**Where the boundary sits**
- **ARC-Core owns**: event log, receipt shape, authority primitive, replay semantics.
- **Proto-AGI owns**: the reasoning loop, the tool registry, the memory retrieval policy, the action selection logic.

---

### 3. AGI_Photon-Quantum-Computing — Photon AGI thinking core + SSOT bot lab

**Repo**: [AGI_Photon-Quantum-Computing](https://github.com/GareBear99/AGI_Photon-Quantum-Computing)

**Vision**: Production dossier for a **Photon AGI thinking core** paired with a **SSOT (single source of truth) bot lab** that produces candidate cognition modules and promotes them under governance.

**What ARC-Core will provide**
- **SSOT is the ARC-Core primitive** — the entire kernel is built around "one canonical record, receipt-verified". Photon's SSOT requirement maps onto ARC-Core directly.
- **Thinking steps = events** — each step of photon-flavoured cognition is an event with a SHA-256 identity.
- **Candidate promotion = Gate-v2 flow** — promoting a thinking-core candidate follows the same proposal / evidence / receipt discipline LLMBuilder's Gate v2 uses today, extended to the photon lane.
- **Benchmark receipts** — every experiment in the bot lab emits a receipt: inputs, outputs, scoring, canonical identity, authority. Benchmarks are replayable by construction.

**Where the boundary sits**
- **ARC-Core owns**: SSOT primitive, receipt chain, authority contract, event identity rules.
- **AGI_Photon-Quantum-Computing owns**: the photon cognition model, the thinking-core architecture, the bot-lab harness, the scorers, the promotion doctrine.

---

### 4. A-real-time-spatial-signal-intelligence-engine — geospatial signal intelligence

**Repo**: [A-real-time-spatial-signal-intelligence-engine](https://github.com/GareBear99/A-real-time-spatial-signal-intelligence-engine)

**Vision**: Google Earth + WiFi / RF analysis + device tracking + physics simulation + satellite imagery, fused into a single real-time spatial intelligence surface. This is the natural upgrade path for ARC-Core's existing geospatial primitives.

**What ARC-Core will provide (today's kernel already has most of this)**
- **Geo-tagged events** — every RF / WiFi / satellite reading is an event with a position, timestamp, and provenance. ARC-Core's geospatial layer already handles structures / sensors / geofences / blueprints / calibration / tracks / incidents.
- **Device identity over time** — a moving device becomes an ARC-Core entity; its track is a sequence of events with a stable identity.
- **Geofence triggers = authority gates** — entering / exiting a zone of interest is an authority event. Incidents are first-class receipt-producing entities.
- **Physics-sim replay** — propagating signals through terrain / atmosphere is a deterministic replay of the event stream through a solver. If the inputs replay, the outputs must replay.
- **Evidence export** — any investigation can export a portable, receipt-verifiable evidence pack covering a geographic + temporal window.

**Where the boundary sits**
- **ARC-Core owns**: the geospatial primitive set, entity identity, receipt chain, evidence-pack format.
- **A-real-time-spatial-signal-intelligence-engine owns**: the RF / WiFi analyzers, the satellite ingestion pipeline, the physics solver, the Google-Earth-grade visualization, the device-tracking correlator.

---

### Status and cadence

These four repos are **explicitly roadmap**, not production. Each one will move into the core 7+15 picture in order once its ARC-Core integration lands:
- Turbo OS moves first because OS-level speedups unblock every other surface.
- Proto-AGI moves second because a persistent memory-backed loop is the substrate several other repos will depend on.
- Photon + SSOT moves third (large-model-family compatible).
- Spatial signal intelligence moves fourth because today's kernel already covers ~70% of its doctrine requirements; it needs integration work, not invention.

---

## The consumer-application rule

Consumer applications can use ARC-Core's discipline without being part of the governed-AI ecosystem. The rule is the same in both directions:

- **ARC-Core provides**: authority, events, receipts, SHA-256 identity, evidence export.
- **Consumer owns**: the domain logic (game rules, simulation physics, plugin DSP, billing logic, UI).

ARC-Core does not try to render anything, simulate anything, synthesize audio, run a physics engine, process payments, or know what a "celestial object" is. It knows what an **event** is, what a **receipt** is, and what **authority** means. That's enough to serve both a governed-AI lab and a commercial plugin ecosystem.

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
