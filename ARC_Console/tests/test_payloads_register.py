"""Payload registration tests (ARC-Apache v5 manifest -> ARC-Core authority record).

Covers ``POST /api/payloads/register`` + ``GET /api/payloads`` +
``GET /api/payloads/{manifest_sha256}``: happy path, idempotent
re-registration, hash validation, receipt verification (known + unknown),
operator role guard, and the receipt chain still verifying after a
registration (the key-rotation regression check).
"""
import hashlib
import pytest
import httpx
from tests._client import make_transport
from arc.services.bootstrap import seed_demo


def setup_module():
    seed_demo()


def _h(tag: str) -> str:
    """Deterministic 64-hex SHA-256 for a test tag (stable across re-runs)."""
    return hashlib.sha256(tag.encode()).hexdigest()


def _payload(manifest_tag: str, **overrides) -> dict:
    body = {
        "manifest_sha256": _h(manifest_tag),
        "envelope_sha256": _h(manifest_tag + ":envelope"),
        "merkle_root": _h(manifest_tag + ":merkle"),
        "content_class": "test-payload",
        "source": "arc-apache-test",
    }
    body.update(overrides)
    return body


@pytest.mark.anyio
async def test_register_payload_happy_path():
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        resp = await client.post(
            "/api/payloads/register",
            json=_payload("happy-path"),
            headers={"X-ARC-Role": "operator"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["arc_event_type"] == "payload.registered"
    assert data["manifest_sha256"] == _h("happy-path")
    assert data["policy_status"] == "quarantine"
    assert data["payload_id"]
    assert data["registered_at"]
    # The issued receipt is a real 64-hex chain receipt for this registration.
    assert data["receipt_sha256"] and len(data["receipt_sha256"]) == 64


@pytest.mark.anyio
async def test_register_payload_idempotent():
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        first = await client.post(
            "/api/payloads/register",
            json=_payload("idempotent"),
            headers={"X-ARC-Role": "operator"},
        )
        second = await client.post(
            "/api/payloads/register",
            json=_payload("idempotent"),
            headers={"X-ARC-Role": "operator"},
        )
        listed = await client.get("/api/payloads?limit=100")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["payload_id"] == second.json()["payload_id"]
    assert first.json()["receipt_sha256"] == second.json()["receipt_sha256"]
    assert first.json()["registered_at"] == second.json()["registered_at"]
    matches = [p for p in listed.json()["payloads"] if p["manifest_sha256"] == _h("idempotent")]
    assert len(matches) == 1


@pytest.mark.anyio
async def test_register_payload_rejects_bad_hash():
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        resp = await client.post(
            "/api/payloads/register",
            json=_payload("bad-hash", manifest_sha256="not-a-hash"),
            headers={"X-ARC-Role": "operator"},
        )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_register_payload_rejects_unknown_receipt():
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        resp = await client.post(
            "/api/payloads/register",
            json=_payload("unknown-receipt", receipt_sha256=_h("no-such-receipt")),
            headers={"X-ARC-Role": "operator"},
        )
    assert resp.status_code == 400
    assert "receipt not found" in resp.json()["detail"]


@pytest.mark.anyio
async def test_register_payload_requires_operator():
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        resp = await client.post("/api/payloads/register", json=_payload("needs-operator"))
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_register_payload_with_known_receipt_and_accepted_policy():
    # The manifest tag is derived from the receipt being verified, so the
    # test registers a fresh payload on every run against a persistent DB
    # (the chain grows, so the most recent receipt — and hence the tag —
    # changes each run; idempotent re-register would return the old row).
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        receipts = await client.get("/api/receipts?limit=1")
        known = receipts.json()["receipts"][0]["hash"]
        tag = f"known-receipt-{known[:12]}"
        resp = await client.post(
            "/api/payloads/register",
            json=_payload(tag, receipt_sha256=known, policy_status="accepted"),
            headers={"X-ARC-Role": "operator"},
        )
        by_hash = await client.get(f"/api/payloads/{_h(tag)}")
    assert resp.status_code == 200
    assert resp.json()["policy_status"] == "accepted"
    assert by_hash.status_code == 200
    assert by_hash.json()["manifest_sha256"] == _h(tag)
    assert by_hash.json()["receipt_sha256"] == known


@pytest.mark.anyio
async def test_get_payload_unknown_returns_404():
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        resp = await client.get(f"/api/payloads/{_h('never-registered')}")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_receipt_chain_verifies_after_registration():
    async with httpx.AsyncClient(transport=make_transport(), base_url="http://testserver") as client:
        await client.post(
            "/api/payloads/register",
            json=_payload("chain-check"),
            headers={"X-ARC-Role": "operator"},
        )
        verify = await client.get("/api/receipts/verify")
    assert verify.status_code == 200
    assert verify.json()["ok"] is True
