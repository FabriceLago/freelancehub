"""Il n'existe pas encore d'endpoint d'invitation (une organisation n'a
qu'un membre à l'inscription) — pour tester le contrôle de rôle sur un
MEMBER, on ajoute directement la membership en base via db_session, comme
le ferait un futur endpoint d'invitation."""

from app.core.security import create_access_token
from app.models.organization import Membership, Role
from app.models.user import User
from app.core.security import hash_password


def _add_member_to_org(db_session, organization_id) -> str:
    user = User(
        email=f"member-{organization_id}@example.com",
        hashed_password=hash_password("correct-horse-battery-staple"),
        full_name="Just A Member",
    )
    db_session.add(user)
    db_session.flush()
    db_session.add(Membership(user_id=user.id, organization_id=organization_id, role=Role.MEMBER))
    db_session.commit()
    return create_access_token(subject=str(user.id))


def test_member_cannot_delete_a_client(client, registered_org, db_session):
    owner_headers = registered_org["headers"]
    org_resp = client.get("/organizations/me", headers=owner_headers)
    organization_id = org_resp.json()["id"]

    member_token = _add_member_to_org(db_session, organization_id)
    member_headers = {"Authorization": f"Bearer {member_token}"}

    create_resp = client.post("/clients", json={"name": "Acme"}, headers=owner_headers)
    client_id = create_resp.json()["id"]

    resp = client.delete(f"/clients/{client_id}", headers=member_headers)
    assert resp.status_code == 403


def test_member_can_still_read_org_data(client, registered_org, db_session):
    # Contrôle négatif : require_role ne doit bloquer QUE l'action réservée
    # (delete), pas la lecture normale des données de sa propre organisation.
    owner_headers = registered_org["headers"]
    org_resp = client.get("/organizations/me", headers=owner_headers)
    organization_id = org_resp.json()["id"]

    member_token = _add_member_to_org(db_session, organization_id)
    member_headers = {"Authorization": f"Bearer {member_token}"}

    client.post("/clients", json={"name": "Acme"}, headers=owner_headers)

    resp = client.get("/clients", headers=member_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_owner_can_delete_a_client(client, registered_org):
    headers = registered_org["headers"]
    create_resp = client.post("/clients", json={"name": "Acme"}, headers=headers)
    client_id = create_resp.json()["id"]

    resp = client.delete(f"/clients/{client_id}", headers=headers)
    assert resp.status_code == 204
