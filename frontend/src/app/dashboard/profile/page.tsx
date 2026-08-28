"use client";

import { useAuth } from "@/lib/auth-context";

export default function ProfilePage() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-2xl font-bold">Profil</h1>

      <div className="max-w-md rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-5">
        <dl className="flex flex-col gap-4">
          <Row label="Nom complet" value={user.full_name} />
          <Row label="Email" value={user.email} />
          <Row
            label="Statut email"
            value={
              user.is_verified ? (
                <span className="rounded-md bg-[var(--color-ok-bg)] px-2 py-0.5 text-xs font-semibold text-[var(--color-ok)]">
                  Vérifié
                </span>
              ) : (
                <span className="rounded-md bg-[var(--color-warn-bg)] px-2 py-0.5 text-xs font-semibold text-[var(--color-warn)]">
                  Non vérifié
                </span>
              )
            }
          />
        </dl>
      </div>
      <p className="text-xs text-[var(--color-text-dim)]">
        La modification du profil (nom, mot de passe) arrivera avec les paramètres de compte complets.
      </p>
    </div>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-sm text-[var(--color-text-dim)]">{label}</dt>
      <dd className="text-sm font-medium">{value}</dd>
    </div>
  );
}
