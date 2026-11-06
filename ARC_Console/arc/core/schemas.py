"""Pydantic request/response models for ARC-Core's HTTP surface.

Every request body posted to ``arc.api.routes`` is validated against one of
the ``*In`` classes below; every structured response that isn't a bare dict
is built from one of the ``*Out`` classes. Field-level validators enforce
value ranges (confidence in [0,1], severity 1..10, RSSI -150..0, lat/lng
bounds, polygon shape, etc.) — these are the first line of defense before
any service code runs.

See ``docs/ARCHITECTURE.md`` §5.1 for the full catalogue.
"""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
import uuid


def utcnow() -> str:
    """Return the current UTC time as an ISO-8601 string.

    Used everywhere a timestamp is written to SQLite. Always UTC, always
    ISO-8601 so lexicographic ordering is also chronological.
    """
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    """Generate a prefixed 12-hex-char UUID4 identifier.

    Example: ``new_id("evt") -> "evt_8f3c1a2b4d5e"``. Prefixes used across
    the codebase: ``evt`` (event), ``ent`` (entity, via resolver), ``case``,
    ``prop`` (proposal), ``aud`` (audit), ``rcp`` (receipt), ``str``
    (structure), ``geo`` (geofence), ``trk`` (track), ``ovr`` (overlay),
    ``cal`` (calibration), ``inc`` (incident), ``sess`` (session), ``usr``
    (user), ``con`` (connector), ``run`` (connector run), ``note``,
    ``watch``, ``ce`` (case_event).
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _validate_polygon_points(polygon: list[list[float]]) -> list[list[float]]:
    """Validate a ``[[lat, lng], ...]`` polygon shape.

    Enforces: at least 3 vertices, each vertex a 2-element pair, latitudes in
    ``[-90, 90]``, longitudes in ``[-180, 180]``. Raises ``ValueError`` on
    any violation (which Pydantic surfaces as a 422 to the HTTP caller).
    """
    if len(polygon) < 3:
        raise ValueError("Polygon must have at least 3 points")
    for point in polygon:
        if len(point) != 2:
            raise ValueError("Each polygon point must be [lat, lng]")
        lat, lng = point
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("Polygon coordinates out of range")
    return polygon


class EventIn(BaseModel):
    event_type: str = Field(min_length=1, max_length=80)
    source: str = Field(default="manual", min_length=1, max_length=120)
    subject: str = Field(min_length=1, max_length=160)
    object: str | None = Field(default=None, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    confidence: float = Field(default=0.65, ge=0.0, le=1.0)
    severity: int = Field(default=3, ge=1, le=10)
    payload: dict[str, Any] = Field(default_factory=dict)
    ts: str = Field(default_factory=utcnow)


class EventOut(EventIn):
    id: str
    fingerprint: str


class WatchlistIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    entity_ref: str = Field(min_length=1, max_length=160)
    note: str = Field(default="", max_length=500)


class CaseIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    summary: str = Field(default="", max_length=4000)
    status: Literal["open", "active", "closed"] = "open"


class ProposalIn(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    target_type: str = Field(min_length=1, max_length=80)
    target_id: str = Field(min_length=1, max_length=160)
    rationale: str = Field(default="", max_length=4000)
    simulation_depth: int = Field(default=2, ge=1, le=5)




class ProposalOut(BaseModel):
    proposal_id: str
    created_at: str
    status: str
    created_by_role: str
    action: str
    target_type: str
    target_id: str
    rationale: str
    simulation: dict[str, Any]
    approved_at: str | None = None


class StructureIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    address: str = Field(min_length=1, max_length=200)
    structure_type: str = Field(min_length=1, max_length=80)
    levels: int = Field(default=1, ge=1, le=100)
    polygon: list[list[float]]

    @field_validator("polygon")
    @classmethod
    def validate_polygon(cls, value: list[list[float]]) -> list[list[float]]:
        return _validate_polygon_points(value)


class GeofenceIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    geofence_type: str = Field(min_length=1, max_length=80)
    structure_id: str | None = Field(default=None, max_length=160)
    polygon: list[list[float]]
    severity: int = Field(default=6, ge=1, le=10)

    @field_validator("polygon")
    @classmethod
    def validate_polygon(cls, value: list[list[float]]) -> list[list[float]]:
        return _validate_polygon_points(value)


class ObservationIn(BaseModel):
    sensor_id: str = Field(min_length=1, max_length=160)
    rssi: float = Field(ge=-150, le=0)
    reliability: float | None = Field(default=None, ge=0.0, le=1.0)


class TrackEstimateIn(BaseModel):
    subject: str = Field(min_length=1, max_length=160)
    structure_id: str = Field(min_length=1, max_length=160)
    source: str = Field(default="manual", min_length=1, max_length=120)
    floor: int | None = Field(default=None, ge=-5, le=300)
    observations: list[ObservationIn] = Field(min_length=1, max_length=64)


class BlueprintOverlayIn(BaseModel):
    structure_id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=160)
    image_url: str = Field(min_length=1, max_length=500)
    opacity: float = Field(default=0.45, ge=0.0, le=1.0)
    scale: float = Field(default=1.0, gt=0.0, le=100.0)
    offset_x: float = 0.0
    offset_y: float = 0.0
    rotation_deg: float = Field(default=0.0, ge=-360.0, le=360.0)
    floor: int | None = Field(default=None, ge=-5, le=300)


class CalibrationProfileIn(BaseModel):
    structure_id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=160)
    path_loss: float = Field(default=2.2, ge=0.1, le=8.0)
    noise_db: float = Field(default=3.5, ge=0.0, le=100.0)
    smoothing: float = Field(default=0.65, ge=0.0, le=1.0)
    notes: str = Field(default="", max_length=2000)


class ImportedTrackPointIn(BaseModel):
    lat: float = Field(ge=-90.0, le=90.0)
    lng: float = Field(ge=-180.0, le=180.0)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    zone: str | None = Field(default=None, max_length=80)
    floor: int | None = Field(default=None, ge=-5, le=300)
    ts: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class TrackImportIn(BaseModel):
    subject: str = Field(min_length=1, max_length=160)
    structure_id: str = Field(min_length=1, max_length=160)
    source: str = Field(default="import", min_length=1, max_length=120)
    track_points: list[ImportedTrackPointIn] = Field(min_length=1, max_length=1000)


class IncidentIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    status: Literal["open", "active", "closed"] = "open"
    subject: str | None = Field(default=None, max_length=160)
    structure_id: str | None = Field(default=None, max_length=160)
    details: dict[str, Any] = Field(default_factory=dict)


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)
    source: str = Field(default="local-ui", min_length=1, max_length=120)


class ConnectorIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    connector_type: Literal["filesystem_jsonl"] = "filesystem_jsonl"
    path: str = Field(min_length=1, max_length=500)
    enabled: bool = True


class NoteIn(BaseModel):
    subject_type: Literal["case", "entity", "subject", "connector"]
    subject_id: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=8000)
    tags: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            tag = item.strip().lower()
            if not tag:
                raise ValueError("Tags cannot be empty")
            if len(tag) > 40:
                raise ValueError("Tag too long")
            cleaned.append(tag)
        return cleaned


def _validate_sha256_hex(value: str | None) -> str | None:
    """Validate a SHA-256 hex digest: exactly 64 lowercase hex chars.

    Used by the payload-registration models. ``None`` passes through (for
    optional fields); anything else that is not 64 hex chars raises
    ``ValueError`` (Pydantic surfaces it as a 422 to the HTTP caller).
    """
    if value is None:
        return None
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value.lower()) or value != value.lower():
        raise ValueError("Must be exactly 64 lowercase hex characters (SHA-256)")
    return value


class PayloadRegisterIn(BaseModel):
    """Register an ARC-Apache v5 payload manifest with ARC-Core.

    Mirrors ``ARC-Apache/integration/ARC_CORE_ROUTES.py``. ARC-Core is the
    authority record: registration stores the manifest reference, verifies
    the optional receipt against the chain, and appends a
    ``payload.registered`` event + receipt. No blob bytes are ever sent —
    only hashes + metadata; chunks live in ARC-Apache object storage.
    """

    manifest_sha256: str = Field(min_length=64, max_length=64)
    envelope_sha256: str = Field(min_length=64, max_length=64)
    merkle_root: str = Field(min_length=64, max_length=64)
    content_class: str = Field(min_length=1, max_length=80)
    source: str = Field(min_length=1, max_length=120)
    policy_status: Literal["quarantine", "accepted", "rejected"] = "quarantine"
    receipt_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    signature_key_name: str | None = Field(default=None, max_length=120)

    @field_validator("manifest_sha256", "envelope_sha256", "merkle_root", "receipt_sha256")
    @classmethod
    def validate_hashes(cls, value: str | None) -> str | None:
        return _validate_sha256_hex(value)


class PayloadRegisterOut(BaseModel):
    ok: bool
    arc_event_type: str = "payload.registered"
    payload_id: str
    manifest_sha256: str
    receipt_sha256: str | None = None
    policy_status: str
    registered_at: str

