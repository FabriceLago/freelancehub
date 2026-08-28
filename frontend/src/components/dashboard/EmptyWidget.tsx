export function EmptyWidget({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed border-[var(--color-line)] px-4 py-6 text-center">
      <p className="text-xs text-[var(--color-text-dim)]">{message}</p>
    </div>
  );
}
