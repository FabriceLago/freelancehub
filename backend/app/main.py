from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

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
