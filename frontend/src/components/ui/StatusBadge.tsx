import type { ProspectStatus } from "@/lib/types";

const CONFIG: Record<ProspectStatus, { label: string; className: string }> = {
  contacted: { label: "Contacté", className: "bg-[var(--color-surface-2)] text-[var(--color-text-dim)]" },
  discussing: { label: "En discussion", className: "bg-[var(--color-warn-bg)] text-[var(--color-warn)]" },
  converted: { label: "Converti", className: "bg-[var(--color-ok-bg)] text-[var(--color-ok)]" },
  lost: { label: "Perdu", className: "bg-[var(--color-danger-bg)] text-[var(--color-danger)]" },
};

export function StatusBadge({ status }: { status: ProspectStatus }) {
  const { label, className } = CONFIG[status];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-semibold ${className}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {label}
    </span>
  );
}
