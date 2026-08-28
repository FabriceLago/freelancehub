"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import type { ClientOut, ProjectOut, ProjectStatus } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Modal } from "@/components/ui/Modal";

const STATUS_LABELS: Record<ProjectStatus, string> = {
  active: "Actif",
  completed: "Terminé",
  archived: "Archivé",
};

const STATUS_CLASS: Record<ProjectStatus, string> = {
  active: "bg-[var(--color-ok-bg)] text-[var(--color-ok)]",
  completed: "bg-[var(--color-surface-2)] text-[var(--color-text-dim)]",
  archived: "bg-[var(--color-warn-bg)] text-[var(--color-warn)]",
};

const FILTERS: { value: ProjectStatus | "all"; label: string }[] = [
  { value: "all", label: "Tous" },
  { value: "active", label: "Actif" },
  { value: "completed", label: "Terminé" },
  { value: "archived", label: "Archivé" },
];

export default function ProjectsPage() {
  const { notify } = useToast();
  const [projects, setProjects] = useState<ProjectOut[]>([]);
  const [clients, setClients] = useState<ClientOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<ProjectStatus | "all">("all");
  const [modalOpen, setModalOpen] = useState(false);

  async function load() {
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const [projectList, clientList] = await Promise.all([
        api.listProjects(token, filter === "all" ? undefined : filter),
        api.listClients(token),
      ]);
      setProjects(projectList);
      setClients(clientList);
    } catch {
      notify("Impossible de charger les projets", "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const clientName = (id: string) => clients.find((c) => c.id === id)?.name ?? "—";

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-display text-2xl font-bold">Projets</h1>
        <Button onClick={() => setModalOpen(true)} disabled={clients.length === 0}>
          + Nouveau projet
        </Button>
      </div>

      {clients.length === 0 && !loading && (
        <p className="text-xs text-[var(--color-text-dim)]">
          Ajoutez d&apos;abord un{" "}
          <Link href="/dashboard/clients" className="font-medium text-[var(--color-accent)]">
            client
          </Link>{" "}
          pour pouvoir créer un projet.
        </p>
      )}

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
      ) : projects.length === 0 ? (
        <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-10 text-center">
          <p className="text-sm font-medium">Aucun projet pour l&apos;instant</p>
          <p className="mt-1 text-xs text-[var(--color-text-dim)]">Créez votre premier projet pour un client.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-[var(--color-line)]">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-[var(--color-line)] bg-[var(--color-surface-2)] text-xs uppercase tracking-wide text-[var(--color-text-dim)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Nom</th>
                <th className="px-4 py-3 font-semibold">Client</th>
                <th className="px-4 py-3 font-semibold">Statut</th>
                <th className="px-4 py-3 font-semibold">Échéance</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id} className="border-b border-[var(--color-line)] last:border-0">
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/projects/${p.id}`} className="font-medium hover:text-[var(--color-accent)]">
                      {p.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-[var(--color-text-dim)]">{clientName(p.client_id)}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold ${STATUS_CLASS[p.status]}`}>
                      {STATUS_LABELS[p.status]}
                    </span>
                  </td>
                  <td className="font-data px-4 py-3 text-[var(--color-text-dim)]">{p.due_date || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modalOpen && (
        <NewProjectModal
          clients={clients}
          onClose={() => setModalOpen(false)}
          onCreated={(p) => {
            setProjects((prev) => [p, ...prev]);
            setModalOpen(false);
          }}
        />
      )}
    </div>
  );
}

function NewProjectModal({
  clients,
  onClose,
  onCreated,
}: {
  clients: ClientOut[];
  onClose: () => void;
  onCreated: (p: ProjectOut) => void;
}) {
  const { notify } = useToast();
  const [name, setName] = useState("");
  const [clientId, setClientId] = useState(clients[0]?.id ?? "");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
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
      const project = await api.createProject(token, {
        client_id: clientId,
        name,
        description: description || undefined,
        due_date: dueDate || undefined,
      });
      onCreated(project);
      notify("Projet créé.", "success");
    } catch {
      notify("Impossible de créer le projet", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal title="Nouveau projet" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <Field label="Nom" name="name" value={name} onChange={(e) => setName(e.target.value)} error={errors.name} />

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

        <Field
          label="Échéance"
          name="due_date"
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />

        <div className="flex flex-col gap-1.5">
          <label htmlFor="description" className="text-sm font-medium">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3.5 py-2.5 text-sm outline-none focus:border-[var(--color-accent)]"
          />
        </div>

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
