import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.models.billing import Plan, PlanCode, Subscription, SubscriptionStatus
from app.models.organization import Organization
from app.repositories import plan_repository
from app.services import stripe_provider

# Statuts Stripe -> statuts internes. Tout ce qui n'est pas "active" ou
# "trialing" tombe dans PAST_DUE par défaut plutôt que de planter sur un
# statut Stripe qu'on n'a pas explicitement mappé (ex: "unpaid", "paused").
_STRIPE_STATUS_MAP: dict[str, SubscriptionStatus] = {
    "active": SubscriptionStatus.ACTIVE,
    "trialing": SubscriptionStatus.TRIALING,
    "canceled": SubscriptionStatus.CANCELED,
    "incomplete": SubscriptionStatus.INCOMPLETE,
    "incomplete_expired": SubscriptionStatus.CANCELED,
    "past_due": SubscriptionStatus.PAST_DUE,
    "unpaid": SubscriptionStatus.PAST_DUE,
}


class PlanNotAvailableError(AppError):
    pass


class NoStripeCustomerError(AppError):
    pass


class UnknownStripePriceError(AppError):
    pass


def list_plans(db: Session) -> list[Plan]:
    return plan_repository.list_all(db)


def create_checkout_session(db: Session, organization: Organization, plan_code: PlanCode, user_email: str) -> str:
    if plan_code == PlanCode.FREE:
        raise PlanNotAvailableError()

    plan = plan_repository.get_by_code(db, plan_code)
    if plan is None or plan.stripe_price_id is None:
        # Le plan existe chez nous mais son Product/Price Stripe n'a jamais
        # été créé — voir scripts/setup_stripe.py. Pas une erreur utilisateur.
        raise PlanNotAvailableError()

    return stripe_provider.create_checkout_session(
        price_id=plan.stripe_price_id,
        customer_email=user_email,
        client_reference_id=str(organization.id),
        success_url=f"{settings.frontend_url}/dashboard/settings?checkout=success",
        cancel_url=f"{settings.frontend_url}/dashboard/settings?checkout=cancelled",
    )


def create_portal_session(db: Session, organization: Organization) -> str:
    subscription = organization.subscription
    if subscription is None or subscription.stripe_customer_id is None:
        # Jamais passé par Checkout : pas de client Stripe à gérer via le portail.
        raise NoStripeCustomerError()
    return stripe_provider.create_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=f"{settings.frontend_url}/dashboard/settings",
    )


def _get_subscription_by_customer(db: Session, stripe_customer_id: str) -> Subscription | None:
    return db.execute(
        select(Subscription).where(Subscription.stripe_customer_id == stripe_customer_id)
    ).scalar_one_or_none()


def _sync_subscription_from_stripe(db: Session, subscription: Subscription, stripe_sub: dict) -> None:
    status = _STRIPE_STATUS_MAP.get(stripe_sub["status"], SubscriptionStatus.PAST_DUE)
    subscription.status = status
    subscription.stripe_subscription_id = stripe_sub["id"]

    # stripe_sub est un StripeObject, pas un dict : pas de .get() (voir
    # https://github.com/stripe/stripe-python#working-with-api-resources) —
    # l'accès par clé fonctionne, mais lève KeyError si absente.
    period_end = stripe_sub["current_period_end"] if "current_period_end" in stripe_sub else None
    if period_end:
        subscription.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)

    price_id = stripe_sub["items"]["data"][0]["price"]["id"]
    plan = plan_repository.get_by_stripe_price_id(db, price_id)
    if plan is None:
        raise UnknownStripePriceError()
    subscription.plan_id = plan.id


def handle_webhook_event(db: Session, event: dict) -> None:
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        organization_id = uuid.UUID(data["client_reference_id"])
        organization = db.get(Organization, organization_id)
        if organization is None or organization.subscription is None:
            return  # organisation supprimée entre-temps — rien à synchroniser
        organization.subscription.stripe_customer_id = data["customer"]
        # Le reste des champs (statut, plan, période) arrive juste après via
        # customer.subscription.updated — Stripe envoie systématiquement les
        # deux événements pour un nouveau checkout, pas la peine de dupliquer
        # la lecture ici.
        db.commit()

    elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
        subscription = _get_subscription_by_customer(db, data["customer"])
        if subscription is None:
            return  # pas encore lié (checkout.session.completed pas encore traité) — le prochain event resynchronisera
        _sync_subscription_from_stripe(db, subscription, data)
        db.commit()

    elif event_type == "customer.subscription.deleted":
        subscription = _get_subscription_by_customer(db, data["customer"])
        if subscription is None:
            return
        # Un abonnement annulé retombe sur Free — jamais de fonctionnalités
        # payantes qui persistent silencieusement après annulation.
        free_plan = plan_repository.get_by_code(db, PlanCode.FREE)
        subscription.status = SubscriptionStatus.CANCELED
        subscription.plan_id = free_plan.id
        db.commit()

    elif event_type == "invoice.payment_failed":
        subscription = _get_subscription_by_customer(db, data["customer"])
        if subscription is None:
            return
        subscription.status = SubscriptionStatus.PAST_DUE
        db.commit()
