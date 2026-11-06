# ARC-Core Architecture

This document is the ground-truth technical reference for ARC-Core's implementation. It is generated from direct reading of the code, not from marketing copy. All file paths are relative to `ARC_Console/` unless otherwise stated.

## 1. Repository Layout
```
ARC-Core/
├── ARC_Console/                # The deployable service (FastAPI + SQLite)
│   ├── run_arc.py              # 1-line entrypoint: re-exports app for uvicorn
│   ├── seed_demo.py            # CLI to bootstrap the SQLite with demo data
│   ├── requirements.txt
│   ├── arc/
│   │   ├── api/
│   │   │   ├── main.py         # FastAPI app factory + lifespan + CORS + UI mount
│   │   │   ├── routes.py       # All HTTP endpoints (~47 routes)
│   │   │   └── deps.py         # startup() hook → bootstrap.seed_demo()
│   │   ├── core/
│   │   │   ├── config.py       # Envs, paths, limits
│   │   │   ├── db.py           # SQLite schema (17 tables) + connect()
│   │   │   ├── schemas.py      # Pydantic request/response models (18 classes)
│   │   │   ├── auth.py         # Role ladder + PBKDF2 password hashing
│   │   │   ├── risk.py         # score_event() + impact_band()
│   │   │   ├── util.py         # normalize_entity, guess_entity_type, fingerprint
│   │   │   └── simulator.py    # Proposal dry-run (outcomes + caution flags)
│   │   ├── services/
│   │   │   ├── bootstrap.py    # seed_demo() — initializes DB + sample data
│   │   │   ├── ingest.py       # create_event, list_events (+ fingerprint dedupe)
│   │   │   ├── resolver.py     # resolve_entity() — canonical entity_id minting
│   │   │   ├── graph.py        # upsert_edge, snapshot — directed relation graph
│   │   │   ├── watchlists.py   # create + list
│   │   │   ├── cases.py        # create, get, list, attach_event
│   │   │   ├── proposals.py    # create, approve, list (w/ simulation)
│   │   │   ├── notebook.py     # analyst notes (subject-scoped)
│   │   │   ├── connectors.py   # filesystem_jsonl poll-based ingestion
│   │   │   ├── authn.py        # login, resolve_session, ensure_bootstrap_admin
│   │   │   ├── audit.py        # log() + append_receipt() + verify_receipt_chain()
│   │   │   └── geospatial.py   # structures, sensors, geofences, tracks, heatmap,
│   │   │                         blueprint overlays, calibration, incidents,
│   │   │                         evidence-pack export
│   │   ├── geo/
│   │   │   ├── geometry.py     # centroid, bounds, point-in-polygon, haversine
│   │   │   └── estimator.py    # weighted-RSSI centroid + RSSI-from-distance
│   │   └── ui/                 # Static HTML + CSS + JS (dashboard, 6 pages)
│   ├── tests/                  # 5 pytest files (13 tests)
│   └── data/                   # Runtime SQLite + keys + connector inbox (gitignored)
├── docs/                       # Narrative + reference docs (this file lives here)
├── ECOSYSTEM.md                # Cross-repo integration contracts
├── README.md                   # Public-facing entrypoint
└── CHANGELOG.md                # Keep-a-Changelog history
```
Total Python footprint under `ARC_Console/`: **39 files, ~2,611 lines**. No external runtime dependency beyond FastAPI + Pydantic + the standard library (Uvicorn for serving; SQLite is in stdlib).

## 2. Process Model and Lifespan
`arc/api/main.py`:
```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    startup()   # → arc.api.deps.startup() → arc.services.bootstrap.seed_demo()
    yield
```
On every process start ARC-Core:
1. Creates `data/` if missing.
2. Runs `init_db()` (idempotent — all tables use `CREATE TABLE IF NOT EXISTS`).
3. Calls `ensure_bootstrap_admin()` (idempotent — creates `admin/arc-demo-admin` only if missing).
4. Seeds three demo events, three demo structures (Pine House, Cedar Duplex, Lakeview Home), sensors, geofences, blueprint overlays, calibration profiles, one demo RF track, one sample incident, and a filesystem connector.
5. Polls the demo connector once to import two seeded presence/geo_ping events.

Shutdown does no cleanup (SQLite is process-shared; WAL files drain on next open).
CORS is `*` in `DEMO_MODE=1`, closed otherwise. UI is mounted at `/ui` via `StaticFiles(html=True)`.

