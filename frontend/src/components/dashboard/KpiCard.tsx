import Link from "next/link";

export function KpiCard({
  label,
  value,
  note,
  href,
}: {
  label: string;
  value: string;
  note?: string;
  href?: string;
}) {
  const content = (
    <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] px-4 py-3.5 transition-colors hover:border-[var(--color-text-dim)]">
      <div className="text-xs text-[var(--color-text-dim)]">{label}</div>
      <div className="font-data mt-1 text-2xl">{value}</div>
      {note && <div className="mt-1 text-[11px] text-[var(--color-text-dim)]">{note}</div>}
    </div>
  );

  if (!href) return content;

  return (
    <Link href={href} className="block">
      {content}
    </Link>
  );
}
