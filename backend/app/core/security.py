import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt : algorithme lent par conception (protège contre le brute-force
# hors-ligne en cas de fuite de la base) — standard pour le hash de mot de passe.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """subject = l'id utilisateur (str). Le token ne contient aucune donnée
    sensible : juste de quoi identifier l'utilisateur et vérifier l'expiration."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Retourne le user_id (sub) si le token est valide et non expiré, sinon None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def generate_raw_token() -> str:
    """Jeton opaque pour la vérification d'email / reset mot de passe —
    envoyé par email, jamais stocké en clair côté serveur (voir hash_token)."""
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    # SHA-256 suffit ici (contrairement au mot de passe, pas besoin de bcrypt) :
    # le jeton est déjà à haute entropie (secrets.token_urlsafe), donc pas de
    # risque de brute-force par dictionnaire — on veut juste éviter qu'une
    # fuite de la table verification_tokens rende les liens actifs réutilisables.
    return hashlib.sha256(raw_token.encode()).hexdigest()
