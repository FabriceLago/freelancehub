import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, clients, invoices, organizations, projects, prospects, quotes, users
from app.core.config import settings

# Sans ceci, le logger racine reste au niveau WARNING par défaut et les
# logger.info() applicatifs (ex: le stub d'email) sont silencieusement ignorés.
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="FreelanceHub API", version="0.1.0")

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
