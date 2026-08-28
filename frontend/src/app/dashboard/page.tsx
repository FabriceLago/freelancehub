"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { buildActivityFeed } from "@/lib/activity";
import { getStoredToken, useAuth } from "@/lib/auth-context";
import type { ClientOut, OrganizationOut, ProspectOut } from "@/lib/types";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { EmptyWidget } from "@/components/dashboard/EmptyWidget";
import { NotificationBanner } from "@/components/dashboard/NotificationBanner";

const ROLE_LABELS: Record<string, string> = { owner: "Propriétaire", admin: "Admin", member: "Membre" };
const PLAN_LABELS: Record<string, string> = { free: "Free", starter: "Starter", pro: "Pro", business: "Business" };

export default function DashboardPage() {
  const { user } = useAuth();
  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [prospects, setProspects] = useState<ProspectOut[] | null>(null);
  const [clients, setClients] = useState<ClientOut[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    Promise.all([api.myOrganization(token), api.listProspects(token), api.listClients(token)])
      .then(([orgData, prospectList, clientList]) => {
        setOrg(orgData);
        setProspects(prospectList);
        setClients(clientList);
      })
      .finally(() => setLoading(false));
  }, []);

  const activeProspects = prospects?.filter((p) => p.status === "contacted" || p.status === "discussing").length;
  const activity = prospects && clients ? buildActivityFeed(prospects, clients) : [];

  return (
    <div className="flex flex-col gap-7">
      <div>
        <h1 className="font-display text-2xl font-bold">Bonjour, {user?.full_name.split(" ")[0]}</h1>
        <p className="mt-1 text-sm text-[var(--color-text-dim)]">
          {loading ? "Chargement de votre espace..." : org?.name}
          {org && ` · Rôle : ${ROLE_LABELS[org.role]}`}
        </p>
      </div>

      {user && !user.is_verified && (
        <NotificationBanner message="Votre email n'est pas encore vérifié — consultez votre boîte de réception." />
      )}

      <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-5">
        <KpiCard label="Plan actuel" value={org ? PLAN_LABELS[org.plan] : "…"} href="/dashboard/settings" />
        <KpiCard
          label="Prospects actifs"
          value={activeProspects !== undefined ? String(activeProspects) : "…"}
          href="/dashboard/prospects"
        />
        <KpiCard
          label="Clients"
          value={clients !== null ? String(clients.length) : "…"}
          href="/dashboard/clients"
        />
        <KpiCard label="Projets en cours" value="—" note="Bientôt disponible" />
        <KpiCard label="Factures impayées" value="—" note="Bientôt disponible" />
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1.6fr_1fr]">
        <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-6">
          <h2 className="mb-3 text-sm font-semibold">Activité récente</h2>
          {loading ? (
            <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>
          ) : (
            <ActivityFeed items={activity} />
          )}
        </div>

        <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-6">
          <h2 className="mb-3 text-sm font-semibold">Tâches</h2>
          <EmptyWidget message="La gestion des tâches arrive avec les projets." />
        </div>
      </div>

      <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-6">
        <h2 className="mb-3 text-sm font-semibold">Revenus</h2>
        <EmptyWidget message="Le suivi du chiffre d'affaires arrive avec les devis et factures." />
      </div>
    </div>
  );
}
