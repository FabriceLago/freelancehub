"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getStoredToken, useAuth } from "@/lib/auth-context";
import type { OrganizationOut, ProspectOut } from "@/lib/types";

const ROLE_LABELS: Record<string, string> = { owner: "Propriétaire", admin: "Admin", member: "Membre" };
const PLAN_LABELS: Record<string, string> = { free: "Free", starter: "Starter", pro: "Pro", business: "Business" };

export default function DashboardPage() {
  const { user } = useAuth();
  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [prospects, setProspects] = useState<ProspectOut[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    Promise.all([api.myOrganization(token), api.listProspects(token)])
      .then(([orgData, prospectList]) => {
        setOrg(orgData);
        setProspects(prospectList);
      })
      .finally(() => setLoading(false));
  }, []);

  const activeProspects = prospects?.filter((p) => p.status === "contacted" || p.status === "discussing").length;

  return (
    <div className="flex flex-col gap-7">
      <div>
        <h1 className="font-display text-2xl font-bold">Bonjour, {user?.full_name.split(" ")[0]}</h1>
        <p className="mt-1 text-sm text-[var(--color-text-dim)]">
          {loading ? "Chargement de votre espace..." : org?.name}
          {org && ` · Rôle : ${ROLE_LABELS[org.role]}`}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Plan actuel" value={org ? PLAN_LABELS[org.plan] : "…"} />
        <Kpi label="Prospects actifs" value={activeProspects !== undefined ? String(activeProspects) : "…"} />
        <Kpi label="Projets en cours" value="—" note="Bientôt disponible" />
        <Kpi label="Factures impayées" value="—" note="Bientôt disponible" />
      </div>

      <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold">Prospects récents</h2>
          <Link href="/dashboard/prospects" className="text-xs font-semibold text-[var(--color-accent)]">
            Tout voir
          </Link>
        </div>
        {loading ? (
          <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>
        ) : !prospects || prospects.length === 0 ? (
          <p className="text-sm text-[var(--color-text-dim)]">
            Aucun prospect pour l&apos;instant.{" "}
            <Link href="/dashboard/prospects" className="font-medium text-[var(--color-accent)]">
              Ajoutez-en un
            </Link>
            .
          </p>
        ) : (
          <ul className="flex flex-col divide-y divide-[var(--color-line)]">
            {prospects.slice(0, 5).map((p) => (
              <li key={p.id} className="flex items-center justify-between py-2 text-sm">
                <span className="font-medium">{p.name}</span>
                <span className="text-xs text-[var(--color-text-dim)]">{p.email || p.phone || "—"}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-8 text-center">
        <p className="text-sm font-medium">Projets et factures arrivent dans une prochaine étape.</p>
        <p className="mt-1 text-xs text-[var(--color-text-dim)]">
          Prospects, compte et organisation sont pleinement fonctionnels dès maintenant.
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
