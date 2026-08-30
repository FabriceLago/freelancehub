from fastapi import APIRouter, Depends

from app.api.deps import get_current_membership
from app.models.organization import Membership
from app.schemas.organization import OrganizationOut

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/me", response_model=OrganizationOut)
def read_current_organization(membership: Membership = Depends(get_current_membership)):
    return OrganizationOut(
        id=membership.organization.id,
        name=membership.organization.name,
        currency=membership.organization.currency,
        role=membership.role,
        plan=membership.organization.subscription.plan.code,
        subscription_status=membership.organization.subscription.status,
    )