## 3. Configuration Surface (`arc/core/config.py`)
All configuration is env-driven with safe demo defaults:
- `APP_NAME = "ARC-Core"` (constant — advertised in `/health` and `/api/manifest`).
- `APP_VERSION = "6.0.0"` (constant — represents the v6 Operator-Grade line).
- `ARC_DEMO_MODE` (default `"1"`): when `"0"`, tightens CORS and token gating.
- `ARC_SHARED_TOKEN` (default empty): if set, non-observer endpoints require `X-ARC-Token` match; when not in demo mode, observer also requires it.
- `DEFAULT_LIMIT = 100`, `MAX_LIMIT = 500` (query caps, enforced in `_bounded()` in `routes.py`).
- `MAX_GRID_SIZE = 64` (heatmap cap).
- `RECEIPT_VERIFY_MAX = 5000` (`/api/receipts/verify` cap).
- `ARC_SESSION_TTL_HOURS` (default `12`): session token lifetime.
- `ARC_BOOTSTRAP_PASSWORD` (default `"arc-demo-admin"`): seeds the initial admin user's password.
- `DATA_DIR = <repo>/ARC_Console/data` (SQLite + keys + connector inboxes).
- `KEY_DIR = DATA_DIR / "keys"` (houses `receipt_signing.key`).
- `CONNECTOR_INBOX_DIR = DATA_DIR / "connectors"` (filesystem-connector root).
- `NOTEBOOK_EXPORT_LIMIT = 250`.

## 4. Persistence Layer (`arc/core/db.py`)
SQLite with `PRAGMA journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=15000` ms.
`connect()` returns a `sqlite3.Connection` with `Row` factory; callers use `with connect() as conn:` for transactional safety.
`init_db()` runs the full `SCHEMA` script idempotently.

### 4.1 Tables (18 total)

**Events & entities**
- `events(id, ts, event_type, source, subject, object, location, confidence, severity, fingerprint, payload_json)`
  Indexes: `ts`, `subject`, `object`, `event_type`, **unique `fingerprint`** (this is the dedupe mechanism — see §5.1).
- `entities(entity_id, label, entity_type, aliases_json, first_seen, last_seen, risk_score)` — `risk_score` is monotonically raised by `ingest.create_event` via `MAX(risk_score, ?)`; it never decays.
- `edges(edge_id, src_entity, dst_entity, relation, weight, last_seen)` — indexed on `src_entity` and `dst_entity`. `edge_id` is a deterministic composite `edge_{src}_{relation}_{dst}` truncated to 180 chars.

**Analyst workflow**
- `watchlists(watchlist_id, name, entity_id, note, created_at)` — unique on `(entity_id, name)`.
- `cases(case_id, title, priority, status, summary, created_at)` — priority in `{low, medium, high, critical}`, status in `{open, active, closed}`.
- `case_events(case_event_id, case_id, event_id, attached_at)` — unique on `(case_id, event_id)`; `attach_event` swallows `IntegrityError` (idempotent re-attach).
- `analyst_notes(note_id, created_at, actor_role, subject_type, subject_id, title, body, tags_json)` — indexed on `(subject_type, subject_id, created_at DESC)`; subject_type in `{case, entity, subject, connector}`.

**Governance**
- `proposals(proposal_id, created_at, status, created_by_role, action, target_type, target_id, rationale, simulation_json, approved_at)`.
- `audit_log(audit_id, ts, actor_role, action, target, detail_json)` — every mutating route writes here via `audit.log()`.
- `receipt_chain(receipt_id, ts, record_type, record_id, actor_role, payload_json, prev_hash, hash, signature, key_id)` — the tamper-evident chain; see §8 for protocol.
- `payloads(payload_id, manifest_sha256 UNIQUE, envelope_sha256, merkle_root, content_class, source, policy_status, receipt_sha256, signature_key_name, issued_receipt_sha256, registered_at, registered_by_role)` — the authority record for ARC-Apache v5 payload manifests; see §11.5 and `arc/services/payloads.py`. `receipt_sha256` is the caller-supplied receipt (verified against the chain when given); `issued_receipt_sha256` is the ARC-Core receipt for the `payload.registered` event.

**Geospatial**
- `structures(structure_id, name, address, structure_type, levels, polygon_json, center_lat, center_lng, created_at)` — unique on `(name, address)`; `center_lat/lng` are stored denormalized for fast queries, computed via `geometry.centroid`.
- `sensors(sensor_id, structure_id, label, sensor_type, lat, lng, reliability, created_at)` — `sensor_id` is a deterministic composite `{structure_id}-sn{idx}` (1..5).
- `geofences(geofence_id, name, geofence_type, structure_id, polygon_json, severity, created_at)`.
- `track_points(track_id, ts, subject, structure_id, source, lat, lng, confidence, zone, floor, observations_json, estimate_json)` — the estimated track ledger; indexed on `subject`, `ts`, and `(structure_id, ts DESC)`.
- `blueprint_overlays(overlay_id, structure_id, name, image_url, opacity, scale, offset_x, offset_y, rotation_deg, floor, created_at, updated_at)` — unique on `(structure_id, name, coalesce(floor, -1))`.
- `calibration_profiles(profile_id, structure_id, name, profile_json, notes, created_at, updated_at)` — unique on `(structure_id, name)`; `profile_json` stores `{path_loss, noise_db, smoothing}`.
- `incidents(incident_id, ts, title, severity, status, subject, structure_id, detail_json)` — severity is a free string (`"medium"`/`"critical"`/…), not the 1-10 int used for events.

**Auth**
- `auth_users(user_id, username UNIQUE, display_name, role, password_salt, password_hash, is_active, created_at, last_login_at)` — password storage is PBKDF2-HMAC-SHA256 at 120 000 iterations.
- `auth_sessions(session_id, user_id, role, issued_at, expires_at, session_token UNIQUE, created_from, is_revoked)` — tokens are `secrets.token_urlsafe(32)`, TTL 12 h by default.

**Connectors**
- `connector_sources(connector_id, name UNIQUE, connector_type, config_json, status, cursor_value, last_polled_at, last_result_json, created_at, updated_at)` — `cursor_value` is the filename high-watermark for the `filesystem_jsonl` connector.
- `connector_runs(run_id, connector_id, started_at, ended_at, status, imported_count, detail_json)` — one row per poll, `status ∈ {running, ok, error}`.

## 5. Core Types and Utilities

### 5.1 Pydantic schemas (`arc/core/schemas.py`)
20 models. Highlights:
- `EventIn` — `event_type` (1-80 chars), `source` (default `"manual"`, 1-120), `subject` (1-160), optional `object/location` (≤160), `confidence ∈ [0,1]` (default `0.65`), `severity ∈ [1,10]` (default `3`), `payload: dict`, `ts` defaulting to `utcnow()` ISO-8601 UTC.
- `PayloadRegisterIn` — ARC-Apache v5 manifest registration: `manifest_sha256` / `envelope_sha256` / `merkle_root` (each exactly 64 lowercase hex chars), `content_class`, `source`, `policy_status ∈ {quarantine, accepted, rejected}` (default `quarantine`), optional `receipt_sha256` (64 hex, verified against the chain) and `signature_key_name`.
- `PayloadRegisterOut` — `{ok, arc_event_type: "payload.registered", payload_id, manifest_sha256, receipt_sha256, policy_status, registered_at}`; `receipt_sha256` is the ARC-Core-issued receipt for the registration.
- `EventOut` — adds `id` and `fingerprint` (SHA-256 truncated to 24 hex chars).
- `StructureIn` / `GeofenceIn` both run polygons through `_validate_polygon_points`: ≥3 points, each a `[lat, lng]` pair with `-90≤lat≤90` and `-180≤lng≤180`.
- `ObservationIn` — `rssi ∈ [-150, 0]`, `reliability ∈ [0,1]` optional.
- `TrackEstimateIn` — 1-64 observations, `floor ∈ [-5, 300]`.
- `BlueprintOverlayIn` — `opacity ∈ [0,1]`, `scale ∈ (0, 100]`, `rotation_deg ∈ [-360, 360]`.
- `CalibrationProfileIn` — `path_loss ∈ [0.1, 8]`, `noise_db ∈ [0, 100]`, `smoothing ∈ [0, 1]`.
- `NoteIn.clean_tags` — strips/lowercases, forbids empty, caps at 40 chars/tag and 20 tags/note.

Helper functions: `utcnow()` → ISO-8601 UTC string; `new_id(prefix)` → `{prefix}_{uuid4().hex[:12]}`.

### 5.2 Hashing & Fingerprints (`arc/core/util.py`)
- `normalize_entity(text)` — whitespace-collapsed, trimmed, lower-cased.
- `guess_entity_type(value)` — heuristic: `"location"` if contains st/ave/road/rd/park/mall/airport; `"device"` if digits + one of device/cam/node; `"org"` if corp/inc/ltd/group; else `"person"`. This is intentionally lightweight — good enough for first-pass prioritization, overridable by an analyst.
- `fingerprint(event_type, source, subject, object_, location, payload)` — produces a **24-hex-char SHA-256 prefix** over a canonical JSON blob with normalized subject/object/location and sort-keyed payload. This is the dedupe identity for `events.fingerprint` (UNIQUE index) — replays of the same logical event return the existing row instead of inserting a duplicate.

### 5.3 Risk scoring (`arc/core/risk.py`)
```
score = confidence*50 + severity*4 + min(18, log1p(event_count_7d)*6) + min(12, related_edges*1.5)
if watchlisted: score += 18
score = round(min(100, score), 2)
```
Bounded to [0, 100]. `impact_band(score)` maps to `"critical" (≥80) / "high" (≥60) / "medium" (≥35) / "low"`.
Design intent (explainable): the formula is linear and inspectable so an analyst reading a risk score can always trace *why* it's that value without invoking an ML explainer.

### 5.4 Simulator (`arc/core/simulator.py`)
Pure-Python dry-run for proposals. Given `(action, target_id, risk_score, depth)`:
- Adds +10 to score if action ∈ {observe, flag, escalate}, else +4, clamped to 100.
- Emits canned `likely_outcomes` strings per action category.
- Emits `caution_flags` if `risk_score ≥ 60` (operator-cost warning) and an extra outcome if `depth ≥ 3` (second-order scrutiny).
- Returns `{target_id, action, impact_band, confidence, likely_outcomes, caution_flags}` where `confidence = min(0.95, 0.55 + risk_score/200)`.

## 6. Authentication and Authorization

