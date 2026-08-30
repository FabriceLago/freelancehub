def _create_client(client, headers) -> str:
    resp = client.post("/clients", json={"name": "Acme"}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_create_quote_computes_totals_server_side(client, registered_org):
    headers = registered_org["headers"]
    client_id = _create_client(client, headers)

    resp = client.post(
        "/quotes",
        json={
            "client_id": client_id,
            "tax_rate": "20",
            "line_items": [
                {"description": "Design", "quantity": 2, "unit_price_cents": 10000},
                {"description": "Dev", "quantity": 1, "unit_price_cents": 5000},
            ],
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    # subtotal = 2*10000 + 1*5000 = 25000 ; total = 25000 * 1.20 = 30000
    assert body["subtotal_cents"] == 25000
    assert body["total_cents"] == 30000
    assert body["status"] == "draft"


def test_client_cannot_send_a_fake_total_it_is_ignored(client, registered_org):
    # Le total n'est même pas un champ accepté par QuoteCreate : impossible
    # pour le client de l'imposer, le serveur le recalcule toujours.
    headers = registered_org["headers"]
    client_id = _create_client(client, headers)

    resp = client.post(
        "/quotes",
        json={
            "client_id": client_id,
            "total_cents": 1,
            "line_items": [{"description": "Design", "quantity": 1, "unit_price_cents": 10000}],
        },
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["total_cents"] == 10000


def test_quote_cannot_be_edited_once_sent(client, registered_org):
    headers = registered_org["headers"]
    client_id = _create_client(client, headers)

    create_resp = client.post(
        "/quotes",
        json={
            "client_id": client_id,
            "line_items": [{"description": "Design", "quantity": 1, "unit_price_cents": 10000}],
        },
        headers=headers,
    )
    quote_id = create_resp.json()["id"]

    transition_resp = client.post(f"/quotes/{quote_id}/transition", json={"status": "sent"}, headers=headers)
    assert transition_resp.status_code == 200

    edit_resp = client.patch(
        f"/quotes/{quote_id}",
        json={"line_items": [{"description": "Changed", "quantity": 1, "unit_price_cents": 99999}]},
        headers=headers,
    )
    assert edit_resp.status_code == 409


def test_quote_invalid_status_transition_is_rejected(client, registered_org):
    headers = registered_org["headers"]
    client_id = _create_client(client, headers)

    create_resp = client.post(
        "/quotes",
        json={
            "client_id": client_id,
            "line_items": [{"description": "Design", "quantity": 1, "unit_price_cents": 10000}],
        },
        headers=headers,
    )
    quote_id = create_resp.json()["id"]

    # DRAFT -> ACCEPTED n'est pas une transition permise (doit passer par SENT)
    resp = client.post(f"/quotes/{quote_id}/transition", json={"status": "accepted"}, headers=headers)
    assert resp.status_code == 400


def test_only_accepted_quote_can_become_an_invoice(client, registered_org):
    headers = registered_org["headers"]
    client_id = _create_client(client, headers)

    create_resp = client.post(
        "/quotes",
        json={
            "client_id": client_id,
            "line_items": [{"description": "Design", "quantity": 1, "unit_price_cents": 10000}],
        },
        headers=headers,
    )
    quote_id = create_resp.json()["id"]

    resp = client.post(f"/quotes/{quote_id}/convert-to-invoice", headers=headers)
    assert resp.status_code == 400
