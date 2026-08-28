import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.organization import Membership, Role
from app.models.user import User
from app.repositories import user_repository

# tokenUrl sert uniquement à générer la doc Swagger (bouton "Authorize") —
# l'endpoint réel est POST /auth/login qui, lui, prend du JSON et pas un
# formulaire OAuth2 classique.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou expirés",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_error

    subject = decode_access_token(token)
    if subject is None:
        raise credentials_error
    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise credentials_error

    user = user_repository.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_error

    return user


# OWNER > ADMIN > MEMBER : un rang supérieur satisfait automatiquement les
# exigences d'un rang inférieur (un OWNER peut tout ce qu'un ADMIN peut faire).
_ROLE_RANK = {Role.MEMBER: 1, Role.ADMIN: 2, Role.OWNER: 3}


def get_current_membership(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Membership:
    """Résout l'organisation de l'utilisateur courant. Le MVP ne crée qu'une
    membership par utilisateur (à l'inscription) : on prend la première/seule.
    Le jour où un utilisateur peut appartenir à plusieurs organisations
    (invitation à rejoindre une autre équipe), cette dépendance devra lire un
    en-tête/paramètre "organisation active" plutôt que de prendre la première."""
    membership = db.execute(
        select(Membership).where(Membership.user_id == current_user.id).limit(1)
    ).scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Aucune organisation associée à ce compte"
        )
    return membership


def require_role(minimum: Role):
    """Dépendance paramétrée : `Depends(require_role(Role.ADMIN))` dans un
    endpoint refuse (403) tout membre dont le rôle est en dessous du minimum
    requis sur SON organisation — c'est le point de contrôle qui empêchera un
    utilisateur d'agir sur les données d'une organisation qui n'est pas la
    sienne (Phase 11), puisque get_current_membership ne renvoie jamais que
    la propre organisation de l'utilisateur courant."""

    def dependency(membership: Membership = Depends(get_current_membership)) -> Membership:
        if _ROLE_RANK[membership.role] < _ROLE_RANK[minimum]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle insuffisant pour cette action",
            )
        return membership

    return dependency
