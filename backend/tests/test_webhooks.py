"""Le webhook Stripe n'a aucune protection par JWT (Stripe ne peut pas en
envoyer un) — sa seule ligne de défense est la vérification de signature
HMAC. On la signe à la main, exactement comme le fait le SDK Stripe côté
serveur, pour prouver que la vérification fonctionne dans les deux sens :
rejette une signature invalide, accepte une signature valide."""

import hashlib
import hmac
import json
import time

from app.core.config import settings


def _sign(payload: bytes, secret: str) -> str:
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode()}".encode()
    signature = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


def _make_event(event_type: str, data_object: dict) -> bytes:
    return json.dumps(
        {
            "id": "evt_test_1",
            "type": event_type,
            "data": {"object": data_object},
        }
    ).encode()


def test_webhook_with_invalid_signature_is_rejected(client):
    payload = _make_event("checkout.session.completed", {"customer": "cus_x", "client_reference_id": "x"})
    resp = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": "t=123,v1=deadbeef", "content-type": "application/json"},
    )
    assert resp.status_code == 400


def test_webhook_with_missing_signature_is_rejected(client):
    payload = _make_event("checkout.session.completed", {"customer": "cus_x", "client_reference_id": "x"})
    resp = client.post("/webhooks/stripe", content=payload, headers={"content-type": "application/json"})
    assert resp.status_code == 400


def test_webhook_with_valid_signature_updates_subscription(client, registered_org):
    org_resp = client.get("/organizations/me", headers=registered_org["headers"])
    organization_id = org_resp.json()["id"]

    payload = _make_event(
        "checkout.session.completed",
        {"customer": "cus_test_123", "client_reference_id": organization_id},
    )
    signature = _sign(payload, settings.stripe_webhook_secret)

    resp = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": signature, "content-type": "application/json"},
    )
    assert resp.status_code == 204


def test_webhook_without_configured_secret_returns_503(client, monkeypatch):
    monkeypatch.setattr(settings, "stripe_webhook_secret", "")
    payload = _make_event("checkout.session.completed", {"customer": "cus_x", "client_reference_id": "x"})
    resp = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": "t=123,v1=deadbeef", "content-type": "application/json"},
    )
    assert resp.status_code == 503
