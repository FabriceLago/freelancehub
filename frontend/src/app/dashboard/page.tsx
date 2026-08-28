"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getStoredToken, useAuth } from "@/lib/auth-context";
import type { OrganizationOut } from "@/lib/types";

const ROLE_LABELS: Record<string, string> = { owner: "Propriétaire", admin: "Admin", member: "Membre" };
const PLAN_LABELS: Record<string, string> = { free: "Free", starter: "Starter", pro: "Pro", business: "Business" };

export default function DashboardPage() {
  const { user } = useAuth();
  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [orgLoading, setOrgLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    api
      .myOrganization(token)
      .then(setOrg)
      .finally(() => setOrgLoading(false));
  }, []);

  return (
    <div className="flex flex-col gap-7">
      <div>
        <h1 className="font-display text-2xl font-bold">Bonjour, {user?.full_name.split(" ")[0]}</h1>
        <p className="mt-1 text-sm text-[var(--color-text-dim)]">
          {orgLoading ? "Chargement de votre espace..." : org?.name}
          {org && ` · Rôle : ${ROLE_LABELS[org.role]}`}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Plan actuel" value={org ? PLAN_LABELS[org.plan] : "…"} />
        <Kpi label="Prospects actifs" value="—" note="Bientôt disponible" />
        <Kpi label="Projets en cours" value="—" note="Bientôt disponible" />
        <Kpi label="Factures impayées" value="—" note="Bientôt disponible" />
      </div>

      <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-8 text-center">
        <p className="text-sm font-medium">La gestion des prospects, projets et factures arrive dans la prochaine étape.</p>
        <p className="mt-1 text-xs text-[var(--color-text-dim)]">
          Le compte, l&apos;organisation et l&apos;authentification sont pleinement fonctionnels dès maintenant.
        </p>
      </div>
    </div>
  );
}

function Kpi({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] px-4 py-3.5">
      <div className="text-xs text-[var(--color-text-dim)]">{label}</div>
      <div className="font-data mt-1 text-2xl">{value}</div>
      {note && <div className="mt-1 text-[11px] text-[var(--color-text-dim)]">{note}</div>}
    </div>
  );
}
