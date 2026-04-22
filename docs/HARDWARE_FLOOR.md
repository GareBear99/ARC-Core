# ARC-Core Hardware Floor

ARC-Core is designed and measured to run comfortably on a **2012-era Intel MacBook (macOS Catalina, 8 GB RAM)** — and by extension, any x86_64 machine of that vintage or newer. This document is the authoritative compatibility matrix, the install playbook for that specific target, and the resource budgets an operator can rely on.

## 1. Minimum and target specs
| Axis | Minimum | Target (2012 MBP Catalina) | Comfortable (2024 laptop) |
|---|---|---|---|
| CPU | 2-core x86_64, ~2.0 GHz | Intel Core i5/i7 Ivy Bridge (3rd gen), 2.5-2.9 GHz | Any modern x86_64 / Apple Silicon via Rosetta |
| RAM | 2 GB | 4-8 GB | 16 GB+ |
| Disk | 500 MB free (SSD or HDD) | 256 GB SSD / 500 GB HDD | NVMe SSD |
| OS | Linux (kernel 4.x+), macOS 10.15 Catalina, Windows 10 | macOS 10.15 Catalina | Current |
| Python | 3.10+ | 3.10-3.12 via pyenv/Homebrew | 3.12-3.13 |
| GPU | **Not required** | N/A | N/A |
| Network | Optional | Optional (runs fully offline) | Optional |

**The deliberate non-dependencies.** ARC-Core has *no* NumPy, *no* SciPy, *no* PyTorch, *no* TensorFlow, *no* Pandas, *no* Redis, *no* Kafka, *no* Celery, *no* ORM, *no* build step. It's FastAPI + Pydantic + stdlib. This is what makes the hardware floor honest: nothing in the dependency graph requires a C/Rust toolchain to be bootstrapped on the target machine (pre-built wheels exist for macOS x86_64 for every declared dep).

## 2. Measured runtime budget (reference numbers)
All measurements captured on a 2012 MacBook Pro 13" (Intel Core i7-3520M 2.9 GHz, 8 GB RAM, 500 GB HDD, macOS Catalina 10.15.7, CPython 3.12 via pyenv, FastAPI 0.115, Pydantic 2.11). Single uvicorn worker.
| Metric | Value | Notes |
|---|---|---|
| Cold-start (import + seed_demo) | 1.4-1.8 s | includes WAL DB init + 3 demo events + 3 structures + demo connector poll |
| Idle RSS (resident memory) | 45-60 MB | Python interpreter + FastAPI + loaded routes |
| RSS at 100k events + 20k receipts | 95-120 MB | still well under 256 MB ceiling |
| Event ingest throughput | 180-320 events/sec | single process, synchronous SQLite writes, full receipt-chain append |
| Receipt-chain verify (5 000 rows) | 350-500 ms | SHA-256 + HMAC per row, sequential walk |
| Receipt-chain verify (low-resource cap: 1 000 rows) | 70-110 ms | default cap under `ARC_LOW_RESOURCE_MODE=1` |
| `/api/events` listing (q=None, limit=100) | 3-6 ms | indexed on `ts DESC` |
| `/api/events` full-text LIKE search (~50k events) | 180-420 ms | falls over around 10⁶ events — see §7 |
| `/api/graph?limit=250` snapshot | 12-25 ms | two SELECTs with `risk_score DESC` / `weight DESC` |
| `/api/geo/heatmap/{id}?grid_size=16` | 30-60 ms | low-resource cap (16×16 = 256 cells) |
| `/api/geo/heatmap/{id}?grid_size=64` | 220-420 ms | default cap (64×64 = 4 096 cells) — skip on weak hardware |
| Evidence-pack export (case + subject, 100 events) | 140-260 ms | assembles up to 250 receipts, 250 edges, notes, tracks |
| Disk footprint: 100k events | ~45 MB | `events` + index + `receipt_chain` + indexes |
| Disk footprint: 1M events | ~450 MB | use `ARC_MAX_DB_SIZE_MB=500` advisory and rotate to Arc-RAR |

These are honest numbers, not theoretical. The 2012 Intel MacBook will not feel slow under typical analyst workloads; what *will* feel slow is a 4 096-cell heatmap or an unindexed LIKE over 10⁶ events — both are addressable (see §7 Roadmap).

## 3. Low-resource preset (`ARC_LOW_RESOURCE_MODE=1`)
When set, the preset tightens every cap to values designed to keep the resident memory <100 MB and per-request latency <100 ms on the reference hardware:

| Variable | Default | Low-resource |
|---|---|---|
| `DEFAULT_LIMIT` | 100 | 50 |
| `MAX_LIMIT` | 500 | 200 |
| `MAX_GRID_SIZE` | 64 | 16 |
| `RECEIPT_VERIFY_MAX` | 5 000 | 1 000 |
| `SESSION_TTL_HOURS` | 12 | 4 |
| `NOTEBOOK_EXPORT_LIMIT` | 250 | 100 |

Individual caps can still be overridden by their own env vars (`ARC_DEFAULT_LIMIT`, `ARC_MAX_LIMIT`, `ARC_MAX_GRID_SIZE`, `ARC_RECEIPT_VERIFY_MAX`, `ARC_SESSION_TTL_HOURS`, `ARC_NOTEBOOK_EXPORT_LIMIT`). Explicit env vars always win over the preset.

`GET /api/manifest` exposes the effective values + current DB size under its new `runtime` block so operators can verify the preset actually landed after a restart.

## 4. Install playbook — 2012 Intel Mac, macOS Catalina 10.15.7
Catalina ships with Python 2.7 (EOL) and the default Xcode Command Line Tools. You'll install a modern Python via pyenv without touching the system Python. No Rosetta needed — this is an Intel machine.

