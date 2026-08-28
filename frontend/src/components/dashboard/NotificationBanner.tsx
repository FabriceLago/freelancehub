export function NotificationBanner({ message, tone = "warn" }: { message: string; tone?: "warn" | "info" }) {
  const toneClass =
    tone === "warn"
      ? "border-[var(--color-warn)] bg-[var(--color-warn-bg)] text-[var(--color-warn)]"
      : "border-[var(--color-line)] bg-[var(--color-surface-2)] text-[var(--color-text)]";

  return (
    <div className={`rounded-lg border px-4 py-3 text-sm font-medium ${toneClass}`} role="status">
      {message}
    </div>
  );
}
