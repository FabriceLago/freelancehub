// Sentry côté navigateur (Phase 19). Le DSN n'est pas un secret — conçu par
// Sentry pour être embarqué dans un bundle client public (il n'autorise que
// l'envoi d'événements, jamais la lecture de données).
import * as Sentry from "@sentry/nextjs";

if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  });
}