### 6.1 Role ladder (`arc/core/auth.py`)
```
observer(1) < analyst(2) < operator(3) < approver(4) < admin(5)
```
`require_role(required, X-ARC-Role, X-ARC-Token, Authorization)` resolution order:
1. If `Authorization: Bearer <token>` is set, resolve the session via `authn.resolve_session`. Session's `role` overrides everything. Invalid/expired → **401**.
2. Else, use `X-ARC-Role` header (default `observer`). Unknown role → **400**.
3. If caller's rank < required rank → **403**.
4. Shared-token gate: if `ARC_SHARED_TOKEN` is configured *and* the required role is anything above observer, `X-ARC-Token` must match or **401**.
5. In non-demo mode, observer calls also require the shared token when it is set.

Session auth bypasses step 4/5 entirely (the session is already authenticated).

### 6.2 Password storage
`make_password_hash(password)` uses `PBKDF2-HMAC-SHA256`, **120 000 iterations**, 16-byte random salt. Hash + salt are base64-encoded. `verify_password` uses `hmac.compare_digest` for constant-time comparison.

### 6.3 Session lifecycle (`arc/services/authn.py`)
- `ensure_bootstrap_admin()` — no-op if an `admin` row exists; otherwise creates it with the bootstrap password and emits an `auth_user` receipt.
- `login(LoginIn)` — verifies password, inserts an `auth_sessions` row with a fresh `secrets.token_urlsafe(32)` session token, stamps `last_login_at`, writes an audit row + `auth_session` receipt. If credentials are still the defaults, the response includes a `bootstrap_password_hint` field flagging that.
- `resolve_session(token)` — returns None when: no token / token not found / is_revoked=1 / expires_at ≤ now. Otherwise returns the joined user+session row.

TTL defaults to 12 h; there's no sliding renewal — callers re-login on expiry.

## 7. Event + Entity + Graph Pipeline

### 7.1 Entity resolution (`arc/services/resolver.py`)
```python
entity_id = f"ent_{normalize(label).replace(' ','_')[:48]}"
```
- If the row exists: append the raw `label` to its `aliases_json`, refresh `last_seen`.
- Else: insert with `guess_entity_type(label)`, `aliases=[label]`, `risk_score=0`.

This is **deterministic and idempotent** — the same label (or any whitespace/case variant of it) always produces the same `entity_id`. That's why `entity_id` is safe to use as a foreign key in events/edges/tracks without a separate resolution step.

### 7.2 Event ingest (`arc/services/ingest.py::create_event`)
1. Resolve subject → `subject_entity` (`ent_...`). Same for object if present.
2. Compute `fingerprint` over the full canonical payload.
3. Open a transaction. If a row with this fingerprint already exists → return the existing `EventOut` (idempotent replay).
4. Compute risk inputs:
   - `watchlisted`: `EXISTS(SELECT 1 FROM watchlists WHERE entity_id=?)`.
   - `edge_count`: `COUNT(*) FROM edges WHERE src OR dst = subject_entity`.
   - `count7`: `COUNT(*) FROM events WHERE subject=? AND ts ≥ now-7d`.
5. `risk_score = score_event(...)` (see §5.3).
6. INSERT into `events` with `payload_json = json.dumps(payload, sort_keys=True)`.
7. Monotonically raise entity's risk: `UPDATE entities SET risk_score = MAX(risk_score, ?)`.
8. If `object_entity` is set: `upsert_edge(subject_entity, object_entity, event_type, increment=max(1.0, confidence*2))`.
9. Commit.
10. Outside the transaction: append a receipt `("event", event_id, "observer", {fingerprint, subject, object, source})` — see §8.

