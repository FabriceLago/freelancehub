"""Limite de débit en mémoire (par processus) sur les endpoints les plus
exposés au brute-force : login, inscription, reset de mot de passe.

Limite connue et assumée : ce compteur vit en mémoire du process — il ne
survit pas à un redémarrage et ne se partage pas entre plusieurs workers/
instances. Suffisant pour une seule instance (état actuel du déploiement) ;
passer à un backend Redis (`storage_uri="redis://..."`) est le prochain pas
si l'app tourne un jour derrière plusieurs workers."""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _client_ip(request: Request) -> str:
    # derrière le proxy edge de Railway (ou n'importe quel reverse proxy en
    # prod), request.client.host est l'IP du proxy, pas celle du client —
    # trouvé en testant en prod : 7 tentatives de login échouées de suite
    # sans jamais déclencher le 429, alors que la même limite fonctionnait
    # en local sans proxy devant l'appli.
    #
    # Diagnostiqué via un endpoint de debug temporaire : Railway fournit
    # X-Real-IP (une IP unique, non falsifiable côté client — Railway
    # l'écrase avec l'IP TCP réellement connectée) qui correspond à la
    # PREMIÈRE valeur de X-Forwarded-For. La DERNIÈRE valeur de
    # X-Forwarded-For, elle, s'est avérée être un hop interne Railway
    # variable d'une requête à l'autre — c'est ce qui empêchait la limite
    # de jamais se déclencher (chaque tentative semblait venir d'un client
    # différent). X-Real-IP est donc la source la plus fiable ici.
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=_client_ip)
