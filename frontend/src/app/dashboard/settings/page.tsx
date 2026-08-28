"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import type { OrganizationOut } from "@/lib/types";

const ROLE_LABELS: Record<string, string> = { owner: "Propriétaire", admin: "Admin", member: "Membre" };
const PLAN_LABELS: Record<string, string> = { free: "Free", starter: "Starter", pro: "Pro", business: "Business" };

export default function SettingsPage() {
  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    api
      .myOrganization(token)
      .then(setOrg)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-2xl font-bold">Paramètres</h1>

      <section className="max-w-md rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-5">
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-[var(--color-text-dim)]">
          Organisation
        </h2>
        {loading ? (
          <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>
        ) : org ? (
          <dl className="flex flex-col gap-3">
            <Row label="Nom" value={org.name} />
            <Row label="Devise" value={org.currency} />
            <Row label="Votre rôle" value={ROLE_LABELS[org.role]} />
          </dl>
        ) : (
          <p className="text-sm text-[var(--color-danger)]">Impossible de charger l&apos;organisation.</p>
        )}
      </section>

      <section className="max-w-md rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-5">
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-[var(--color-text-dim)]">
          Abonnement
        </h2>
        {org && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Plan {PLAN_LABELS[org.plan]}</span>
            <span className="rounded-md bg-[var(--color-ok-bg)] px-2 py-0.5 text-xs font-semibold text-[var(--color-ok)]">
              Actif
            </span>
          </div>
        )}
        <p className="mt-3 text-xs text-[var(--color-text-dim)]">
          Le changement de plan et la facturation Stripe seront disponibles une fois l&apos;intégration Stripe branchée.
        </p>
      </section>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-sm text-[var(--color-text-dim)]">{label}</dt>
      <dd className="text-sm font-medium">{value}</dd>
    </div>
  );
}
