import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership
from app.core.database import get_db
from app.models.organization import Membership
from app.schemas.ai import QuoteDraftRequest, QuoteDraftResponse, ReminderDraftResponse
from app.services import ai_service
from app.services.ai_provider import AIProviderError, AIProviderNotConfiguredError
from app.services.ai_service import AIQuotaExceededError, ClientNotInOrganizationError, InvoiceNotFoundError

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/quote-draft", response_model=QuoteDraftResponse)
def create_quote_draft(
    payload: QuoteDraftRequest,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return ai_service.generate_quote_draft(db, membership.organization_id, payload.client_id, payload.prompt)
    except ClientNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client introuvable")
    except AIQuotaExceededError:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Quota IA atteint pour votre plan ce mois-ci — passez à un plan supérieur",
        )
    except AIProviderNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Assistant IA non configuré"
        )
    except AIProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@router.post("/invoices/{invoice_id}/reminder-draft", response_model=ReminderDraftResponse)
def create_reminder_draft(
    invoice_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return ai_service.generate_reminder_draft(db, membership.organization_id, invoice_id)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facture introuvable")
    except AIQuotaExceededError:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Quota IA atteint pour votre plan ce mois-ci — passez à un plan supérieur",
        )
    except AIProviderNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Assistant IA non configuré"
        )
    except AIProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
