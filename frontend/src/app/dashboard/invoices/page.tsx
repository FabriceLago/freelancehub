"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { formatCents } from "@/lib/money";
import type { ClientOut, InvoiceOut, LineItemInput, QuoteOut } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { LineItemsEditor } from "@/components/ui/LineItemsEditor";

const QUOTE_STATUS_LABELS: Record<string, string> = {
  draft: "Brouillon",
  sent: "Envoyé",
  accepted: "Accepté",
  declined: "Refusé",
  expired: "Expiré",
};
const QUOTE_STATUS_CLASS: Record<string, string> = {
  draft: "bg-[var(--color-surface-2)] text-[var(--color-text-dim)]",
  sent: "bg-[var(--color-warn-bg)] text-[var(--color-warn)]",
  accepted: "bg-[var(--color-ok-bg)] text-[var(--color-ok)]",
  declined: "bg-[var(--color-danger-bg)] text-[var(--color-danger)]",
  expired: "bg-[var(--color-danger-bg)] text-[var(--color-danger)]",
};

const INVOICE_STATUS_LABELS: Record<string, string> = {
  draft: "Brouillon",
  sent: "Envoyée",
  paid: "Payée",
  overdue: "En retard",
  cancelled: "Annulée",
};
const INVOICE_STATUS_CLASS: Record<string, string> = {
  draft: "bg-[var(--color-surface-2)] text-[var(--color-text-dim)]",
  sent: "bg-[var(--color-warn-bg)] text-[var(--color-warn)]",
  paid: "bg-[var(--color-ok-bg)] text-[var(--color-ok)]",
  overdue: "bg-[var(--color-danger-bg)] text-[var(--color-danger)]",
  cancelled: "bg-[var(--color-surface-2)] text-[var(--color-text-dim)]",
};

