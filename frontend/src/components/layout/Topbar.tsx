"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export function Topbar() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);

  if (!user) return null;

  return (
    <div className="flex items-center justify-end border-b border-[var(--color-line)] px-6 py-3">
      <div className="relative">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm font-medium hover:bg-[var(--color-surface-2)]"
        >
          <span
            className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-accent)] text-xs font-bold text-[var(--color-accent-text)]"
            aria-hidden="true"
          >
            {user.full_name.charAt(0).toUpperCase()}
          </span>
          {user.full_name}
        </button>
        {open && (
          <div className="absolute right-0 z-10 mt-1 w-44 rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] py-1 shadow-lg">
            <Link
              href="/dashboard/profile"
              className="block px-3 py-2 text-sm hover:bg-[var(--color-surface-2)]"
              onClick={() => setOpen(false)}
            >
              Profil
            </Link>
            <Link
              href="/dashboard/settings"
              className="block px-3 py-2 text-sm hover:bg-[var(--color-surface-2)]"
              onClick={() => setOpen(false)}
            >
              Paramètres
            </Link>
            <button
              onClick={() => logout()}
              className="block w-full px-3 py-2 text-left text-sm text-[var(--color-danger)] hover:bg-[var(--color-surface-2)]"
            >
              Se déconnecter
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
