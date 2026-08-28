"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/prospects", label: "Prospects" },
  { href: "/dashboard/clients", label: "Clients" },
  { href: "/dashboard/projects", label: "Projets" },
  { href: "/dashboard/invoices", label: "Devis & Factures" },
  { href: "/dashboard/settings", label: "Paramètres" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="flex w-full flex-col gap-1 p-4 md:w-56 md:border-r md:border-[var(--color-line)] md:p-6">
      <Link href="/dashboard" className="font-display mb-5 px-2 text-base font-extrabold">
        FreelanceHub
      </Link>
      {NAV_ITEMS.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`rounded-md px-3 py-2 text-sm ${
              active
                ? "border border-[var(--color-line)] bg-[var(--color-surface)] font-semibold text-[var(--color-text)]"
                : "text-[var(--color-text-dim)] hover:text-[var(--color-text)]"
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
