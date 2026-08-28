export function ComingSoon({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-2xl font-bold">{title}</h1>
      <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-10 text-center">
        <p className="text-sm font-medium">Bientôt disponible</p>
        <p className="mt-1 text-xs text-[var(--color-text-dim)]">{description}</p>
      </div>
    </div>
  );
}
