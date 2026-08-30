"""Couche d'abstraction Stripe — c'est le SEUL fichier qui importe le SDK
stripe. Le reste de l'app appelle ces fonctions ; changer de PSP plus tard
(ou juste faire évoluer l'intégration Stripe) ne touche que ce fichier."""

import logging

import stripe

from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger("freelancehub.stripe")


class StripeNotConfiguredError(AppError):
    pass


class StripeProviderError(AppError):
    pass


def _require_configured() -> None:
    if not settings.stripe_secret_key:
        raise StripeNotConfiguredError()
    stripe.api_key = settings.stripe_secret_key


def create_checkout_session(
    *, price_id: str, customer_email: str, client_reference_id: str, success_url: str, cancel_url: str
) -> str:
    """client_reference_id = notre organization_id : c'est ce qui permet au
    webhook de retrouver l'organisation sans dépendre d'un matching par email
    (fragile si l'email diffère entre notre compte et le paiement Stripe)."""
    _require_configured()
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=customer_email,
            client_reference_id=client_reference_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except stripe.error.StripeError as exc:
        logger.error("Stripe checkout session creation failed: %s", exc)
        raise StripeProviderError(str(exc))
    return session.url


def create_portal_session(*, customer_id: str, return_url: str) -> str:
    _require_configured()
    try:
        session = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
    except stripe.error.StripeError as exc:
        logger.error("Stripe portal session creation failed: %s", exc)
        raise StripeProviderError(str(exc))
    return session.url


def construct_webhook_event(payload: bytes, signature_header: str) -> "stripe.Event":
    _require_configured()
    if not settings.stripe_webhook_secret:
        raise StripeNotConfiguredError()
    try:
        return stripe.Webhook.construct_event(payload, signature_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        logger.warning("Stripe webhook signature verification failed: %s", exc)
        raise StripeProviderError("Signature webhook invalide")
