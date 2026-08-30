from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Chargées depuis les variables d'environnement (.env en local, vraies
    # variables d'env en production) — jamais codées en dur dans le repo.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/freelancehub"
    secret_key: str = "change-me-in-.env"
    access_token_expire_minutes: int = 60 * 24  # 24h
    cors_origins: list[str] = ["http://localhost:3000"]
    ai_api_key: str = ""
    # Le nom générique AI_API_KEY (plutôt que ANTHROPIC_API_KEY) garde le
    # AIService swappable vers un autre fournisseur sans renommer la config.
    ai_model: str = "claude-opus-5"
    ai_timeout_seconds: float = 30.0


settings = Settings()
