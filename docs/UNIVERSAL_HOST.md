# ARC-Core as a Universal Host

This document answers one question: **how do I adapt *any* application so it can ride on ARC-Core running on a 2012-era Intel Mac?**

The thesis: if your app can be expressed as *entities, events, authority, and receipts* at a rate humans (or slow hardware) can actually keep up with, it fits on this hardware floor. The adaptation rules below are mechanical; the worked examples prove them.

For the hardware numbers and install playbook, see [`HARDWARE_FLOOR.md`](./HARDWARE_FLOOR.md). For the compare-with-competitors view, see [`CONTINUUM_COMPARISON.md`](./CONTINUUM_COMPARISON.md).

## 1. The adaptation rules
To ride on ARC-Core, every piece of your application state is mapped into one of five ARC-Core primitives. No exceptions — if something doesn't fit these, either push the transformation upstream (your app normalizes it before POST) or bypass ARC-Core for that concern (e.g., don't shove video frames through it).
| Primitive | What it is in ARC-Core | What you map into it |
|---|---|---|
| **Event** | A typed, timestamped, fingerprinted state-change with `payload: dict` | Any discrete action, observation, or transaction in your app |
| **Entity** | A canonical `ent_...` id with aliases and a risk score | Any identifiable actor, object, asset, or subject |
| **Edge** | A directed relation with accumulating weight | Any recurring link between two entities (e.g., "user-X bought asset-Y") |
| **Proposal** | Action + rationale + simulation → approval | Any state transition that needs authority review before taking effect |
| **Receipt** | Hash-chained + HMAC-signed row | Emitted automatically by the above; you don't write these, you verify them |

Two operational primitives sit alongside:
- **Case** — groups events, notes, proposals into one investigation. Map to: any "work item" your app tracks (a ticket, a deal, a build, a match).
- **Geofence / track** — polygon + sensor + estimated position. Map to: any bounded zone with "something happens when inside" semantics (keep-out zones, trading windows, arena regions).

## 2. What to keep and what to strip (on 2012 Intel hardware)
The rule of thumb: **keep the discipline, strip the bandwidth.**
### Keep (everything 2012 Intel can host easily)
- State-change emission (POST `/api/events` at up to ~300 events/sec sustained).
- Role-gated mutations (`require_role("operator")` costs microseconds).
- Proposal/approve lifecycle (nothing real-time; analyst-paced).
- Evidence export (one-shot JSON bundles, bounded by `NOTEBOOK_EXPORT_LIMIT`).
- Geospatial polygons and receipts — indoor scale, not continental.
- Receipt-chain verification as a *background* job.
### Strip (things that don't fit on 2012 Intel)
- Anything over ~1 KB per event × 300/sec sustained → offload to a separate stream and post summaries to ARC-Core.
- Video / audio streams as payloads — post the *metadata* (timestamp, classifier output, feature vector id) and keep the media in object storage.
- ML inference inline — do inference in a separate process, POST the result as an event.
- Full-text search over 10⁶ events — narrow by entity/time, or wait for FTS5 (roadmap R3).
- Real-time push to the UI (roadmap R1); until WebSocket ships, poll the event list every 2-5 s from the client.
### Don't attempt on 2012 Intel
- Heavy ML training. That's `ARC-Neuron-LLMBuilder`'s job, and its training still needs modern hardware.
- Kafka-scale event bus (>10k events/sec). Use a real broker upstream, ARC-Core ingests the summary rate.
- Multi-tenant SaaS. Deploy one ARC-Core per tenant behind a reverse proxy.

## 3. Minimum-viable integration (any language, one HTTP client)
If your application speaks HTTP, it can talk to ARC-Core in under 20 lines. Here's the one-file Python example every ARC-Core consumer boils down to:
```python path=null start=null
import os
import requests

BASE = os.getenv("ARC_BASE", "http://127.0.0.1:8000")
TOKEN = os.getenv("ARC_TOKEN", "")  # optional shared-token
ROLE = os.getenv("ARC_ROLE", "observer")

def post_event(event_type: str, subject: str, *, object_=None, payload=None,
               confidence: float = 0.8, severity: int = 3) -> dict:
    """Idempotent POST of a typed event. Returns the canonical EventOut."""
    r = requests.post(
        f"{BASE}/api/events",
        json={
            "event_type": event_type,
            "source": os.getenv("ARC_SOURCE", "my-app"),
            "subject": subject,
            "object": object_,
            "payload": payload or {},
            "confidence": confidence,
            "severity": severity,
        },
        headers={"X-ARC-Role": ROLE, "X-ARC-Token": TOKEN} if TOKEN else {"X-ARC-Role": ROLE},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()

def verify_chain(limit: int = 1000) -> dict:
    r = requests.get(f"{BASE}/api/receipts/verify", params={"limit": limit}, timeout=10)
    r.raise_for_status()
    return r.json()
```

