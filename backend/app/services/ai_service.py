import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.models.ai import AiGeneration
from app.models.billing import Subscription
from app.models.crm import Client
from app.models.organization import Organization
from app.repositories import client_repository, invoice_repository
from app.services import ai_provider

QUOTE_DRAFT_SYSTEM_PROMPT = (
    "Tu es un assistant qui aide des freelances UX/UI et développeurs "
    "Front-End à préparer des devis. À partir d'une courte description de "
    "projet, propose 2 à 6 lignes de devis réalistes pour un freelance "
    "(description courte et professionnelle, quantité, prix unitaire en "
    "centimes d'euro — reste réaliste, ni trop bas ni exagéré) et un taux "
    "de TVA suggéré (20 par défaut pour la France, sauf indication "
    "contraire dans la description)."
)

REMINDER_SYSTEM_PROMPT = (
    "Tu rédiges des emails de relance de facture impayée pour des "
    "freelances, à destination de leurs clients professionnels. Ton poli "
    "et professionnel, ferme sans être agressif. Réponds en français."
)


class AIQuotaExceededError(AppError):
    pass


class ClientNotInOrganizationError(AppError):
    pass


class InvoiceNotFoundError(AppError):
    pass


class QuoteDraftLineItem(BaseModel):
    description: str
    quantity: float = Field(gt=0)
    unit_price_cents: int = Field(ge=0)


class QuoteDraftResult(BaseModel):
    line_items: list[QuoteDraftLineItem]
    suggested_tax_rate: float = Field(ge=0, le=100)


class ReminderDraftResult(BaseModel):
    subject: str
    body: str


def _get_ai_limit(db: Session, organization_id: uuid.UUID) -> int | None:
    org = db.execute(
        select(Organization)
        .options(selectinload(Organization.subscription).selectinload(Subscription.plan))
        .where(Organization.id == organization_id)
    ).scalar_one()
    return org.subscription.plan.ai_generations_per_month


def _count_usage_this_month(db: Session, organization_id: uuid.UUID) -> int:
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return db.execute(
        select(func.count())
        .select_from(AiGeneration)
        .where(AiGeneration.organization_id == organization_id, AiGeneration.created_at >= month_start)
    ).scalar_one()


def _check_quota(db: Session, organization_id: uuid.UUID) -> None:
    limit = _get_ai_limit(db, organization_id)
    if limit is None:
        return  # plan illimité (Pro/Business)
    if _count_usage_this_month(db, organization_id) >= limit:
        raise AIQuotaExceededError()


def _record_usage(db: Session, organization_id: uuid.UUID, kind: str) -> None:
    # Enregistré seulement APRÈS un appel IA réussi — un appel qui échoue
    # (clé invalide, timeout...) ne doit pas consommer le quota mensuel de
    # l'utilisateur pour rien.
    db.add(AiGeneration(organization_id=organization_id, kind=kind))
    db.commit()


def generate_quote_draft(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID, prompt: str) -> QuoteDraftResult:
    if client_repository.get_for_organization(db, organization_id, client_id) is None:
        raise ClientNotInOrganizationError()

    _check_quota(db, organization_id)
    result = ai_provider.generate_structured(QUOTE_DRAFT_SYSTEM_PROMPT, prompt, QuoteDraftResult)
    _record_usage(db, organization_id, "quote_draft")
    return result


def generate_reminder_draft(db: Session, organization_id: uuid.UUID, invoice_id: uuid.UUID) -> ReminderDraftResult:
    invoice = invoice_repository.get_for_organization(db, organization_id, invoice_id)
    if invoice is None:
        raise InvoiceNotFoundError()

    client = db.get(Client, invoice.client_id)
    balance_euros = invoice.balance_cents / 100
    due = invoice.due_date.isoformat() if invoice.due_date else "non précisée"
    user_prompt = (
        f"Facture {invoice.number}, montant dû {balance_euros:.2f} €, "
        f"client {client.name}, échéance {due}. Rédige un email de relance "
        f"(objet + corps)."
    )

    _check_quota(db, organization_id)
    result = ai_provider.generate_structured(REMINDER_SYSTEM_PROMPT, user_prompt, ReminderDraftResult)
    _record_usage(db, organization_id, "reminder_draft")
    return result
