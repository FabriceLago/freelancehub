"""Version automatisée de l'audit manuel de la Phase 11 : deux organisations,
un exemplaire de chaque ressource, et on vérifie qu'aucune des deux ne peut
jamais voir ou modifier les données de l'autre — le cœur de la promesse
multi-tenant. Toute régression ici est critique."""

import uuid


def _register(client, label):
    suffix = uuid.uuid4().hex[:8]
    resp = client.post(
        "/auth/register",
        json={
            "email": f"{label}-{suffix}@example.com",
            "password": "correct-horse-battery-staple",
            "full_name": label,
            "organization_name": f"{label} Org {suffix}",
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}}


def _create_client(client, headers) -> str:
    resp = client.post("/clients", json={"name": "Some Client"}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_org_a_cannot_read_org_b_client(client):
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")

    b_client_id = _create_client(client, org_b["headers"])

    resp = client.get(f"/clients/{b_client_id}", headers=org_a["headers"])
    assert resp.status_code == 404


def test_org_a_cannot_list_org_b_clients(client):
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")
    _create_client(client, org_b["headers"])

    resp = client.get("/clients", headers=org_a["headers"])
    assert resp.status_code == 200
    assert resp.json() == []


def test_org_a_cannot_update_org_b_client(client):
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")
    b_client_id = _create_client(client, org_b["headers"])

    resp = client.patch(f"/clients/{b_client_id}", json={"name": "Hijacked"}, headers=org_a["headers"])
    assert resp.status_code == 404


def test_org_a_cannot_delete_org_b_client(client):
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")
    b_client_id = _create_client(client, org_b["headers"])

    resp = client.delete(f"/clients/{b_client_id}", headers=org_a["headers"])
    assert resp.status_code == 404


def test_org_a_cannot_reference_org_b_client_when_creating_a_project(client):
    # Empêche de "rattacher" une ressource à soi-même en visant l'id d'un
    # client d'une autre organisation (contournement d'isolation via une FK).
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")
    b_client_id = _create_client(client, org_b["headers"])

    resp = client.post(
        "/projects", json={"client_id": b_client_id, "name": "Stolen project"}, headers=org_a["headers"]
    )
    assert resp.status_code == 400


def test_org_a_cannot_reference_org_b_client_when_creating_a_quote(client):
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")
    b_client_id = _create_client(client, org_b["headers"])

    resp = client.post(
        "/quotes",
        json={
            "client_id": b_client_id,
            "line_items": [{"description": "Hack", "quantity": 1, "unit_price_cents": 100}],
        },
        headers=org_a["headers"],
    )
    assert resp.status_code == 400


def test_org_a_cannot_read_org_b_prospect(client):
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")

    resp = client.post("/prospects", json={"name": "Some Prospect"}, headers=org_b["headers"])
    assert resp.status_code == 201
    b_prospect_id = resp.json()["id"]

    resp = client.get(f"/prospects/{b_prospect_id}", headers=org_a["headers"])
    assert resp.status_code == 404


def test_org_a_cannot_read_org_b_invoice(client):
    org_a = _register(client, "orga")
    org_b = _register(client, "orgb")
    b_client_id = _create_client(client, org_b["headers"])

    resp = client.post(
        "/invoices",
        json={
            "client_id": b_client_id,
            "line_items": [{"description": "Work", "quantity": 1, "unit_price_cents": 5000}],
        },
        headers=org_b["headers"],
    )
    assert resp.status_code == 201
    b_invoice_id = resp.json()["id"]

    resp = client.get(f"/invoices/{b_invoice_id}", headers=org_a["headers"])
    assert resp.status_code == 404


def test_org_a_own_data_is_still_reachable(client):
    # Contrôle négatif : l'isolation ne doit pas bloquer l'accès à ses PROPRES
    # données — sinon les tests ci-dessus pourraient "réussir" pour la mauvaise
    # raison (tout bloqué, y compris le légitime).
    org_a = _register(client, "orga")
    a_client_id = _create_client(client, org_a["headers"])

    resp = client.get(f"/clients/{a_client_id}", headers=org_a["headers"])
    assert resp.status_code == 200
    assert resp.json()["id"] == a_client_id
