import logging

logger = logging.getLogger("freelancehub.email")

# STUB : aucun fournisseur d'email n'est branché à ce stade (voir Phase 18 —
# "emails" dans la checklist production). En attendant, on logue le lien —
# ce qui permet de tester le flux complet (reset / vérification) en local
# sans dépendance externe. Ne PAS laisser ce stub en production : les emails
# ne partiraient jamais réellement.


def send_verification_email(to_email: str, raw_token: str) -> None:
    link = f"http://localhost:3000/verify-email?token={raw_token}"
    logger.info("[EMAIL STUB] Vérification pour %s : %s", to_email, link)


def send_password_reset_email(to_email: str, raw_token: str) -> None:
    link = f"http://localhost:3000/reset-password?token={raw_token}"
    logger.info("[EMAIL STUB] Reset mot de passe pour %s : %s", to_email, link)
