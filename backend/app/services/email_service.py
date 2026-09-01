import logging

import resend
from resend.exceptions import ResendError

from app.core.config import settings

logger = logging.getLogger("freelancehub.email")

# Sans RESEND_API_KEY (dev/tests), on retombe sur le comportement stub —
# permet de tester le flux complet (reset / vérification) en local sans
# dépendance externe ni compte Resend.


def _send(to_email: str, subject: str, html: str, stub_label: str, link: str) -> None:
    if not settings.resend_api_key:
        logger.info("[EMAIL STUB] %s pour %s : %s", stub_label, to_email, link)
        return

    resend.api_key = settings.resend_api_key
    try:
        resend.Emails.send(
            {
                "from": settings.email_from,
                "to": to_email,
                "subject": subject,
                "html": html,
            }
        )
    except ResendError:
        # Un email qui échoue à partir (clé invalide, domaine non vérifié,
        # rate limit Resend...) ne doit jamais faire planter l'inscription ou
        # la demande de reset — l'utilisateur peut toujours redemander un lien.
        logger.exception("Échec d'envoi email (%s) à %s", stub_label, to_email)


def send_verification_email(to_email: str, raw_token: str) -> None:
    link = f"{settings.frontend_url}/verify-email?token={raw_token}"
    _send(
        to_email,
        subject="Vérifiez votre adresse email — FreelanceHub",
        html=f'<p>Bienvenue sur FreelanceHub !</p><p><a href="{link}">Cliquez ici pour vérifier votre email</a></p>',
        stub_label="Vérification",
        link=link,
    )


def send_password_reset_email(to_email: str, raw_token: str) -> None:
    link = f"{settings.frontend_url}/reset-password?token={raw_token}"
    _send(
        to_email,
        subject="Réinitialisation de votre mot de passe — FreelanceHub",
        html=(
            f"<p>Une réinitialisation de mot de passe a été demandée pour ce compte.</p>"
            f'<p><a href="{link}">Cliquez ici pour choisir un nouveau mot de passe</a></p>'
            f"<p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</p>"
        ),
        stub_label="Reset mot de passe",
        link=link,
    )
