from datetime import datetime, timezone

from app.models.crm import Client
from app.models.organization import Membership, Organization, Role
from app.models.quote import Quote, QuoteStatus
from app.models.user import User
from app.utils.numbering import generate_number


def _make_org_with_client(db_session):
    user = User(email="numbering@example.com", hashed_password="x", full_name="Numbering Test")
    db_session.add(user)
    db_session.flush()

    organization = Organization(name="Numbering Org")
    db_session.add(organization)
    db_session.flush()

    db_session.add(Membership(user_id=user.id, organization_id=organization.id, role=Role.OWNER))

    crm_client = Client(organization_id=organization.id, name="Acme")
    db_session.add(crm_client)
    db_session.commit()
    return organization, crm_client


def test_generate_number_starts_at_one(db_session):
    organization, _ = _make_org_with_client(db_session)
    number = generate_number(db_session, organization.id, "DEV", Quote)
    year = datetime.now(timezone.utc).year
    assert number == f"DEV-{year}-0001"


def test_generate_number_increments_per_existing_row(db_session):
    organization, crm_client = _make_org_with_client(db_session)
    db_session.add(
        Quote(
            organization_id=organization.id,
            client_id=crm_client.id,
            number="DEV-0000-9999",
            status=QuoteStatus.DRAFT,
            subtotal_cents=0,
            total_cents=0,
        )
    )
    db_session.commit()

    number = generate_number(db_session, organization.id, "DEV", Quote)
    year = datetime.now(timezone.utc).year
    assert number == f"DEV-{year}-0002"


def test_generate_number_is_scoped_per_organization(db_session):
    org_a, client_a = _make_org_with_client(db_session)
    db_session.add(
        Quote(
            organization_id=org_a.id,
            client_id=client_a.id,
            number="DEV-0000-0001",
            status=QuoteStatus.DRAFT,
            subtotal_cents=0,
            total_cents=0,
        )
    )
    db_session.commit()

    user_b = User(email="numbering-b@example.com", hashed_password="x", full_name="B")
    db_session.add(user_b)
    db_session.flush()
    org_b = Organization(name="Org B")
    db_session.add(org_b)
    db_session.flush()
    db_session.add(Membership(user_id=user_b.id, organization_id=org_b.id, role=Role.OWNER))
    db_session.commit()

    # Org B n'a aucun devis : son premier numéro doit rester 0001, pas hérité
    # du compteur de l'org A.
    number = generate_number(db_session, org_b.id, "DEV", Quote)
    year = datetime.now(timezone.utc).year
    assert number == f"DEV-{year}-0001"