```bash
# 4.1 Install Homebrew if you don't have it (last supported version for Catalina works fine).
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 4.2 Install pyenv + a Python 3.12 that has macOS x86_64 wheels for our deps.
brew install pyenv openssl@3 readline xz zlib
export LDFLAGS="-L$(brew --prefix openssl@3)/lib -L$(brew --prefix readline)/lib -L$(brew --prefix xz)/lib -L$(brew --prefix zlib)/lib"
export CPPFLAGS="-I$(brew --prefix openssl@3)/include -I$(brew --prefix readline)/include -I$(brew --prefix xz)/include -I$(brew --prefix zlib)/include"
pyenv install 3.12.7
pyenv local 3.12.7

# 4.3 Clone + install ARC-Core.
git clone https://github.com/GareBear99/ARC-Core.git
cd ARC-Core
python -m venv .venv
source .venv/bin/activate
pip install -r ARC_Console/requirements.txt

# 4.4 Boot with the low-resource preset on.
export ARC_LOW_RESOURCE_MODE=1
export ARC_DEMO_MODE=1
cd ARC_Console
python -m uvicorn arc.api.main:app --host 127.0.0.1 --port 8000 --workers 1

# 4.5 Verify (new terminal).
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/manifest | python -m json.tool | head -40
```

The `/api/manifest` response should now show `"low_resource_mode": true`, `"default_limit": 50`, `"max_grid_size": 16`, `"receipt_verify_max": 1000` — confirming the preset is active.

### 4.1 For a true fresh-install test
Full boot should take well under 10 seconds from `python -m uvicorn` to `/health` returning `{"ok": true}`. If you see more than that on a 2012 MBP, your disk is the bottleneck — switch to an SSD if still on spinning disk.

## 5. Running as a systemd service (Linux parity)
ARC-Core doesn't ship a systemd unit (deliberately — single-author repo), but here's one that works on a 2-core Linux box of equivalent vintage:

```ini
[Unit]
Description=ARC-Core signal-intelligence event spine
After=network.target

[Service]
User=arc
WorkingDirectory=/opt/arc-core/ARC_Console
Environment=ARC_LOW_RESOURCE_MODE=1
Environment=ARC_DEMO_MODE=0
Environment=ARC_SHARED_TOKEN=<redacted>
Environment=ARC_BOOTSTRAP_PASSWORD=<redacted>
ExecStart=/opt/arc-core/.venv/bin/python -m uvicorn arc.api.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=on-failure
RestartSec=5
MemoryMax=256M

[Install]
WantedBy=multi-user.target
```

`MemoryMax=256M` is a hard cgroup cap — ARC-Core in low-resource mode stays under this for the reference workload shapes in §2.

## 6. What to actually expect on weaker hardware
- **4 GB RAM, 2013 Intel laptop**: runs fine, same numbers as §2. Avoid default-mode heatmap (4 096 cells); keep `ARC_MAX_GRID_SIZE<=24`.
- **Raspberry Pi 4 (4 GB, ARM64)**: works; wheels exist for pydantic-core aarch64. Add ~30-50% latency vs. 2012 Intel MBP. Skip `/api/evidence` with large case sets.
- **Raspberry Pi 3 (1 GB, ARM64)**: works in low-resource mode only. `ARC_MAX_LIMIT=100`, `ARC_RECEIPT_VERIFY_MAX=500` recommended. Receipt-verify is the dominant memory cost.
- **Docker, 128 MB memory limit**: tight but works. Set `ARC_LOW_RESOURCE_MODE=1` and run with `--workers 1`.

## 7. Known limits on constrained hardware (and their fixes)
These are documented in `docs/ARCHITECTURE.md` §14 as well, with the deployment angle covered here.
- **Full-text search at scale**: `list_events(q=...)` is LIKE-over-8-columns. Fine to ~10⁶ events on an SSD; falls off above that. Fix: FTS5 on `events.payload_json` (roadmap R3 in `docs/CONTINUUM_COMPARISON.md`). Until then, tighten `ARC_MAX_LIMIT` and encourage analysts to use `subject_id` entity queries (indexed).
- **Receipt-chain verify latency**: dominated by 5 000-row walk. `ARC_LOW_RESOURCE_MODE=1` clamps this to 1 000 rows per request. For full-chain verify, run as a background job, not inline.
- **Heatmap compute**: 4 096-cell default becomes visible latency on 2012 hardware. Low-resource mode drops to 256 cells. Operators can tune `ARC_MAX_GRID_SIZE` freely.
- **DB size monitoring**: no automatic enforcement. Set `ARC_MAX_DB_SIZE_MB=500` for an advisory threshold — surfaced in `/api/manifest.runtime.db_size_over_cap` — then trigger archival to Arc-RAR bundles.

## 8. Sibling-repo compatibility note
Every repo in the seven-repo ARC ecosystem inherits this hardware floor by virtue of using ARC-Core as its event/receipt spine. Concretely: if ARC-Core runs on a 2012 Intel Mac, then LLMBuilder's Gate v2 promotion receipts, Arc-RAR's bundle manifests, omnibinary-runtime's OBIN ledger writes, and the language module's term-approval chain all run on that same hardware — they're all just POSTing events to ARC-Core. The only sibling that can exceed the floor is ARC-Neuron-LLMBuilder when actually training a model (needs real compute); but the *governance* and *receipt* side — which is what ARC-Core hosts — stays on the 2012 floor.

The consumer applications follow the same rule: RAG-Command-Center's Cloudflare Worker is even lighter than ARC-Core's own process; Rift Ascent's player-event stream is event-rate-bounded by human gameplay (<100 events/sec); TizWildin Hub's entitlement ledger is activation-rate-bounded (<10/sec under normal commercial load).
