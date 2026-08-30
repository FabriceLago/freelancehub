from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, require_role
from app.core.database import get_db
from app.models.organization import Membership, Role
from app.schemas.billing import CheckoutSessionRequest, PlanOut, SessionUrlResponse
from app.services import billing_service
from app.services.billing_service import NoStripeCustomerError, PlanNotAvailableError
from app.services.stripe_provider import StripeNotConfiguredError, StripeProviderError

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanOut])
def list_plans(membership: Membership = Depends(get_current_membership), db: Session = Depends(get_db)):
    return billing_service.list_plans(db)


@router.post("/checkout-session", response_model=SessionUrlResponse)
def create_checkout_session(
    payload: CheckoutSessionRequest,
    membership: Membership = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    try:
        url = billing_service.create_checkout_session(
            db, membership.organization, payload.plan_code, membership.user.email
        )
    except PlanNotAvailableError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce plan n'est pas disponible à l'achat")
    except StripeNotConfiguredError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Paiement non configuré")
    except StripeProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return SessionUrlResponse(url=url)


@router.post("/portal-session", response_model=SessionUrlResponse)
def create_portal_session(
    membership: Membership = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    try:
        url = billing_service.create_portal_session(db, membership.organization)
    except NoStripeCustomerError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun abonnement payant actif — souscrivez d'abord à un plan",
        )
    except StripeNotConfiguredError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Paiement non configuré")
    except StripeProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return SessionUrlResponse(url=url)
