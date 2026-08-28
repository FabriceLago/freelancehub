# FreelanceHub

SaaS de gestion de prospects, clients, projets, devis et factures pour freelances UX/UI et Front-End, avec assistant IA intégré.

## Fonctionnalités (MVP)

- Authentification (inscription, connexion, profil)
- Gestion des prospects et clients
- Gestion des projets et tâches
- Devis et factures (export, suivi payé/impayé)
- Dashboard avec KPI d'activité
- Assistant IA pour la rédaction de devis et relances

## Architecture

```text
saas/
├── frontend/          Next.js 15 + TypeScript + Tailwind CSS
├── backend/           FastAPI + SQLAlchemy + Alembic
├── infrastructure/
│   └── docker/         Dockerfiles frontend/backend
├── docker-compose.yml
├── .env.example
└── README.md
```

## Installation

### Prérequis
- Node.js 20+
- Python 3.12+ (le venv local peut utiliser une autre version, l'image Docker fixe 3.12)
- PostgreSQL 16 (ou Docker)

### Variables d'environnement
```bash
cp .env.example .env
# éditer .env avec vos propres valeurs
```

### Backend
```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash — venv\Scripts\activate.bat sous cmd.exe
pip install -r requirements.txt
alembic upgrade head            # applique les migrations
uvicorn app.main:app --reload   # démarre l'API sur http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                     # démarre sur http://localhost:3000
```

## Développement avec Docker

```bash
docker compose build
docker compose up
docker compose down
```

Lance PostgreSQL, le backend (port 8000) et le frontend (port 3000) ensemble.

## Tests

```bash
# Backend
cd backend && source venv/Scripts/activate && pytest

# Frontend
cd frontend && npm test
```

## Déploiement

Voir les phases 17-18 du plan de développement (à venir) pour l'architecture de déploiement en production.

## Statut du projet

Projet en cours de construction, étape par étape. Voir l'historique de conversation pour l'analyse produit (Étape 0) et la maquette UX/UI (Étape 1).
