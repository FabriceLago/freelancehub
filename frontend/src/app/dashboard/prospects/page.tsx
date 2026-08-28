"use client";

import { FormEvent, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import type { OrganizationOut, ProspectOut, ProspectStatus } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";
import { StatusBadge } from "@/components/ui/StatusBadge";

const STATUS_OPTIONS: { value: ProspectStatus; label: string }[] = [
  { value: "contacted", label: "Contacté" },
  { value: "discussing", label: "En discussion" },
  { value: "lost", label: "Perdu" },
];

const FILTERS: { value: ProspectStatus | "all"; label: string }[] = [
  { value: "all", label: "Tous" },
  { value: "contacted", label: "Contacté" },
  { value: "discussing", label: "En discussion" },
  { value: "converted", label: "Converti" },
  { value: "lost", label: "Perdu" },
];

export default function ProspectsPage() {
  const { notify } = useToast();
  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [prospects, setProspects] = useState<ProspectOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<ProspectStatus | "all">("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);

  const canDelete = org?.role === "owner" || org?.role === "admin";

  async function load() {
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const [orgData, list] = await Promise.all([
        api.myOrganization(token),
        api.listProspects(token, filter === "all" ? undefined : filter),
      ]);
      setOrg(orgData);
      setProspects(list);
    } catch {
      notify("Impossible de charger les prospects", "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // `load` est redéfinie à chaque render (elle dépend de `filter`), donc
    // l'appeler directement ici est le comportement voulu à chaque changement
    // de filtre — pas un cas d'oubli de dépendance.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [filter]);

  async function handleStatusChange(id: string, status: ProspectStatus) {
    const token = getStoredToken();
    if (!token) return;
    setBusyId(id);
    try {
      const updated = await api.updateProspect(token, id, { status });
      setProspects((prev) => prev.map((p) => (p.id === id ? updated : p)));
    } catch {
      notify("Impossible de changer le statut", "error");
    } finally {
      setBusyId(null);
    }
  }

  async function handleConvert(id: string) {
    const token = getStoredToken();
    if (!token) return;
    setBusyId(id);
    try {
      const client = await api.convertProspect(token, id);
      notify(`${client.name} converti en client.`, "success");
      load();
    } catch {
      notify("Impossible de convertir ce prospect", "error");
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(id: string) {
    const token = getStoredToken();
    if (!token) return;
    setBusyId(id);
    try {
      await api.deleteProspect(token, id);
      setProspects((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Impossible de supprimer ce prospect", "error");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-display text-2xl font-bold">Prospects</h1>
        <Button onClick={() => setModalOpen(true)}>+ Nouveau prospect</Button>
      </div>

      <div className="flex gap-2 border-b border-[var(--color-line)] pb-3">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              filter === f.value
                ? "bg-[var(--color-surface-2)] text-[var(--color-text)]"
                : "text-[var(--color-text-dim)] hover:text-[var(--color-text)]"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>
      ) : prospects.length === 0 ? (
        <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-10 text-center">
          <p className="text-sm font-medium">Aucun prospect pour l&apos;instant</p>
          <p className="mt-1 text-xs text-[var(--color-text-dim)]">
            Ajoutez votre premier prospect pour démarrer votre pipeline commercial.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-[var(--color-line)]">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-[var(--color-line)] bg-[var(--color-surface-2)] text-xs uppercase tracking-wide text-[var(--color-text-dim)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Nom</th>
                <th className="px-4 py-3 font-semibold">Contact</th>
                <th className="px-4 py-3 font-semibold">Statut</th>
                <th className="px-4 py-3 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {prospects.map((p) => (
                <tr key={p.id} className="border-b border-[var(--color-line)] last:border-0">
                  <td className="px-4 py-3 font-medium">{p.name}</td>
                  <td className="px-4 py-3 text-[var(--color-text-dim)]">{p.email || p.phone || "—"}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={p.status} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {p.status !== "converted" && (
                        <>
                          <select
                            value={p.status}
                            disabled={busyId === p.id}
                            onChange={(e) => handleStatusChange(p.id, e.target.value as ProspectStatus)}
                            className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-2 py-1 text-xs disabled:opacity-60"
                          >
                            {STATUS_OPTIONS.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                          <button
                            onClick={() => handleConvert(p.id)}
                            disabled={busyId === p.id}
                            className="text-xs font-semibold text-[var(--color-accent)] disabled:opacity-60"
                          >
                            Convertir
                          </button>
                        </>
                      )}
                      {canDelete && (
                        <button
                          onClick={() => handleDelete(p.id)}
                          disabled={busyId === p.id}
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

      {modalOpen && (
        <NewProspectModal
          onClose={() => setModalOpen(false)}
          onCreated={(p) => {
            setProspects((prev) => [p, ...prev]);
            setModalOpen(false);
          }}
        />
      )}
    </div>
  );
}

function NewProspectModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: (p: ProspectOut) => void;
}) {
  const { notify } = useToast();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [source, setSource] = useState("");
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
    try {
      const prospect = await api.createProspect(token, {
        name,
        email: email || undefined,
        phone: phone || undefined,
        source: source || undefined,
      });
      onCreated(prospect);
      notify("Prospect ajouté.", "success");
    } catch {
      notify("Impossible de créer le prospect", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal title="Nouveau prospect" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <Field label="Nom" name="name" value={name} onChange={(e) => setName(e.target.value)} error={errors.name} />
        <Field label="Email" name="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Field label="Téléphone" name="phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <Field
          label="Source"
          name="source"
          placeholder="ex : formulaire, recommandation"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        />
        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Annuler
          </Button>
          <Button type="submit" loading={loading}>
            Ajouter
          </Button>
        </div>
      </form>
    </Modal>
  );
}
