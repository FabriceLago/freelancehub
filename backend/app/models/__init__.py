"""Agrège tous les modèles pour qu'ils s'enregistrent sur Base.metadata —
requis par `alembic revision --autogenerate` (migrations/env.py fait
`from app.models import *`)."""

from app.models.audit import AuditLog
from app.models.billing import Plan, Subscription
from app.models.crm import Client, Prospect
from app.models.invoice import Invoice, InvoiceLineItem, Payment
from app.models.organization import Membership, Organization, Role
from app.models.project import Project, Task
from app.models.quote import Quote, QuoteLineItem
from app.models.user import User

__all__ = [
    "AuditLog",
    "Plan",
    "Subscription",
    "Client",
    "Prospect",
    "Invoice",
    "InvoiceLineItem",
    "Payment",
    "Membership",
    "Organization",
    "Role",
    "Project",
    "Task",
    "Quote",
    "QuoteLineItem",
    "User",
]