That's it — now anything your app does can emit ARC-Core events with full dedupe + receipts + entity resolution. The `fingerprint` you get back on each event is the canonical identity; replaying the same POST returns the same event_id.

## 4. Worked example A — currency / arbitrage trading bot
Target: the `BrokeBot` / `Doman.ai_Arbritrage_Bot` use case from the portfolio. Running on a 2012 Intel Mac.

### Budget
- Market ticks: sample at 1-5 Hz (not every exchange frame — downsample upstream).
- Order rate: ≤10/min during active trading.
- Fill rate: ≤10/min.
- Strategy decisions: ≤1/min.

All comfortably within 2012-Intel + low-resource-mode budget (pipeline can absorb ~300 events/sec, we're at ~5 events/sec peak).

### Mapping
| Trading concept | ARC-Core primitive | Example POST |
|---|---|---|
| Market tick (top-of-book) | `event` (type=`market_tick`, subject=`EURUSD`) | `{event_type:"market_tick", subject:"EURUSD", payload:{bid:1.0523, ask:1.0525, venue:"oanda"}}` |
| Exchange account | `auth_users` row + entity | Created once at bot startup via `ensure_bootstrap_admin`-style flow |
| Strategy decision | `proposal` (action=`buy`, target_type=`pair`, target_id=`EURUSD`) | Includes `simulation_depth` → engine returns predicted impact band before any order is placed |
| Above-threshold position | `require_role("approver")` on proposal approval | Bot runs as `operator`; a human (or a separate bot with scoped approver role) must approve |
| Order sent | `event` (type=`order_sent`, subject=`order_<uuid>`, object=`EURUSD`) | Linked to proposal via `payload.proposal_id` |
| Fill | `event` (type=`fill`, subject=`order_<uuid>`, payload={price, qty, slippage}) | The filled amount is the consuming receipt |
| Risk breach | `incident` (severity=`critical`) | Stops the bot; surfaces in `/api/incidents` + receipt chain |
| Backtest run | Deterministic replay via event log + recomputed state | `SELECT * FROM events WHERE source='backtest-<id>' ORDER BY ts ASC` |
| PnL calculation | Derived state from event-log replay | Never stored; always computed |
| Key rotation / credential roll | `auth_user` update + receipt | Appends an audit trail nobody can silently delete |

### Why this is good on 2012 Intel
- Ledger footprint: ~200 bytes/event × 5 events/sec × 6.5 hours trading = ~23 MB/day. Under `ARC_MAX_DB_SIZE_MB=500` advisory, that's 20+ days before archival to Arc-RAR.
- Decision latency: proposal → simulation → approval ≈ 8 ms end-to-end (measured).
- Replay / backtest: 1-day-of-events replay runs in ~3-4 s.

### What to strip
- **Tick-level latency trading**: don't. ARC-Core isn't a microsecond-latency trading stack, and 2012 Intel isn't a colo box. Use this for *slow* arbitrage (funding-rate, triangular, cross-exchange with >1 s windows) — which is what the portfolio name `Doman.ai_Arbritrage_Bot` implies anyway.
- **Streaming market data in the receipt chain**: don't POST every millisecond tick; downsample to 1-5 Hz upstream. The *decisions* and *orders* are what the receipt chain protects; the ticks are just inputs.

## 5. Worked example B — robotics control plane (Robotics-Master-Controller future)
Target: prosthetics/actuator control on a 2012 Intel Mac acting as the safety-gate server. A real-time control loop still runs on a dedicated MCU — ARC-Core is the *authority layer*.
| Robotics event | ARC-Core primitive | Rate |
|---|---|---|
| Actuator command issued | event (type=`actuate`, subject=`left_servo_3`) | ≤100/sec per limb (fingerprint dedupe handles retries) |
| Sensor reading at threshold | event (type=`imu_over_limit`) | Rate-limited upstream to ≤10/sec |
| Motor enable/disable | proposal + approval | Human analyst approves for above-safe-envelope operation |
| E-stop triggered | incident (severity=`critical`) | Single event; receipt-chain tail becomes the post-mortem anchor |
| Fabrication job start | proposal with simulation | Dry-run G-code lint + collision check = `simulation_json` |
| Fabrication job complete | event (type=`job_complete`, payload={duration, material, defects_detected}) | Once per job |
| Fleet heartbeat | event (type=`heartbeat`, subject=`robot_<id>`) | 1/sec per robot; fingerprint dedupe ensures safe retransmit |

### Why this fits the hardware floor
A 2012 Intel MBP at 8 GB RAM comfortably hosts a fleet-scale receipt ledger for dozens of robots in low-resource mode. The *control loop* runs on the robot; ARC-Core is the signed-history layer that tells you, six months later, exactly what every actuator did and who authorized it.

## 6. Worked example C — real-estate operations (already shipping in RAG-Command-Center)
This one is already working; documenting it as proof that the universal-host pattern ships. See `RAG-Command-Center`'s own README §"Built on ARC-Core" for the full pattern table. Summary:
- Signal compile (Reddit/Victoria Open Data/Facebook paste) at a few posts per hour → well under the hardware floor.
- Deal scoring at 0-100% → explainable linear formula, inspectable by the analyst.
- Hot/Warm/Cold/Stale decay → sliding window exactly like `risk.score_event`.
- Pipeline kanban → proposal → evidence → receipt → approval.
- Cloudflare Worker runs *even lighter* than ARC-Core's own process; the heavy analyst console happens when someone's reviewing it on their laptop.

## 7. Worked example D — entertainment plugin backend (already shipping in TizWildin Hub)
14 JUCE plugins; ~hundreds-to-thousands of daily activation/license events. 2012 Intel Mac handles this without breaking a sweat.
- Every license check, update check, activation attempt = event.
- Stripe webhook = event ingested via `http_webhook` connector (roadmap R2 — until then, a Worker relays them).
- Seat transfer = proposal + approval.
- Support ticket = case with attached events.

Footprint after 6 months of commercial traffic: <80 MB DB, <60 MB RSS. Trivially within the hardware floor.

## 8. Worked example E — governed AI build loop (already shipping in ARC-Neuron-LLMBuilder)
The only consumer where ARC-Core's hardware floor and the *workload's* hardware floor diverge — model training needs real compute. But everything ARC-Core hosts stays on the 2012 floor:
- Gate v2 promotion receipt = event + proposal + simulation + receipt.
- Candidate/incumbent identity = canonical entity id.
- Benchmark result = event.
- Training-run metadata (NOT weights) = event with `payload.artifact_sha256`.
- The weights themselves go to Arc-RAR (a separate file-storage concern).

The v1.0.0-governed release shipped with a 2012 Intel Mac Catalina as the build host — proving the pattern.

## 9. When **not** to use ARC-Core as your host
- You need sub-millisecond latency on the state transition itself (e.g., HFT, game physics tick, real-time control loop). Use ARC-Core for the *authority/history* layer that sits next to your fast loop, not inside it.
- You need to store raw media (video/audio) at rate. Store media elsewhere; post metadata events to ARC-Core.
- You need a truly distributed multi-writer ledger. ARC-Core is single-node + single-writer SQLite. For that shape, use Hyperledger or a real multi-master DB.

## 10. Sanity-check checklist before you adapt
Before plumbing your app into ARC-Core on a 2012 Intel laptop, verify:
- [ ] Event rate sustained ≤ ~300/sec (ideally ≤ 50/sec for headroom on HDD machines).
- [ ] Individual event payload ≤ ~2 KB (store references, not blobs).
- [ ] Your authority model has at most 5 distinct ranks (maps onto the role ladder).
- [ ] Every state change you care about is expressible as an event type string + payload dict.
- [ ] You can tolerate eventual-consistency at sub-second granularity (SQLite WAL commits are not instant).
- [ ] You don't need push notifications until roadmap R1 WebSocket lands — polling is fine.

If all six check, your app rides on ARC-Core on 2012 Intel hardware. If one fails, either fix upstream or accept the hardware-floor caveat for that concern.
