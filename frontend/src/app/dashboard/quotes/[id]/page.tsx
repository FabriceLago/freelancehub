"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { formatCents } from "@/lib/money";
import type { ClientOut, OrganizationOut, QuoteDetailOut } from "@/lib/types";
import { Button } from "@/components/ui/Button";

const STATUS_LABELS: Record<string, string> = {
  draft: "Brouillon",
  sent: "Envoyé",
  accepted: "Accepté",
  declined: "Refusé",
  expired: "Expiré",
};

export default function QuoteDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { notify } = useToast();
  const router = useRouter();

  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [quote, setQuote] = useState<QuoteDetailOut | null>(null);
  const [client, setClient] = useState<ClientOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const canDelete = org?.role === "owner" || org?.role === "admin";

  async function load() {
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const [orgData, quoteData, clients] = await Promise.all([
        api.myOrganization(token),
        api.getQuote(token, id),
        api.listClients(token),
      ]);
      setOrg(orgData);
      setQuote(quoteData);
      setClient(clients.find((c) => c.id === quoteData.client_id) ?? null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        notify("Devis introuvable", "error");
        router.push("/dashboard/invoices");
      } else {
        notify("Impossible de charger le devis", "error");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleTransition(status: string) {
    const token = getStoredToken();
    if (!token || !quote) return;
    setBusy(true);
    try {
      const updated = await api.transitionQuote(token, quote.id, status as QuoteDetailOut["status"]);
      setQuote({ ...quote, ...updated });
    } catch {
      notify("Transition impossible", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleConvert() {
    const token = getStoredToken();
    if (!token || !quote) return;
    setBusy(true);
    try {
      const invoice = await api.convertQuoteToInvoice(token, quote.id);
      notify("Facture créée.", "success");
      router.push(`/dashboard/invoices/${invoice.id}`);
    } catch {
      notify("Conversion impossible", "error");
      setBusy(false);
    }
  }

  async function handleDelete() {
    const token = getStoredToken();
    if (!token || !quote) return;
    setBusy(true);
    try {
      await api.deleteQuote(token, quote.id);
      notify("Devis supprimé.", "success");
      router.push("/dashboard/invoices");
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Suppression impossible", "error");
      setBusy(false);
    }
  }

  if (loading) return <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>;
  if (!quote) return null;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link href="/dashboard/invoices" className="text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-text)]">
          ← Devis & Factures
        </Link>
        <div className="mt-2 flex items-center justify-between gap-4">
          <h1 className="font-display text-2xl font-bold">{quote.number}</h1>
          <span className="rounded-md bg-[var(--color-surface-2)] px-2.5 py-1 text-xs font-semibold">
            {STATUS_LABELS[quote.status]}
          </span>
        </div>
        <p className="mt-1 text-sm text-[var(--color-text-dim)]">{client?.name ?? "—"}</p>
      </div>

      <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-6">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-[var(--color-line)] text-xs uppercase tracking-wide text-[var(--color-text-dim)]">
            <tr>
              <th className="pb-2 font-semibold">Description</th>
              <th className="pb-2 text-right font-semibold">Qté</th>
              <th className="pb-2 text-right font-semibold">Prix unit.</th>
              <th className="pb-2 text-right font-semibold">Total</th>
            </tr>
          </thead>
          <tbody>
            {quote.line_items.map((li) => (
              <tr key={li.id} className="border-b border-[var(--color-line)]">
                <td className="py-2">{li.description}</td>
                <td className="font-data py-2 text-right">{li.quantity}</td>
                <td className="font-data py-2 text-right">{formatCents(li.unit_price_cents, quote.currency)}</td>
                <td className="font-data py-2 text-right">
                  {formatCents(Math.round(parseFloat(li.quantity) * li.unit_price_cents), quote.currency)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-3 flex flex-col items-end gap-1 text-sm">
          <div className="text-[var(--color-text-dim)]">Sous-total : {formatCents(quote.subtotal_cents, quote.currency)}</div>
          <div className="text-[var(--color-text-dim)]">TVA {quote.tax_rate}%</div>
          <div className="font-data text-base font-semibold">Total : {formatCents(quote.total_cents, quote.currency)}</div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {quote.status === "draft" && (
          <Button onClick={() => handleTransition("sent")} loading={busy}>
            Envoyer
          </Button>
        )}
        {quote.status === "sent" && (
          <>
            <Button onClick={() => handleTransition("accepted")} loading={busy}>
              Marquer accepté
            </Button>
            <Button variant="secondary" onClick={() => handleTransition("declined")} loading={busy}>
              Marquer refusé
            </Button>
          </>
        )}
        {quote.status === "accepted" && (
          <Button onClick={handleConvert} loading={busy}>
            Convertir en facture
          </Button>
        )}
        {quote.status === "draft" && canDelete && (
          <button
            onClick={handleDelete}
            disabled={busy}
            className="ml-auto text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-danger)] disabled:opacity-60"
          >
            Supprimer ce devis
          </button>
        )}
      </div>
    </div>
  );
}
