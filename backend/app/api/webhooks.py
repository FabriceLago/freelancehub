import logging

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services import billing_service, stripe_provider
from app.services.billing_service import UnknownStripePriceError
from app.services.stripe_provider import StripeNotConfiguredError, StripeProviderError

logger = logging.getLogger("freelancehub.stripe")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe", status_code=status.HTTP_204_NO_CONTENT)
async def stripe_webhook(request: Request):
    # Endpoint volontairement SANS get_current_membership : Stripe ne peut
    # pas envoyer de JWT. La sécurité vient uniquement de la vérification de
    # signature ci-dessous (HMAC avec STRIPE_WEBHOOK_SECRET) — sans elle,
    # n'importe qui pourrait POSTer un faux événement "abonnement payé".
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    try:
        event = stripe_provider.construct_webhook_event(payload, signature)
    except StripeNotConfiguredError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Webhook non configuré")
    except StripeProviderError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signature invalide")

    # Session DB dédiée : cet endpoint n'a pas de dépendance get_current_user
    # pour fournir get_db via le cycle de requête habituel.
    db: Session = SessionLocal()
    try:
        billing_service.handle_webhook_event(db, event)
    except UnknownStripePriceError:
        # Un price_id Stripe qu'on ne reconnaît pas dans notre table plans —
        # signale un décalage de config (voir scripts/setup_stripe.py), pas
        # une attaque. On logue et on renvoie 200 : Stripe reste heureux et
        # ne boucle pas sur un retry vain, l'incident est visible dans les logs.
        logger.error("Stripe webhook: unknown price_id for event %s", event["type"])
    finally:
        db.close()

    return None
