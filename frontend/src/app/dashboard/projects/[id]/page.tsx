"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, use, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import type { OrganizationOut, ProjectDetailOut, ProjectStatus } from "@/lib/types";
import { Button } from "@/components/ui/Button";

const STATUS_OPTIONS: { value: ProjectStatus; label: string }[] = [
  { value: "active", label: "Actif" },
  { value: "completed", label: "Terminé" },
  { value: "archived", label: "Archivé" },
];

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { notify } = useToast();
  const router = useRouter();

  const [org, setOrg] = useState<OrganizationOut | null>(null);
  const [project, setProject] = useState<ProjectDetailOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [taskBusyId, setTaskBusyId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const canDelete = org?.role === "owner" || org?.role === "admin";

  async function load() {
    const token = getStoredToken();
    if (!token) return;
    setLoading(true);
    try {
      const [orgData, projectData] = await Promise.all([api.myOrganization(token), api.getProject(token, id)]);
      setOrg(orgData);
      setProject(projectData);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        notify("Projet introuvable", "error");
        router.push("/dashboard/projects");
      } else {
        notify("Impossible de charger le projet", "error");
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

  async function handleStatusChange(status: ProjectStatus) {
    const token = getStoredToken();
    if (!token || !project) return;
    try {
      const updated = await api.updateProject(token, project.id, { status });
      setProject({ ...project, ...updated });
    } catch {
      notify("Impossible de changer le statut", "error");
    }
  }

  async function handleAddTask(e: FormEvent) {
    e.preventDefault();
    if (!newTaskTitle.trim() || !project) return;
    const token = getStoredToken();
    if (!token) return;
    try {
      const task = await api.createTask(token, project.id, { title: newTaskTitle });
      setProject({ ...project, tasks: [...project.tasks, task] });
      setNewTaskTitle("");
    } catch {
      notify("Impossible d'ajouter la tâche", "error");
    }
  }

  async function handleToggleTask(taskId: string, isDone: boolean) {
    const token = getStoredToken();
    if (!token || !project) return;
    setTaskBusyId(taskId);
    try {
      const updated = await api.updateTask(token, taskId, { is_done: isDone });
      setProject({ ...project, tasks: project.tasks.map((t) => (t.id === taskId ? updated : t)) });
    } catch {
      notify("Impossible de mettre à jour la tâche", "error");
    } finally {
      setTaskBusyId(null);
    }
  }

  async function handleDeleteTask(taskId: string) {
    const token = getStoredToken();
    if (!token || !project) return;
    setTaskBusyId(taskId);
    try {
      await api.deleteTask(token, taskId);
      setProject({ ...project, tasks: project.tasks.filter((t) => t.id !== taskId) });
    } catch {
      notify("Impossible de supprimer la tâche", "error");
    } finally {
      setTaskBusyId(null);
    }
  }

  async function handleDeleteProject() {
    const token = getStoredToken();
    if (!token || !project) return;
    setDeleting(true);
    try {
      await api.deleteProject(token, project.id);
      notify("Projet supprimé.", "success");
      router.push("/dashboard/projects");
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Impossible de supprimer le projet", "error");
      setDeleting(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>;
  }

  if (!project) return null;

  const doneCount = project.tasks.filter((t) => t.is_done).length;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link href="/dashboard/projects" className="text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-text)]">
          ← Projets
        </Link>
        <div className="mt-2 flex items-center justify-between gap-4">
          <h1 className="font-display text-2xl font-bold">{project.name}</h1>
          <select
            value={project.status}
            onChange={(e) => handleStatusChange(e.target.value as ProjectStatus)}
            className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3 py-1.5 text-sm"
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        {project.description && (
          <p className="mt-2 max-w-2xl text-sm text-[var(--color-text-dim)]">{project.description}</p>
        )}
        {project.due_date && (
          <p className="font-data mt-2 text-xs text-[var(--color-text-dim)]">Échéance : {project.due_date}</p>
        )}
      </div>

      <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold">
            Tâches {project.tasks.length > 0 && `(${doneCount}/${project.tasks.length})`}
          </h2>
        </div>

        {project.tasks.length === 0 ? (
          <p className="text-sm text-[var(--color-text-dim)]">Aucune tâche pour l&apos;instant.</p>
        ) : (
          <ul className="mb-4 flex flex-col divide-y divide-[var(--color-line)]">
            {project.tasks.map((t) => (
              <li key={t.id} className="flex items-center gap-3 py-2.5">
                <input
                  type="checkbox"
                  checked={t.is_done}
                  disabled={taskBusyId === t.id}
                  onChange={(e) => handleToggleTask(t.id, e.target.checked)}
                  className="h-4 w-4 accent-[var(--color-accent)]"
                />
                <span className={`flex-1 text-sm ${t.is_done ? "text-[var(--color-text-dim)] line-through" : ""}`}>
                  {t.title}
                </span>
                <button
                  onClick={() => handleDeleteTask(t.id)}
                  disabled={taskBusyId === t.id}
                  className="text-xs text-[var(--color-text-dim)] hover:text-[var(--color-danger)] disabled:opacity-60"
                >
                  Supprimer
                </button>
              </li>
            ))}
          </ul>
        )}

        <form onSubmit={handleAddTask} className="flex gap-2">
          <input
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            placeholder="Nouvelle tâche"
            className="flex-1 rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3 py-2 text-sm outline-none focus:border-[var(--color-accent)]"
          />
          <Button type="submit" variant="secondary">
            Ajouter
          </Button>
        </form>
      </div>

      {canDelete && (
        <div className="flex justify-end">
          <button
            onClick={handleDeleteProject}
            disabled={deleting}
            className="text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-danger)] disabled:opacity-60"
          >
            Supprimer ce projet
          </button>
        </div>
      )}
    </div>
  );
}
