"""Payload registration: ARC-Core as the authority record for ARC-Apache v5 manifests.

ARC-Apache owns the payload bytes (object storage + Merkle tree) and sends
only metadata here — manifest SHA-256, envelope SHA-256, Merkle root,
content class, source, and an optional receipt to verify. ARC-Core stores
the reference, verifies the receipt against the chain when one is given,
and appends a ``payload.registered`` authority event (which itself appends
an ``event`` receipt). The issued receipt hash is stored on the payload row
and returned to the caller.

This is the route ARC-Apache's ``integration/ARC_CORE_ROUTES.py`` stubs
(``POST /payloads/register``) and the route its ``ARC_CORE_ROUTE_STUB.md``
describes in the older ``/binary/*`` form. The v5 shape is canonical here;
the ``/binary/*`` spelling is intentionally not implemented — callers map
``register-manifest`` to ``POST /api/payloads/register`` and
``manifests/{hash}`` to ``GET /api/payloads/{hash}``.

Re-registration is idempotent: registering the same ``manifest_sha256``
twice returns the original record (same ``payload_id``, same issued
receipt), never a duplicate row. A policy change is a separate operation,
not a re-register.

See ``docs/ARCHITECTURE.md`` §8 (receipt chain) and §11 (endpoint catalogue).
"""
from __future__ import annotations
from arc.core.db import connect
from arc.core.schemas import EventIn, PayloadRegisterIn, new_id, utcnow
from arc.services.ingest import create_event


def _row_to_dict(row) -> dict:
    return {
        "payload_id": row["payload_id"],
        "manifest_sha256": row["manifest_sha256"],
        "envelope_sha256": row["envelope_sha256"],
        "merkle_root": row["merkle_root"],
        "content_class": row["content_class"],
        "source": row["source"],
        "policy_status": row["policy_status"],
        "receipt_sha256": row["receipt_sha256"],
        "signature_key_name": row["signature_key_name"],
        "issued_receipt_sha256": row["issued_receipt_sha256"],
        "registered_at": row["registered_at"],
        "registered_by_role": row["registered_by_role"],
    }


def register_payload(req: PayloadRegisterIn, actor_role: str) -> dict:
    """Register a payload manifest. Returns the stored record as a dict.

    Raises:
        ValueError: when ``receipt_sha256`` is given but no such receipt
            exists in the chain (the caller sends a 400).
    """
    if req.receipt_sha256:
        with connect() as conn:
            found = conn.execute(
                "SELECT 1 FROM receipt_chain WHERE hash = ? LIMIT 1",
                (req.receipt_sha256,),
            ).fetchone()
        if not found:
            raise ValueError(f"receipt not found in chain: {req.receipt_sha256}")

    with connect() as conn:
        existing = conn.execute(
            "SELECT * FROM payloads WHERE manifest_sha256 = ?",
            (req.manifest_sha256,),
        ).fetchone()
    if existing:
        return _row_to_dict(existing)

    payload_id = new_id("pay")
    registered_at = utcnow()
    with connect() as conn:
        conn.execute(
            """INSERT INTO payloads
               (payload_id, manifest_sha256, envelope_sha256, merkle_root,
                content_class, source, policy_status, receipt_sha256,
                signature_key_name, issued_receipt_sha256, registered_at,
                registered_by_role)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)""",
            (
                payload_id,
                req.manifest_sha256,
                req.envelope_sha256,
                req.merkle_root,
                req.content_class,
                req.source,
                req.policy_status,
                req.receipt_sha256,
                req.signature_key_name,
                registered_at,
                actor_role,
            ),
        )
        conn.commit()

    try:
        event = create_event(
            EventIn(
                event_type="payload.registered",
                source=req.source,
                subject=req.manifest_sha256,
                object=req.content_class,
                confidence=1.0,
                severity=3,
                payload={
                    "payload_id": payload_id,
                    "manifest_sha256": req.manifest_sha256,
                    "envelope_sha256": req.envelope_sha256,
                    "merkle_root": req.merkle_root,
                    "policy_status": req.policy_status,
                },
            )
        )
    except Exception:
        # All-or-nothing: a registration without its authority event is not
        # a registration. Remove the row so the next attempt starts clean.
        with connect() as conn:
            conn.execute("DELETE FROM payloads WHERE payload_id = ?", (payload_id,))
            conn.commit()
        raise

    with connect() as conn:
        receipt = conn.execute(
            "SELECT hash FROM receipt_chain WHERE record_type = 'event' AND record_id = ?",
            (event.id,),
        ).fetchone()
        issued = receipt["hash"] if receipt else None
        conn.execute(
            "UPDATE payloads SET issued_receipt_sha256 = ? WHERE payload_id = ?",
            (issued, payload_id),
        )
        conn.commit()

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM payloads WHERE payload_id = ?", (payload_id,)
        ).fetchone()
    return _row_to_dict(row)


def list_payloads(limit: int = 50) -> list[dict]:
    """Return the most recently registered payloads, newest first."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM payloads ORDER BY registered_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_payload(manifest_sha256: str) -> dict:
    """Return one payload by manifest hash.

    Raises:
        KeyError: when no payload with that manifest hash is registered
            (the caller sends a 404).
    """
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM payloads WHERE manifest_sha256 = ?",
            (manifest_sha256,),
        ).fetchone()
    if not row:
        raise KeyError(f"payload not registered: {manifest_sha256}")
    return _row_to_dict(row)
