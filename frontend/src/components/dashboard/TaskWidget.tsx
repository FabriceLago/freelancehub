import Link from "next/link";
import type { TaskWithProjectOut } from "@/lib/types";
import { EmptyWidget } from "./EmptyWidget";

export function TaskWidget({ tasks }: { tasks: TaskWithProjectOut[] }) {
  if (tasks.length === 0) {
    return <EmptyWidget message="Aucune tâche en attente." />;
  }

  return (
    <ul className="flex flex-col divide-y divide-[var(--color-line)]">
      {tasks.map((t) => (
        <li key={t.id} className="flex items-center justify-between gap-4 py-2.5 text-sm">
          <div>
            <div className="font-medium">{t.title}</div>
            <Link
              href={`/dashboard/projects/${t.project_id}`}
              className="text-xs text-[var(--color-text-dim)] hover:text-[var(--color-accent)]"
            >
              {t.project_name}
            </Link>
          </div>
          {t.due_date && <span className="font-data shrink-0 text-xs text-[var(--color-text-dim)]">{t.due_date}</span>}
        </li>
      ))}
    </ul>
  );
}
