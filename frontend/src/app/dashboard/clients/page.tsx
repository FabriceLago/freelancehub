"use client";

import { FormEvent, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import type { ClientOut, OrganizationOut } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";

export default function ClientsPage() {
  const { notify } = useToast();
  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [editing, setEditing] = useState<ClientOut | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const canDelete = org?.role === "owner" || org?.role === "admin";

  async function load() {
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const [orgData, list] = await Promise.all([api.myOrganization(token), api.listClients(token)]);
      setOrg(orgData);
      setClients(list);
    } catch {
      notify("Impossible de charger les clients", "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleDelete(id: string) {
    const token = getStoredToken();
    if (!token) return;
    setBusyId(id);
    try {
      await api.deleteClient(token, id);
      setClients((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Impossible de supprimer ce client", "error");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-display text-2xl font-bold">Clients</h1>
        <Button onClick={() => setCreateOpen(true)}>+ Nouveau client</Button>
      </div>

      {loading ? (
        <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>
      ) : clients.length === 0 ? (
        <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-10 text-center">
          <p className="text-sm font-medium">Aucun client pour l&apos;instant</p>
          <p className="mt-1 text-xs text-[var(--color-text-dim)]">
            Ajoutez-en un directement, ou convertissez un prospect.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-[var(--color-line)]">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-[var(--color-line)] bg-[var(--color-surface-2)] text-xs uppercase tracking-wide text-[var(--color-text-dim)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Nom</th>
                <th className="px-4 py-3 font-semibold">Contact</th>
                <th className="px-4 py-3 font-semibold">Origine</th>
                <th className="px-4 py-3 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((c) => (
                <tr key={c.id} className="border-b border-[var(--color-line)] last:border-0">
                  <td className="px-4 py-3">
                    <div className="font-medium">{c.name}</div>
                    {c.company && <div className="text-xs text-[var(--color-text-dim)]">{c.company}</div>}
                  </td>
                  <td className="px-4 py-3 text-[var(--color-text-dim)]">{c.email || c.phone || "—"}</td>
                  <td className="px-4 py-3 text-[var(--color-text-dim)]">
                    {c.converted_from_prospect_id ? "Prospect converti" : "Ajouté directement"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => setEditing(c)}
                        disabled={busyId === c.id}
                        className="text-xs font-semibold text-[var(--color-accent)] disabled:opacity-60"
                      >
                        Modifier
                      </button>
                      {canDelete && (
                        <button
                          onClick={() => handleDelete(c.id)}
                          disabled={busyId === c.id}
                          className="text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-danger)] disabled:opacity-60"
                        >
                          Supprimer
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {createOpen && (
        <ClientFormModal
          title="Nouveau client"
          onClose={() => setCreateOpen(false)}
          onSaved={(c) => {
            setClients((prev) => [c, ...prev]);
            setCreateOpen(false);
          }}
        />
      )}

      {editing && (
        <ClientFormModal
          title="Modifier le client"
          client={editing}
          onClose={() => setEditing(null)}
          onSaved={(c) => {
            setClients((prev) => prev.map((x) => (x.id === c.id ? c : x)));
            setEditing(null);
          }}
        />
      )}
    </div>
  );
}

function ClientFormModal({
  title,
  client,
  onClose,
  onSaved,
}: {
  title: string;
  client?: ClientOut;
  onClose: () => void;
  onSaved: (c: ClientOut) => void;
}) {
  const { notify } = useToast();
  const [name, setName] = useState(client?.name ?? "");
  const [company, setCompany] = useState(client?.company ?? "");
  const [email, setEmail] = useState(client?.email ?? "");
  const [phone, setPhone] = useState(client?.phone ?? "");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setErrors({ name: "Le nom est requis" });
      return;
    }
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    const payload = {
      name,
      company: company || undefined,
      email: email || undefined,
      phone: phone || undefined,
    };
    try {
      const saved = client
        ? await api.updateClient(token, client.id, payload)
        : await api.createClient(token, payload);
      onSaved(saved);
      notify(client ? "Client mis à jour." : "Client ajouté.", "success");
    } catch {
      notify("Impossible d'enregistrer le client", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal title={title} onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <Field label="Nom" name="name" value={name} onChange={(e) => setName(e.target.value)} error={errors.name} />
        <Field label="Société" name="company" value={company} onChange={(e) => setCompany(e.target.value)} />
        <Field label="Email" name="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Field label="Téléphone" name="phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Annuler
          </Button>
          <Button type="submit" loading={loading}>
            {client ? "Enregistrer" : "Ajouter"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