`list_events(limit, q)` does a LIKE search over `event_type | source | subject | object | location | payload_json | subject_label | object_label` when `q` is provided (full-table scan by design; FTS isn't wired up in v6). Results ordered by `ts DESC`.

### 7.3 Graph (`arc/services/graph.py`)
- `upsert_edge(src, dst, relation, increment=1.0, conn=None)` — composite id `edge_{src}_{relation}_{dst}` truncated to 180 chars. Existing edges get `weight += increment` (rounded to 2dp); new edges get `weight = increment`. Accepts an external `conn` so it can run inside ingest's transaction.
- `snapshot(limit=250)` → `{nodes, edges}` where nodes are top entities by `(risk_score DESC, last_seen DESC)` and edges are top relations by `(weight DESC, last_seen DESC)`.

## 8. Receipt Chain (`arc/services/audit.py`) — Protocol Spec
The receipt chain is ARC-Core's tamper-evident ledger.

### 8.1 Key handling
`_ensure_signing_key()` returns the 32-byte HMAC secret, in this precedence:

1. **`ARC_RECEIPT_SIGNING_KEY`** (env var, base64, exactly 32 bytes when decoded) — used as-is and never written to disk. A set-but-invalid value is a hard error (no silent fallback).
2. **`data/keys/receipt_signing.key`** — read if present, otherwise minted (32 random bytes via `secrets.token_bytes(32)`) and written with mode `0o600`. The file is git-ignored and must never be committed.

`KEY_ID="local-hmac-v2"` is recorded on every receipt row. The `v1` key was committed to the repository by accident and was rotated out: the committed file was removed from the working tree and a fresh `v2` key was minted. **Rotation invalidates every receipt signed under the old key** — verification under the new key fails on old rows, so a rotation restarts the verifiable chain from `GENESIS` (a fresh checkout gets a fresh DB + fresh key and all receipts verify). The old key still exists in git history; purging it is a history rewrite and is tracked as a separate step (see `SECURITY.md`).

### 8.2 Append protocol (`append_receipt`)
Given a new `(record_type, record_id, actor_role, payload: dict)`:
1. Read the tail: `SELECT hash FROM receipt_chain ORDER BY ts DESC, receipt_id DESC LIMIT 1`. If empty, `prev_hash = "GENESIS"`.
2. Build `payload_json = json.dumps(payload, sort_keys=True)` (canonical — sort order is part of the integrity contract).
3. `ts = utcnow()` (ISO-8601 UTC).
4. `chain_payload = f"{prev_hash}|{ts}|{record_type}|{record_id}|{actor_role}|{payload_json}"`.
5. `hash = sha256(chain_payload)` (hex).
6. `signature = base64(hmac_sha256(key, chain_payload))`.
7. INSERT the row.

### 8.3 Verification (`verify_receipt_chain`)
Walks rows in insertion order (`ts ASC, receipt_id ASC`). For each row it recomputes the expected hash and HMAC signature given the live `prev_hash` cursor. Any of these returns `{ok: False, reason, receipt_id}` immediately:
- `prev_hash_mismatch` — the stored `prev_hash` doesn't match the running tail.
- `hash_mismatch` — the stored hash doesn't match `sha256(chain_payload)`.
- `signature_mismatch` — the stored signature doesn't match a fresh HMAC.

Success returns `{ok: True, checked, tail, key_id}`. `/api/receipts/verify?limit=N` exposes this (capped at 5 000 rows for latency).

### 8.4 Which operations produce receipts
Search for `append_receipt(` in the code: `event`, `structure`, `sensor_batch`, `geofence`, `overlay`, `calibration`, `track`, `track_import`, `incident`, `auth_user`, `auth_session`, `note`, `connector`, `connector_run`. Analyst mutations that are already in `audit_log` but **not** receipted: watchlist, case, case attach, proposal create/approve. (These are tracked by `audit.log` for debugging but the receipt chain is scoped to state-producing events.)

## 9. Geospatial Stack

### 9.1 Geometry (`arc/geo/geometry.py`)
- `centroid(polygon)` — arithmetic mean of lat/lng (fine for small building-scale polygons; not area-weighted).
- `bounds_from_polygon(poly)` → `{minLat, maxLat, minLng, maxLng}`.
- `point_in_polygon(point, polygon)` — standard ray-cast algorithm; guards division by zero with `1e-12`. Accepts `{lat,lng}` for the point and `[[lat,lng],...]` for the polygon.
- `clamp_point_to_bounds(point, bounds)` — box-clamps a point to a bounding rect.
- `seeded(seed)` / `seeded_point_in_polygon(polygon, seed)` — deterministic pseudo-random point sampler: `sin(seed)*10000 % 1` drives `(r1,r2)` in-box candidates, up to 300 attempts, falling back to `centroid` if no in-polygon hit. Used to place sensors reproducibly inside a structure.
- `distance_meters(a, b)` — haversine with `earth_radius=6_371_000`. Used by the RF estimator.

### 9.2 RSSI estimator (`arc/geo/estimator.py`)
`estimate_from_observations(observations, structure=None)`:
```
for each obs:
    weight = max(0.0001, 10^((rssi+100)/12)) * max(0.2, reliability)
lat = Σ sensor_lat * weight / Σ weight
lng = Σ sensor_lng * weight / Σ weight
```
A weighted centroid of the sensor positions, where weight rises exponentially with RSSI (stronger signal ⇒ greater pull). `reliability` floors to 0.2 so a quarantined sensor still contributes something. The final point is clamped to the structure's bounding box when it lands outside the polygon.

Confidence model:
```
spread = |rssi[0] - rssi[1]|   (top two observations)
avg_rel = mean(reliability)
confidence = clamp(0.15, 0.99, 0.32 + spread/22 + avg_rel*0.25)
```
Higher when the strongest sensor is clearly dominant (large spread) and sensors are reliable. Reported as `method="weighted-rssi-centroid"`.

`rssi_from_distance_meters(m, noise_db=2.5)` — synthetic forward model used by `make_observations(truth, sensors)` to generate RF-like observations for demo tracks: `rssi = -30 - (32 + 20·log10(d))`. Path-loss exponent is baked in (≈2.0); calibration profiles (§4.1) store the real value but the forward demo currently uses the constant.

### 9.3 Track estimate (`services/geospatial.py::estimate_track`)
1. Load structure, run the estimator (zone-clamped to polygon).
2. Classify the `zone` via `infer_zone(polygon, point)` — quadrant/center heuristic over the bounding box:
   - If `|rx-0.5|<0.18` and `|ry-0.5|<0.18` → `"Center-Core"`.
   - `ry<0.33` → `"North Zone"`, `ry>0.66` → `"South Zone"`; else `rx<0.5` → `"West Zone"` else `"East Zone"`.
3. Insert into `track_points` (full observations + estimate blobs as JSON).
4. Evaluate all geofences where `structure_id = ? OR structure_id IS NULL`. Any containing the point contributes a `geofence_hit` with id/name/severity/type.
5. Build a `candidate_cloud` of up to 16 points distributed around the estimate at a radius `∝ (1 - confidence)` — this is what the UI renders as the uncertainty halo.
6. Append a `track` receipt.

### 9.4 Heatmap
`get_heatmap(structure_id, grid_size)` partitions the structure's bounding box into a `grid_size × grid_size` grid, counts track points per cell, drops cells whose center falls outside the polygon, and reports `(gx, gy, count, mean_confidence, center)`. Cap: `MAX_GRID_SIZE=64` → up to 4 096 cells.

### 9.5 Evidence pack (`export_evidence_pack`)
Given `case_id` *and/or* `subject`, assembles a portable JSON bundle:
- The case row (if any) and all attached events joined to the events table.
- Up to 250 track_points for the subject.
- Entities referenced by any collected event/subject (with aliases).
- Up to 250 edges touching those entities, ordered by weight.
- Case notes (subject_type=case) + subject notes (subject_type=subject), up to 100 each.
- Up to 250 most-recent receipts, with the top hash surfaced as `receipt_chain_tail`.
- A summary `{event_count, track_count, entity_count, edge_count, note_count}`.

This is the "portable offline proof" artifact — enough to replay the analyst's chain of reasoning and verify it against the receipt tail hash.

## 10. Connectors (`arc/services/connectors.py`)
Currently one connector type: `filesystem_jsonl`.

`poll_connector(connector_id)`:
1. Open the configured inbox directory; create it if missing.
2. Record a `connector_runs` row with status `running`.
3. Iterate `*.jsonl` files with `name > cursor_value` (lexicographic high-watermark), sorted.
4. For each JSON line, construct an `EventIn` with sensible defaults (`event_type="connector_event"`, `source="connector:<name>"`, `confidence=0.7`, `severity=4`), funnelling all unknown keys into `payload`.
5. Call `ingest.create_event` — full dedupe/risk/graph/receipt path applies.
6. On success: update `cursor_value` to the last processed filename, write `last_result = {imported, files:[{file, imported}]}`, close the run with `status=ok` + `imported_count`, append a `connector_run` receipt.
7. On exception: close the run with `status=error` and the exception repr; re-raise.

`ensure_demo_connector()` seeds `data/connectors/demo_feed/0001_seed.jsonl` with a presence and a geo_ping event, then registers+polls it.

## 11. HTTP Surface (`arc/api/routes.py`)
Total: **50 endpoints**. All mutating routes go through one of the `role_*` Depends guards, which wrap `auth.require_role`.

### 11.1 Meta
- `GET /` → serves `ui/dashboard.html` as `FileResponse`.
- `GET /health` → `{ok, service, version}`.
- `GET /api/manifest` → `{name, version, capabilities[...], ui[...]}` — capabilities list is the authoritative feature manifest, kept in lockstep with actual route behavior.

### 11.2 Auth
- `POST /api/auth/bootstrap` → `ensure_bootstrap_admin()`.
- `POST /api/auth/login` body `LoginIn` → `{session_id, token, role, username, display_name, issued_at, expires_at, bootstrap_password_hint?}`; **401** on bad creds.
- `GET /api/auth/session` header `Authorization: Bearer <token>` → `{session}`; **401** on invalid/expired.

### 11.3 Events / Entities / Graph
- `POST /api/events` (observer) body `EventIn` → `EventOut`.
- `GET /api/events?limit&q` → `{events:[...]}` (capped `1..MAX_LIMIT`).
- `GET /api/entities?limit` → `{entities:[...]}` with `aliases` deserialized.
- `GET /api/entities/{entity_id}` → `{entity, events[≤100], notes[≤50]}`; **404** if missing.
- `GET /api/graph?limit` → `{nodes, edges}`.
- `GET /api/timeline?limit` → `{timeline:[{id, ts, title, severity, source, location, payload}]}`.

### 11.4 Watchlists / Cases
- `POST /api/watchlists` (analyst) body `WatchlistIn` → `{watchlist_id, name, entity_id, note}` + audit.
- `GET /api/watchlists` → list.
- `POST /api/cases` (analyst) body `CaseIn` → case + audit.
- `GET /api/cases` / `GET /api/cases/{case_id}` — includes events and notes.
- `POST /api/cases/{case_id}/attach/{event_id}` (analyst) — idempotent; **404** on missing case or event.

### 11.5 Proposals / Simulate / Audit / Receipts / Payloads
- `POST /api/proposals` (operator) body `ProposalIn` — looks up target's risk, simulates, persists, audits.
- `POST /api/proposals/{id}/approve` (approver) — **404** if missing.
- `GET /api/proposals` — list including deserialized simulation.
- `GET /api/simulate/{target_id}?action&depth` → runs `simulator.simulate` against the target's live risk.
- `GET /api/audit?limit` → recent audit rows with deserialized detail.
- `GET /api/receipts?limit` → recent receipts.
- `GET /api/receipts/verify?limit` → see §8.3; **200** with `{ok:true/false, ...}`.
- `POST /api/payloads/register` (operator) body `PayloadRegisterIn` → registers an ARC-Apache v5 payload manifest (authority record); **400** when a supplied `receipt_sha256` is not in the chain; **422** on a malformed hash. Idempotent — re-registering the same manifest returns the original record. Appends a `payload.registered` event + receipt; see `arc/services/payloads.py`.
- `GET /api/payloads?limit` → most recently registered payloads, newest first.
- `GET /api/payloads/{manifest_sha256}` → one payload; **404** if not registered.

### 11.6 Evidence / Notes / Connectors / Incidents
- `GET /api/evidence?case_id&subject` — requires at least one; returns the evidence pack (§9.5). **400** if neither.
- `POST /api/notes` (analyst) body `NoteIn` → note + audit + receipt.
- `GET /api/notes?subject_type&subject_id&limit`.
- `POST /api/connectors` (admin) body `ConnectorIn` → upsert + audit.
- `GET /api/connectors`.
- `POST /api/connectors/{id}/poll` (admin) → polls inbox + audit + receipt.
- `POST /api/incidents` (analyst) body `IncidentIn` → incident + audit + receipt.
- `GET /api/incidents?limit`.

### 11.7 Geo
- `POST /api/geo/structures` (analyst) body `StructureIn`.
- `GET /api/geo/structures` / `GET /api/geo/structures/{id}`.
- `POST /api/geo/structures/{id}/sensors` (analyst) — builds 5 deterministic anchor sensors; idempotent.
- `GET /api/geo/sensors?structure_id`.
- `POST /api/geo/geofences` (analyst) body `GeofenceIn`.
- `GET /api/geo/geofences?structure_id`.
- `POST /api/geo/estimate` (observer) body `TrackEstimateIn` → resolves each observation's sensor row, fills in missing `reliability` from sensor default, runs the estimator. **400** on unknown `sensor_id`. **404** on missing structure.
- `POST /api/geo/demo-track/{structure_id}?subject` (observer) — synthetic RF demo.
- `GET /api/geo/tracks?limit&subject&structure_id`.
- `GET /api/geo/heatmap/{structure_id}?grid_size`.
- `POST /api/geo/blueprints` (analyst) body `BlueprintOverlayIn` — upsert keyed by `(structure_id, name, floor)`.
- `GET /api/geo/blueprints?structure_id`.
- `POST /api/geo/calibrations` (analyst) body `CalibrationProfileIn` — upsert keyed by `(structure_id, name)`.
- `GET /api/geo/calibrations?structure_id`.
- `POST /api/geo/import-tracks` (observer) body `TrackImportIn` — bulk insert up to 1 000 points; each point gets zone-inferred if not provided.

### 11.8 Header contract
- `X-ARC-Role`: one of `observer | analyst | operator | approver | admin` (default observer).
- `X-ARC-Token`: string matching `ARC_SHARED_TOKEN` when configured.
- `Authorization: Bearer <session_token>`: preferred auth; bypasses role+token headers.

## 12. Dataflow — One Event End-to-End
Example: analyst posts `{event_type:"transfer", source:"manual", subject:"Drone-7", object:"Cache-A", location:"Sector North", confidence:0.74, severity:6, payload:{units:4}}` via `POST /api/events` with `X-ARC-Role: observer`.
1. `role_observer` Depends → `require_role("observer", ...)` → allowed.
2. `schemas.EventIn` validates field widths + confidence/severity ranges.
3. `create_event`:
   - `resolve_entity("Drone-7")` → `ent_drone-7`; `resolve_entity("Cache-A")` → `ent_cache-a`. Both upsert into `entities` with `last_seen` refreshed.
   - `fingerprint(...)` → e.g. `"6a5b…"` (24 hex).
   - SELECT existing by fingerprint: none → proceed.
   - `watchlisted=False`, `edge_count=0`, `count7=0` for a fresh subject.
   - `score_event(0.74, 6, False, 0, 0) ≈ 37 + 24 + 0 + 0 = 61` → entity risk raised to 61.
   - INSERT into `events` with the canonical payload JSON.
   - UPDATE `entities.risk_score = MAX(old, 61)` where entity_id=`ent_drone-7`.
   - `upsert_edge("ent_drone-7", "ent_cache-a", "transfer", increment=max(1.0, 1.48)=1.48)`.
   - Commit.
4. `append_receipt("event", event_id, "observer", {fingerprint, subject:"ent_drone-7", object:"ent_cache-a", source:"manual"})`. This reads the current tail hash, computes `sha256(prev_hash|ts|type|id|role|payload)`, signs via HMAC, inserts the receipt row.
5. Return `EventOut` to the caller; `routes.post_event` writes an `audit_log` row via `audit.log()` before responding.

Any subsequent POST with identical content returns the same EventOut (dedupe via fingerprint). The receipt chain grows by one row per *unique* event.

## 13. Tests (`ARC_Console/tests/` — 31 tests, all passing)
- `test_arc_smoke.py` — end-to-end smoke through events, watchlists, cases, proposals, graph, audit. Covers happy-path for the core analyst loop.
- `test_geo_workflow.py` — structure → sensors → track estimate with fake observations; asserts point-in-polygon clamping and geofence-hit reporting.
- `test_geo_v4_features.py` — blueprint overlay upsert, calibration profile upsert (uniqueness on `(structure_id, name)`), heatmap grid sizing, import_tracks bulk path.
- `test_v5_hardening.py` — input-range enforcement: polygon validation rejections, RSSI out-of-range, negative-floor bounds, too-many-observations rejection.
- `test_v6_ops.py` — receipt-chain verification happy path + detection of out-of-band tampering by mutating a receipt row and re-running `verify_receipt_chain`.
- `test_hardware_floor.py` — the hardware-floor contract: runtime caps surface in `/api/manifest`, low-resource mode, and the portability matrix.
- `test_payloads_register.py` — ARC-Apache v5 payload registration: happy path, idempotent re-register, hash validation (422), unknown receipt (400), operator role guard (403), known-receipt + accepted policy, GET by manifest (404 when unknown), and the receipt chain verifying after a registration.

`conftest.py` wires the `anyio_backend` fixture; `_client.py` builds the `httpx.ASGITransport` for the real app. Tests run against the real SQLite DB, seeded idempotently by `seed_demo()` in each file's `setup_module` — a fresh checkout (no DB, no key file) regenerates both on first run.
Run with `pytest -q` from `ARC_Console/`, or `make test` from the repo root. CI (`.github/workflows/ci.yml`) runs the suite on Python 3.10/3.11/3.12.

## 14. Non-goals and Known Limits (v6.0.0)
- **No WebSocket / SSE** — every UI refresh is a GET poll. Designed for analyst pacing, not high-frequency telemetry.
- **No multi-tenant isolation** — a single SQLite file, one admin user family. Multi-team deployments need upstream isolation (reverse proxy + one DB per tenant).
- **No FTS5 on events** — `list_events(q=...)` is LIKE over multiple columns. Fine to ~10⁶ events on commodity disks; switch to FTS5 for larger deployments.
- **Key rotation invalidates prior receipts** — rotating the signing key (env var `ARC_RECEIPT_SIGNING_KEY`, or deleting `data/keys/receipt_signing.key` so a fresh one is minted) restarts the verifiable chain from `GENESIS`. There is no re-signing of old rows; a rotation is a deliberate break, not a migration. See §8.1.
- **Demo calibration is not applied in the estimator** — `calibration_profiles` stores `path_loss/noise_db/smoothing` but `estimator.py::rssi_from_distance_meters` currently uses constants. A future version will thread the profile through.
- **Risk does not decay** — entity `risk_score` is monotonic per `MAX(old, new)`. If an entity's situation de-escalates, score stays high unless an operator action resets it (no reset endpoint today).
- **Connector ecosystem is minimal** — only `filesystem_jsonl`. HTTP / S3 / syslog connectors are planned as separate connector_type values backed by the same `connector_sources` + `connector_runs` schema.

## 15. Extension Points (how to add things without breaking the contract)
- **New event type**: no schema change — just POST with a new `event_type` string. The graph naturally picks up new relations.
- **New connector type**: add a branch in `poll_connector` keyed on `connector.connector_type`, extend the Literal in `ConnectorIn`, preserve the `connector_runs` lifecycle contract.
- **New receipt producer**: call `append_receipt(record_type, record_id, actor_role, payload_dict)` after the commit that makes the state change. The chain will absorb it without schema changes — downstream verification still passes.
- **New role**: add to `ROLE_ORDER` in `arc/core/auth.py`. Keep ranks integer-ordered.
- **New geo feature**: put geometry helpers in `arc/geo/`, business logic in `arc/services/geospatial.py`, persistence in `arc/core/db.py` (remember to add indexes for any `WHERE` clauses you'll write).
- **New UI page**: drop HTML/CSS/JS in `arc/ui/`; add its name to the `ui` list in `/api/manifest`.

## 16. Versioning and Evidence of v6.0.0
- Version string lives in `arc/core/config.py::APP_VERSION`.
- The line "Tests: 13 passing" on the README badge reflects the real count in `ARC_Console/tests/` (not a placeholder).
- `AUDIT_REPORT_v*.md` files in `ARC_Console/` are historical audit artifacts from earlier versions (v2 initial, v3 geo, v4 spatial hardening, v5 DARPA-grade, v6 ops completion). They are narrative, not machine-verified, and kept for lineage.
- `ARC_Console_v3_0_Signal_Intelligence.zip` is a frozen snapshot of the v3 line for archival comparisons.

## 17. Dependencies (runtime)
`ARC_Console/requirements.txt`:
- `fastapi` — web framework.
- `uvicorn` — ASGI server (declared by caller, not imported in-process).
- `pydantic` — `EventIn` / validators. Pydantic v2 syntax (`field_validator`, `model_dump()`).
- Standard library only for: `sqlite3`, `hashlib`, `hmac`, `secrets`, `base64`, `uuid`, `datetime`, `json`, `pathlib`, `re`, `math`, `statistics`.

No scientific stack (NumPy/SciPy), no ORM, no Redis, no Celery. Deliberate minimalism.
