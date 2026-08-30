"""Couche d'abstraction fournisseur LLM (Phase 9) : c'est le SEUL fichier qui
connaît Anthropic. Le reste de l'app appelle generate_structured() — changer
de fournisseur plus tard ne touche que ce fichier, pas les services métier.

La clé API vit dans AI_API_KEY (jamais dans le frontend, jamais commitée) et
n'est lue qu'ici, jamais passée en clair ailleurs dans le code."""

import logging
from typing import TypeVar

import anthropic
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger("freelancehub.ai")

T = TypeVar("T", bound=BaseModel)


class AIProviderNotConfiguredError(AppError):
    pass


class AIProviderError(AppError):
    pass


def _get_client() -> anthropic.Anthropic:
    if not settings.ai_api_key:
        raise AIProviderNotConfiguredError()
    # Client recréé par appel plutôt que mis en cache au niveau module : ce
    # service ne fait qu'un ou deux appels par requête HTTP, pas de boucle
    # chaude où la réutilisation du client changerait la performance.
    return anthropic.Anthropic(api_key=settings.ai_api_key, timeout=settings.ai_timeout_seconds)


def generate_structured(system: str, user_prompt: str, output_format: type[T], *, max_tokens: int = 1024) -> T:
    """Appelle le LLM avec une sortie contrainte par schéma (output_format).
    Les retries réseau/429/5xx sont gérés par le SDK (2 tentatives par
    défaut) — inutile de les réimplémenter ici."""
    client = _get_client()
    try:
        response = client.messages.parse(
            model=settings.ai_model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            output_format=output_format,
        )
    except anthropic.AuthenticationError:
        logger.error("AI provider: clé API invalide ou révoquée")
        raise AIProviderError("Clé API IA invalide")
    except anthropic.RateLimitError:
        logger.warning("AI provider: rate limit atteint")
        raise AIProviderError("Service IA temporairement surchargé, réessayez dans un instant")
    except anthropic.APIConnectionError:
        logger.error("AI provider: erreur de connexion réseau")
        raise AIProviderError("Impossible de contacter le service IA")
    except anthropic.APIStatusError as exc:
        logger.error("AI provider: erreur API (status=%s)", exc.status_code)
        raise AIProviderError("Le service IA a renvoyé une erreur")

    # Coûts (Phase 9) : loggé à chaque appel réussi pour permettre un suivi
    # de consommation sans attendre une facture mensuelle du fournisseur.
    logger.info(
        "AI generation ok: model=%s input_tokens=%s output_tokens=%s",
        settings.ai_model,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    return response.parsed_output