export default function InvoicesPage() {
  const { notify } = useToast();
  const [tab, setTab] = useState<"quotes" | "invoices">("quotes");
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [quotes, setQuotes] = useState<QuoteOut[]>([]);
  const [invoices, setInvoices] = useState<InvoiceOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<"quote" | "invoice" | null>(null);

  async function load() {
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const [clientList, quoteList, invoiceList] = await Promise.all([
        api.listClients(token),
        api.listQuotes(token),
        api.listInvoices(token),
      ]);
      setClients(clientList);
      setQuotes(quoteList);
      setInvoices(invoiceList);
    } catch {
      notify("Impossible de charger les devis et factures", "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, []);

  const clientName = (id: string) => clients.find((c) => c.id === id)?.name ?? "—";

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-display text-2xl font-bold">Devis & Factures</h1>
        <Button onClick={() => setModal(tab === "quotes" ? "quote" : "invoice")} disabled={clients.length === 0}>
          + Nouveau {tab === "quotes" ? "devis" : "facture"}
        </Button>
      </div>

      {clients.length === 0 && !loading && (
        <p className="text-xs text-[var(--color-text-dim)]">
          Ajoutez d&apos;abord un{" "}
          <Link href="/dashboard/clients" className="font-medium text-[var(--color-accent)]">
            client
          </Link>{" "}
          pour pouvoir créer un devis ou une facture.
        </p>
      )}

      <div className="flex gap-2 border-b border-[var(--color-line)] pb-3">
        <button
          onClick={() => setTab("quotes")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${tab === "quotes" ? "bg-[var(--color-surface-2)] text-[var(--color-text)]" : "text-[var(--color-text-dim)] hover:text-[var(--color-text)]"}`}
        >
          Devis
        </button>
        <button
          onClick={() => setTab("invoices")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${tab === "invoices" ? "bg-[var(--color-surface-2)] text-[var(--color-text)]" : "text-[var(--color-text-dim)] hover:text-[var(--color-text)]"}`}
        >
          Factures
        </button>
      </div>

      {loading ? (
        <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>
      ) : tab === "quotes" ? (
        quotes.length === 0 ? (
          <EmptyState label="devis" />
        ) : (
          <div className="overflow-x-auto rounded-lg border border-[var(--color-line)]">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="border-b border-[var(--color-line)] bg-[var(--color-surface-2)] text-xs uppercase tracking-wide text-[var(--color-text-dim)]">
                <tr>
                  <th className="px-4 py-3 font-semibold">Numéro</th>
                  <th className="px-4 py-3 font-semibold">Client</th>
                  <th className="px-4 py-3 font-semibold">Statut</th>
                  <th className="px-4 py-3 font-semibold">Total</th>
                </tr>
              </thead>
              <tbody>
                {quotes.map((q) => (
                  <tr key={q.id} className="border-b border-[var(--color-line)] last:border-0">
                    <td className="px-4 py-3">
                      <Link href={`/dashboard/quotes/${q.id}`} className="font-data font-medium hover:text-[var(--color-accent)]">
                        {q.number}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-[var(--color-text-dim)]">{clientName(q.client_id)}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold ${QUOTE_STATUS_CLASS[q.status]}`}>
                        {QUOTE_STATUS_LABELS[q.status]}
                      </span>
                    </td>
                    <td className="font-data px-4 py-3">{formatCents(q.total_cents, q.currency)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : invoices.length === 0 ? (
        <EmptyState label="facture" />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-[var(--color-line)]">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-[var(--color-line)] bg-[var(--color-surface-2)] text-xs uppercase tracking-wide text-[var(--color-text-dim)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Numéro</th>
                <th className="px-4 py-3 font-semibold">Client</th>
                <th className="px-4 py-3 font-semibold">Statut</th>
                <th className="px-4 py-3 font-semibold">Total</th>
                <th className="px-4 py-3 font-semibold">Solde dû</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id} className="border-b border-[var(--color-line)] last:border-0">
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/invoices/${inv.id}`} className="font-data font-medium hover:text-[var(--color-accent)]">
                      {inv.number}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-[var(--color-text-dim)]">{clientName(inv.client_id)}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold ${INVOICE_STATUS_CLASS[inv.status]}`}>
                      {INVOICE_STATUS_LABELS[inv.status]}
                    </span>
                  </td>
                  <td className="font-data px-4 py-3">{formatCents(inv.total_cents, inv.currency)}</td>
                  <td className="font-data px-4 py-3 text-[var(--color-text-dim)]">
                    {inv.balance_cents > 0 ? formatCents(inv.balance_cents, inv.currency) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal === "quote" && (
        <NewQuoteModal
          clients={clients}
          onClose={() => setModal(null)}
          onCreated={(q) => {
            setQuotes((prev) => [q, ...prev]);
            setModal(null);
          }}
        />
      )}

      {modal === "invoice" && (
        <NewInvoiceModal
          clients={clients}
          onClose={() => setModal(null)}
          onCreated={(inv) => {
            setInvoices((prev) => [inv, ...prev]);
            setModal(null);
          }}
        />
      )}
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-10 text-center">
      <p className="text-sm font-medium">Aucun {label} pour l&apos;instant</p>
    </div>
  );
}

function NewQuoteModal({
  clients,
  onClose,
  onCreated,
}: {
  clients: ClientOut[];
  onClose: () => void;
  onCreated: (q: QuoteOut) => void;
}) {
  const { notify } = useToast();
  const [clientId, setClientId] = useState(clients[0]?.id ?? "");
  const [taxRate, setTaxRate] = useState("0");
  const [lineItems, setLineItems] = useState<LineItemInput[]>([]);
  const [loading, setLoading] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [draftSeed, setDraftSeed] = useState<{ key: number; items: LineItemInput[] } | null>(null);

  async function handleGenerateDraft() {
    if (!aiPrompt.trim()) {
      notify("Décrivez brièvement le projet", "error");
      return;
    }
    const token = getStoredToken();
    if (!token) return;
    setAiLoading(true);
    try {
      const draft = await api.generateQuoteDraft(token, clientId, aiPrompt);
      const items: LineItemInput[] = draft.line_items.map((li) => ({
        description: li.description,
        quantity: String(li.quantity),
        unit_price_cents: li.unit_price_cents,
      }));
      setDraftSeed((prev) => ({ key: (prev?.key ?? 0) + 1, items }));
      setLineItems(items);
      setTaxRate(String(draft.suggested_tax_rate));
      notify("Brouillon généré — relisez avant de créer le devis.", "success");
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        notify("Quota IA atteint pour votre plan ce mois-ci", "error");
      } else if (err instanceof ApiError && err.status === 503) {
        notify("Assistant IA non configuré", "error");
      } else {
        notify("Impossible de générer le brouillon", "error");
      }
    } finally {
      setAiLoading(false);
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (lineItems.length === 0) {
      notify("Ajoutez au moins une ligne", "error");
      return;
    }
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const quote = await api.createQuote(token, { client_id: clientId, tax_rate: taxRate, line_items: lineItems });
      onCreated(quote);
      notify("Devis créé.", "success");
    } catch {
      notify("Impossible de créer le devis", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal title="Nouveau devis" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="client_id" className="text-sm font-medium">
            Client
          </label>
          <select
            id="client_id"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3.5 py-2.5 text-sm"
          >
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="rounded-md border border-dashed border-[var(--color-line)] p-3">
          <label htmlFor="ai_prompt" className="mb-1.5 block text-xs font-medium text-[var(--color-text-dim)]">
            Assistant IA — décrivez le projet en une phrase
          </label>
          <div className="flex gap-2">
            <input
              id="ai_prompt"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="ex : Site vitrine 5 pages pour un restaurant"
              className="flex-1 rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3 py-2 text-sm outline-none focus:border-[var(--color-accent)]"
            />
            <Button type="button" variant="secondary" onClick={handleGenerateDraft} loading={aiLoading}>
              Générer
            </Button>
          </div>
        </div>

        <LineItemsEditor
          key={draftSeed?.key ?? 0}
          initialItems={draftSeed?.items}
          taxRate={taxRate}
          onTaxRateChange={setTaxRate}
          onChange={setLineItems}
        />

        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Annuler
          </Button>
          <Button type="submit" loading={loading}>
            Créer
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function NewInvoiceModal({
  clients,
  onClose,
  onCreated,
}: {
  clients: ClientOut[];
  onClose: () => void;
  onCreated: (inv: InvoiceOut) => void;
}) {
  const { notify } = useToast();
  const [clientId, setClientId] = useState(clients[0]?.id ?? "");
  const [taxRate, setTaxRate] = useState("0");
  const [dueDate, setDueDate] = useState("");
  const [lineItems, setLineItems] = useState<LineItemInput[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (lineItems.length === 0) {
      notify("Ajoutez au moins une ligne", "error");
      return;
    }
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const invoice = await api.createInvoice(token, {
        client_id: clientId,
        tax_rate: taxRate,
        due_date: dueDate || undefined,
        line_items: lineItems,
      });
      onCreated(invoice);
      notify("Facture créée.", "success");
    } catch {
      notify("Impossible de créer la facture", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal title="Nouvelle facture" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="inv_client_id" className="text-sm font-medium">
            Client
          </label>
          <select
            id="inv_client_id"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3.5 py-2.5 text-sm"
          >
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="due_date" className="text-sm font-medium">
            Échéance
          </label>
          <input
            id="due_date"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3.5 py-2.5 text-sm"
          />
        </div>

        <LineItemsEditor taxRate={taxRate} onTaxRateChange={setTaxRate} onChange={setLineItems} />

        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Annuler
          </Button>
          <Button type="submit" loading={loading}>
            Créer
          </Button>
        </div>
      </form>
    </Modal>
  );
}
