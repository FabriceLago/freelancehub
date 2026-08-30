#!/bin/sh
# Applique les migrations avant de démarrer l'API : sans ça, un déploiement
# pourrait lancer du code qui attend une colonne/table qu'une migration
# n'a pas encore créée. "set -e" arrête le conteneur si la migration échoue
# plutôt que de démarrer une API contre un schéma incohérent.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
