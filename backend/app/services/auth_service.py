from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidTokenError
from app.core.security import generate_raw_token, hash_password, hash_token, verify_password
from app.models.auth_token import TokenPurpose, VerificationToken
from app.models.billing import Plan, PlanCode, Subscription, SubscriptionStatus
from app.models.organization import Membership, Organization, Role
from app.models.user import User
from app.repositories import user_repository
from app.services import email_service

VERIFICATION_TOKEN_TTL = timedelta(hours=24)
RESET_TOKEN_TTL = timedelta(hours=1)


def register(db: Session, email: str, password: str, full_name: str, organization_name: str) -> User:
    """Crée le User ET son organisation (avec un abonnement Free) dans la même
    transaction : un compte sans organisation ne peut rien faire dans une
    architecture multi-tenant, donc les deux naissent toujours ensemble."""
    if user_repository.get_by_email(db, email):
        raise EmailAlreadyRegisteredError()

    user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
    db.add(user)
    db.flush()  # attribue user.id sans committer, pour l'utiliser ci-dessous

    organization = Organization(name=organization_name)
    db.add(organization)
    db.flush()

    db.add(Membership(user_id=user.id, organization_id=organization.id, role=Role.OWNER))

    free_plan = db.execute(select(Plan).where(Plan.code == PlanCode.FREE)).scalar_one()
    db.add(
        Subscription(
            organization_id=organization.id, plan_id=free_plan.id, status=SubscriptionStatus.ACTIVE
        )
    )

    raw_token = generate_raw_token()
    db.add(
        VerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            purpose=TokenPurpose.EMAIL_VERIFICATION,
            expires_at=datetime.now(timezone.utc) + VERIFICATION_TOKEN_TTL,
        )
    )

    db.commit()
    db.refresh(user)

    email_service.send_verification_email(user.email, raw_token)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    # Même erreur générique que l'email n'existe pas ou que le mot de passe soit
    # faux : ne jamais laisser un attaquant déduire quels emails sont inscrits.
    if not user or not verify_password(password, user.hashed_password) or not user.is_active:
        raise InvalidCredentialsError()
    return user


def request_password_reset(db: Session, email: str) -> None:
    user = user_repository.get_by_email(db, email)
    if not user:
        return  # silencieux : ne pas révéler si l'email est inscrit ou non
    raw_token = generate_raw_token()
    db.add(
        VerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            purpose=TokenPurpose.PASSWORD_RESET,
            expires_at=datetime.now(timezone.utc) + RESET_TOKEN_TTL,
        )
    )
    db.commit()
    email_service.send_password_reset_email(user.email, raw_token)


def _consume_token(db: Session, raw_token: str, purpose: TokenPurpose) -> VerificationToken:
    token_hash = hash_token(raw_token)
    token = db.execute(
        select(VerificationToken).where(
            VerificationToken.token_hash == token_hash, VerificationToken.purpose == purpose
        )
    ).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if not token or token.used_at is not None or token.expires_at < now:
        raise InvalidTokenError()
    token.used_at = now
    return token


def reset_password(db: Session, raw_token: str, new_password: str) -> None:
    token = _consume_token(db, raw_token, TokenPurpose.PASSWORD_RESET)
    user = db.get(User, token.user_id)
    user.hashed_password = hash_password(new_password)
    db.commit()


def verify_email(db: Session, raw_token: str) -> None:
    token = _consume_token(db, raw_token, TokenPurpose.EMAIL_VERIFICATION)
    user = db.get(User, token.user_id)
    user.is_verified = True
    db.commit()
