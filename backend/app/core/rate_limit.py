"""Limite de débit en mémoire (par processus) sur les endpoints les plus
exposés au brute-force : login, inscription, reset de mot de passe.

Limite connue et assumée : ce compteur vit en mémoire du process — il ne
survit pas à un redémarrage et ne se partage pas entre plusieurs workers/
instances. Suffisant pour une seule instance (état actuel du déploiement) ;
passer à un backend Redis (`storage_uri="redis://..."`) est le prochain pas
si l'app tourne un jour derrière plusieurs workers."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
