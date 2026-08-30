"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ApiError, api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { formatCents } from "@/lib/money";
import type { OrganizationOut, PlanCode, PlanOut } from "@/lib/types";
import { Button } from "@/components/ui/Button";

const ROLE_LABELS: Record<string, string> = { owner: "Propriétaire", admin: "Admin", member: "Membre" };
const PLAN_LABELS: Record<string, string> = { free: "Free", starter: "Starter", pro: "Pro", business: "Business" };
const STATUS_LABELS: Record<string, string> = {
  trialing: "Essai",
  active: "Actif",
  past_due: "Paiement en retard",
  canceled: "Annulé",
  incomplete: "Incomplet",
};
const STATUS_CLASS: Record<string, string> = {
  trialing: "bg-[var(--color-warn-bg)] text-[var(--color-warn)]",
  active: "bg-[var(--color-ok-bg)] text-[var(--color-ok)]",
  past_due: "bg-[var(--color-danger-bg)] text-[var(--color-danger)]",
  canceled: "bg-[var(--color-surface-2)] text-[var(--color-text-dim)]",
  incomplete: "bg-[var(--color-warn-bg)] text-[var(--color-warn)]",
};

export default function SettingsPage() {
  const { notify } = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [plans, setPlans] = useState<PlanOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [billingBusy, setBillingBusy] = useState<string | null>(null);

  const canManageBilling = org?.role === "owner" || org?.role === "admin";

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    Promise.all([api.myOrganization(token), api.listBillingPlans(token)])
      .then(([orgData, planList]) => {
        setOrg(orgData);
        setPlans(planList);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const checkout = searchParams.get("checkout");
    if (checkout === "success") {
      notify("Abonnement en cours d'activation — quelques secondes le temps que Stripe confirme.", "success");
      router.replace("/dashboard/settings");
    } else if (checkout === "cancelled") {
      notify("Paiement annulé.", "info");
      router.replace("/dashboard/settings");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  async function handleUpgrade(planCode: PlanCode) {
    const token = getStoredToken();
    if (!token) return;
    setBillingBusy(planCode);
    try {
      const { url } = await api.createCheckoutSession(token, planCode);
      window.location.assign(url);
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        notify("Paiement non configuré pour l'instant", "error");
      } else if (err instanceof ApiError && err.status === 400) {
        notify("Ce plan n'est pas encore disponible à l'achat", "error");
      } else {
        notify("Impossible de démarrer le paiement", "error");
      }
      setBillingBusy(null);
    }
  }

  async function handleManageBilling() {
    const token = getStoredToken();
    if (!token) return;
    setBillingBusy("portal");
    try {
      const { url } = await api.createPortalSession(token);
      window.location.assign(url);
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        notify("Paiement non configuré pour l'instant", "error");
      } else {
        notify("Impossible d'ouvrir le portail de facturation", "error");
      }
      setBillingBusy(null);
    }
  }

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
            <span
              className={`rounded-md px-2 py-0.5 text-xs font-semibold ${STATUS_CLASS[org.subscription_status]}`}
            >
              {STATUS_LABELS[org.subscription_status]}
            </span>
          </div>
        )}

        {!canManageBilling && (
          <p className="mt-3 text-xs text-[var(--color-text-dim)]">
            Seul le propriétaire ou un admin peut gérer l&apos;abonnement.
          </p>
        )}

        {canManageBilling && org && org.plan !== "free" && (
          <Button className="mt-4 w-full" variant="secondary" onClick={handleManageBilling} loading={billingBusy === "portal"}>
            Gérer mon abonnement
          </Button>
        )}

        {canManageBilling && org && org.plan === "free" && (
          <div className="mt-4 flex flex-col gap-2">
            {plans
              .filter((p) => p.code !== "free")
              .map((p) => (
                <button
                  key={p.code}
                  onClick={() => handleUpgrade(p.code)}
                  disabled={billingBusy !== null}
                  className="flex items-center justify-between rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3 py-2.5 text-sm hover:border-[var(--color-accent)] disabled:opacity-60"
                >
                  <span className="font-medium">{p.name}</span>
                  <span className="font-data text-[var(--color-text-dim)]">
                    {formatCents(p.price_cents)}/mois {billingBusy === p.code && "…"}
                  </span>
                </button>
              ))}
          </div>
        )}
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
