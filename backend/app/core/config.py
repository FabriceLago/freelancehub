from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Chargées depuis les variables d'environnement (.env en local, vraies
    # variables d'env en production) — jamais codées en dur dans le repo.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/freelancehub"

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, v: str) -> str:
        # Les Postgres managés (Railway, Render, Heroku...) injectent une URL
        # "postgres://" ou "postgresql://" sans préciser de driver — SQLAlchemy
        # utiliserait alors psycopg2 par défaut (absent de requirements.txt,
        # qui n'installe que psycopg 3) et planterait au démarrage.
        if v.startswith("postgres://"):
            return "postgresql+psycopg://" + v[len("postgres://") :]
        if v.startswith("postgresql://"):
            return "postgresql+psycopg://" + v[len("postgresql://") :]
        return v
    secret_key: str = "change-me-in-.env"
    access_token_expire_minutes: int = 60 * 24  # 24h
    cors_origins: list[str] = ["http://localhost:3000"]
    ai_api_key: str = ""
    # Le nom générique AI_API_KEY (plutôt que ANTHROPIC_API_KEY) garde le
    # AIService swappable vers un autre fournisseur sans renommer la config.
    ai_model: str = "claude-opus-5"
    ai_timeout_seconds: float = 30.0

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:3000"

    # Phase 12 — sécurité
    environment: str = "development"


settings = Settings()
