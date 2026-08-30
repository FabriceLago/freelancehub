"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { formatCents } from "@/lib/money";
import type { ClientOut, InvoiceDetailOut, OrganizationOut, ReminderDraftResponse } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";

const STATUS_LABELS: Record<string, string> = {
  draft: "Brouillon",
  sent: "Envoyée",
  paid: "Payée",
  overdue: "En retard",
  cancelled: "Annulée",
};

export default function InvoiceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { notify } = useToast();
  const router = useRouter();

  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [invoice, setInvoice] = useState<InvoiceDetailOut | null>(null);
  const [client, setClient] = useState<ClientOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [reminderDraft, setReminderDraft] = useState<ReminderDraftResponse | null>(null);
  const [reminderLoading, setReminderLoading] = useState(false);

  const canDelete = org?.role === "owner" || org?.role === "admin";

  async function load() {
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const [orgData, invoiceData, clients] = await Promise.all([
        api.myOrganization(token),
        api.getInvoice(token, id),
        api.listClients(token),
      ]);
      setOrg(orgData);
      setInvoice(invoiceData);
      setClient(clients.find((c) => c.id === invoiceData.client_id) ?? null);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        notify("Facture introuvable", "error");
        router.push("/dashboard/invoices");
      } else {
        notify("Impossible de charger la facture", "error");
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
    if (!token || !invoice) return;
    setBusy(true);
    try {
      const updated = await api.transitionInvoice(token, invoice.id, status as InvoiceDetailOut["status"]);
      setInvoice({ ...invoice, ...updated });
    } catch {
      notify("Transition impossible", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleMarkPaid() {
    const token = getStoredToken();
    if (!token || !invoice) return;
    setBusy(true);
    try {
      await api.markInvoicePaid(token, invoice.id);
      const refreshed = await api.getInvoice(token, invoice.id);
      setInvoice(refreshed);
      notify("Facture marquée payée.", "success");
    } catch {
      notify("Impossible de marquer la facture payée", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleGenerateReminder() {
    const token = getStoredToken();
    if (!token || !invoice) return;
    setReminderLoading(true);
    try {
      const draft = await api.generateReminderDraft(token, invoice.id);
      setReminderDraft(draft);
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        notify("Quota IA atteint pour votre plan ce mois-ci", "error");
      } else if (err instanceof ApiError && err.status === 503) {
        notify("Assistant IA non configuré", "error");
      } else {
        notify("Impossible de générer la relance", "error");
      }
    } finally {
      setReminderLoading(false);
    }
  }

  async function handleDelete() {
    const token = getStoredToken();
    if (!token || !invoice) return;
    setBusy(true);
    try {
      await api.deleteInvoice(token, invoice.id);
      notify("Facture supprimée.", "success");
      router.push("/dashboard/invoices");
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Suppression impossible", "error");
      setBusy(false);
    }
  }

  if (loading) return <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>;
  if (!invoice) return null;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link href="/dashboard/invoices" className="text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-text)]">
          ← Devis & Factures
        </Link>
        <div className="mt-2 flex items-center justify-between gap-4">
          <h1 className="font-display text-2xl font-bold">{invoice.number}</h1>
          <span className="rounded-md bg-[var(--color-surface-2)] px-2.5 py-1 text-xs font-semibold">
            {STATUS_LABELS[invoice.status]}
          </span>
        </div>
        <p className="mt-1 text-sm text-[var(--color-text-dim)]">
          {client?.name ?? "—"}
          {invoice.due_date && ` · Échéance : ${invoice.due_date}`}
        </p>
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
            {invoice.line_items.map((li) => (
              <tr key={li.id} className="border-b border-[var(--color-line)]">
                <td className="py-2">{li.description}</td>
                <td className="font-data py-2 text-right">{li.quantity}</td>
                <td className="font-data py-2 text-right">{formatCents(li.unit_price_cents, invoice.currency)}</td>
                <td className="font-data py-2 text-right">
                  {formatCents(Math.round(parseFloat(li.quantity) * li.unit_price_cents), invoice.currency)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-3 flex flex-col items-end gap-1 text-sm">
          <div className="text-[var(--color-text-dim)]">Sous-total : {formatCents(invoice.subtotal_cents, invoice.currency)}</div>
          <div className="text-[var(--color-text-dim)]">TVA {invoice.tax_rate}%</div>
          <div className="font-data text-base font-semibold">Total : {formatCents(invoice.total_cents, invoice.currency)}</div>
          {invoice.paid_cents > 0 && (
            <div className="font-data text-[var(--color-ok)]">Payé : {formatCents(invoice.paid_cents, invoice.currency)}</div>
          )}
          {invoice.balance_cents > 0 && (
            <div className="font-data font-semibold text-[var(--color-danger)]">
              Solde dû : {formatCents(invoice.balance_cents, invoice.currency)}
            </div>
          )}
        </div>
      </div>

      {invoice.payments.length > 0 && (
        <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-6">
          <h2 className="mb-3 text-sm font-semibold">Paiements</h2>
          <ul className="flex flex-col divide-y divide-[var(--color-line)]">
            {invoice.payments.map((p) => (
              <li key={p.id} className="flex items-center justify-between py-2 text-sm">
                <span className="text-[var(--color-text-dim)]">
                  {p.method} · {new Date(p.paid_at).toLocaleDateString("fr-FR")}
                </span>
                <span className="font-data font-medium">{formatCents(p.amount_cents, invoice.currency)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
        {invoice.status === "draft" && (
          <Button onClick={() => handleTransition("sent")} loading={busy}>
            Envoyer
          </Button>
        )}
        {(invoice.status === "draft" || invoice.status === "sent") && (
          <Button onClick={handleMarkPaid} loading={busy}>
            Marquer payée
          </Button>
        )}
        {invoice.status === "sent" && (
          <Button variant="secondary" onClick={() => handleTransition("cancelled")} loading={busy}>
            Annuler
          </Button>
        )}
        {(invoice.status === "sent" || invoice.status === "overdue") && (
          <Button variant="secondary" onClick={handleGenerateReminder} loading={reminderLoading}>
            Générer une relance (IA)
          </Button>
        )}
        {invoice.status === "draft" && canDelete && (
          <button
            onClick={handleDelete}
            disabled={busy}
            className="ml-auto text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-danger)] disabled:opacity-60"
          >
            Supprimer cette facture
          </button>
        )}
      </div>

      {reminderDraft && (
        <Modal title="Relance générée par l'IA" onClose={() => setReminderDraft(null)}>
          <div className="flex flex-col gap-3">
            <div>
              <div className="mb-1 text-xs font-medium text-[var(--color-text-dim)]">Objet</div>
              <div className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface-2)] px-3 py-2 text-sm">
                {reminderDraft.subject}
              </div>
            </div>
            <div>
              <div className="mb-1 text-xs font-medium text-[var(--color-text-dim)]">Message</div>
              <div className="whitespace-pre-wrap rounded-md border border-[var(--color-line)] bg-[var(--color-surface-2)] px-3 py-2 text-sm">
                {reminderDraft.body}
              </div>
            </div>
            <p className="text-xs text-[var(--color-text-dim)]">
              Relisez avant d&apos;envoyer — copiez ce texte dans votre client email habituel.
            </p>
          </div>
        </Modal>
      )}
    </div>
  );
}
