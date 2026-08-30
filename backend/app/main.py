import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import ai, auth, billing, clients, invoices, organizations, projects, prospects, quotes, users, webhooks
from app.core.config import settings
from app.core.rate_limit import limiter

# Sans ceci, le logger racine reste au niveau WARNING par défaut et les
# logger.info() applicatifs (ex: le stub d'email) sont silencieusement ignorés.
logging.basicConfig(level=logging.INFO)

_secret_looks_like_placeholder = settings.secret_key.startswith("change-me") or len(settings.secret_key) < 32
if _secret_looks_like_placeholder and settings.environment != "development":
    # Filet de sécurité : une SECRET_KEY par défaut/trop courte en prod serait
    # devinable par un attaquant, qui pourrait alors forger des JWT valides.
    # Vérifie le préfixe "change-me" (couvre le placeholder du code ET celui
    # de .env.example) plutôt qu'une égalité stricte à une seule valeur connue.
    raise RuntimeError(
        "SECRET_KEY est encore une valeur par défaut ou trop courte (<32 "
        "caractères). Définis une vraie clé secrète aléatoire avant de "
        "lancer l'app hors développement."
    )

# En production, /docs, /redoc et /openapi.json exposent toute la surface de
# l'API (routes, schémas, modèles) publiquement — utile en dev, à couper au-delà.
_docs_enabled = settings.environment == "development"

app = FastAPI(
    title="FreelanceHub API",
    version="0.1.0",
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# En dev, le frontend (localhost:3000) et l'API (localhost:8000) sont sur des
# origines différentes : sans CORS, le navigateur bloquerait les requêtes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "FreelanceHub API", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizations.router)
app.include_router(prospects.router)
app.include_router(clients.router)
app.include_router(projects.router)
app.include_router(quotes.router)
app.include_router(invoices.router)
app.include_router(ai.router)
app.include_router(billing.router)
app.include_router(webhooks.router)
