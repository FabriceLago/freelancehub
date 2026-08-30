"""Crée les Products + Prices Stripe pour les plans payants (Starter/Pro/
Business) et enregistre leurs price_id dans notre table `plans`.

À exécuter UNE FOIS après avoir créé un compte Stripe (mode test d'abord).
Idempotent : un plan qui a déjà un stripe_price_id est ignoré, donc relancer
le script après avoir ajouté une clé ne duplique rien.

Usage :
    cd backend && source venv/Scripts/activate
    python scripts/setup_stripe.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import stripe  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.models.billing import PlanCode  # noqa: E402
from app.repositories import plan_repository  # noqa: E402

PAID_PLANS = [PlanCode.STARTER, PlanCode.PRO, PlanCode.BUSINESS]


def main() -> None:
    if not settings.stripe_secret_key:
        print("STRIPE_SECRET_KEY n'est pas configuré dans backend/.env — arrêt.")
        sys.exit(1)

    stripe.api_key = settings.stripe_secret_key

    db = SessionLocal()
    try:
        for code in PAID_PLANS:
            plan = plan_repository.get_by_code(db, code)
            if plan is None:
                print(f"Plan {code.value} introuvable en base — vérifiez la migration de seed.")
                continue
            if plan.stripe_price_id:
                print(f"{plan.name} : déjà configuré ({plan.stripe_price_id}), ignoré.")
                continue

            product = stripe.Product.create(name=f"FreelanceHub — {plan.name}")
            price = stripe.Price.create(
                product=product.id,
                unit_amount=plan.price_cents,
                currency="eur",
                recurring={"interval": "month"},
            )
            plan.stripe_price_id = price.id
            db.commit()
            print(f"{plan.name} : créé (price_id={price.id})")

        print(
            "\nTerminé. Configurez maintenant le endpoint webhook dans le "
            "Dashboard Stripe (ou `stripe listen --forward-to "
            "localhost:8000/webhooks/stripe` en local) et copiez le secret "
            "de signature dans STRIPE_WEBHOOK_SECRET (backend/.env)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
