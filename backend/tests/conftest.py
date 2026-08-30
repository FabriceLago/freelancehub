"""Fixtures pytest partagées. Les tests tournent contre une VRAIE base
Postgres dédiée (freelancehub_test) — jamais de mock ni de SQLite — pour
rester cohérent avec le reste du projet : ce qui est testé contre une base
qui se comporte différemment (types, contraintes, enums) de la prod donne une
fausse confiance.

Les variables d'environnement sont fixées ICI, avant tout import de `app.*`,
car `app.core.config.settings` et `app.core.database.engine` sont construits
une seule fois à l'import — les changer après coup n'aurait aucun effet."""

import os

os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/freelancehub_test"
os.environ["SECRET_KEY"] = "test-secret-key-only-for-automated-tests-not-for-any-real-use-1234567890"
os.environ["ENVIRONMENT"] = "development"  # garde le garde-fou SECRET_KEY et /docs hors du chemin des tests
os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake_key_for_signature_tests_only"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_fake_secret_for_signature_tests_only"
os.environ["AI_API_KEY"] = ""

import uuid  # noqa: E402

import psycopg  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402
from app.main import app  # noqa: E402
from app.models.billing import Plan, PlanCode  # noqa: E402


def _ensure_test_database_exists() -> None:
    # CREATE DATABASE ne supporte pas IF NOT EXISTS -> on tente et on ignore
    # le cas où elle existe déjà (run précédent).
    admin_conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5432/postgres", autocommit=True
    )
    try:
        admin_conn.execute("CREATE DATABASE freelancehub_test")
    except psycopg.errors.DuplicateDatabase:
        pass
    finally:
        admin_conn.close()


_PLAN_SEED = [
    {"code": PlanCode.FREE, "name": "Free", "price_cents": 0, "max_prospects": 3, "max_documents_per_month": 2, "ai_generations_per_month": 0},
    {"code": PlanCode.STARTER, "name": "Starter", "price_cents": 900, "max_prospects": None, "max_documents_per_month": 15, "ai_generations_per_month": 5},
    {"code": PlanCode.PRO, "name": "Pro", "price_cents": 1900, "max_prospects": None, "max_documents_per_month": None, "ai_generations_per_month": None},
    {"code": PlanCode.BUSINESS, "name": "Business", "price_cents": 3900, "max_prospects": None, "max_documents_per_month": None, "ai_generations_per_month": None},
]


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    # Reproduit ce que fait la migration seed_plans en prod : register()
    # assigne toujours le plan Free à une nouvelle organisation, donc au
    # moins ce plan doit exister pour que l'inscription fonctionne.
    _ensure_test_database_exists()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add_all(Plan(**data) for data in _PLAN_SEED)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_state():
    # Chaque test démarre avec un limiteur de débit remis à zéro : sinon les
    # tests s'exécutant dans la même minute partagent le même compteur
    # (même IP "testclient" pour toutes les requêtes) et se font bloquer
    # les uns les autres par erreur.
    limiter.reset()
    yield
    # Nettoyage par TRUNCATE plutôt que par rollback de transaction : certains
    # endpoints (webhooks Stripe) ouvrent leur propre session/commit et ne
    # peuvent pas être enveloppés dans une transaction de test.
    # "plans" est exclue : c'est un référentiel seedé une fois par session de
    # test, jamais écrit par les tests eux-mêmes (comme en production).
    table_names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables if t.name != "plans")
    with engine.connect() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))
        conn.commit()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    """Session DB brute, pour les tests qui doivent préparer un état que
    l'API ne permet pas encore de créer elle-même (ex : ajouter un membre
    MEMBER à une organisation — il n'existe pas encore d'endpoint
    d'invitation)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def registered_org(client):
    """Enregistre un utilisateur + son organisation (OWNER) et retourne un
    dict prêt à l'emploi pour les tests qui ont juste besoin d'un tenant
    authentifié, sans se soucier des détails d'inscription."""
    suffix = uuid.uuid4().hex[:8]
    email = f"owner-{suffix}@example.com"
    password = "correct-horse-battery-staple"
    resp = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test Owner",
            "organization_name": f"Org {suffix}",
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {
        "email": email,
        "password": password,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }
