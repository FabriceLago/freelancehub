import Link from "next/link";

export function AuthCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-full flex-col items-center justify-center bg-[var(--color-bg)] px-6 py-16">
      <Link href="/" className="font-display mb-8 text-lg font-extrabold">
        FreelanceHub
      </Link>
      <div className="w-full max-w-sm rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-7 shadow-sm">
        <h1 className="font-display text-xl font-bold text-balance">{title}</h1>
        {subtitle && <p className="mt-1.5 text-sm text-[var(--color-text-dim)]">{subtitle}</p>}
        <div className="mt-6">{children}</div>
      </div>
    </div>
  );
}
