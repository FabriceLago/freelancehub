from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidTokenError
from app.core.security import create_access_token
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.register(
            db, payload.email, payload.password, payload.full_name, payload.organization_name
        )
    except EmailAlreadyRegisteredError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet email est déjà utilisé")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate(db, payload.email, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    # Avec un JWT sans état côté serveur (pas de refresh token ni de
    # blacklist — choix assumé du MVP), il n'y a rien à invalider côté API :
    # le client se contente de supprimer le token stocké. Cet endpoint existe
    # pour que le frontend ait un point d'appel cohérent si cette logique
    # évolue plus tard (ex : blacklist Redis).
    return None


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.request_password_reset(db, payload.email)
    # Toujours 204, que l'email existe ou non : évite l'énumération de comptes.
    return None


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        auth_service.reset_password(db, payload.token, payload.new_password)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien invalide ou expiré")
    return None


@router.get("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        auth_service.verify_email(db, token)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien invalide ou expiré")
    return None
