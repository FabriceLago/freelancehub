"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getStoredToken } from "@/lib/auth-context";
import type { ClientOut } from "@/lib/types";

export default function ClientsPage() {
  const [clients, setClients] = useState<ClientOut[] | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) return;
    api.listClients(token).then(setClients);
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-2xl font-bold">Clients</h1>

      {clients === null ? (
        <p className="text-sm text-[var(--color-text-dim)]">Chargement...</p>
      ) : clients.length === 0 ? (
        <div className="rounded-lg border border-dashed border-[var(--color-line)] bg-[var(--color-surface-2)] p-10 text-center">
          <p className="text-sm font-medium">Aucun client pour l&apos;instant</p>
          <p className="mt-1 text-xs text-[var(--color-text-dim)]">
            Convertissez un prospect pour voir apparaître votre premier client ici.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-[var(--color-line)]">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead className="border-b border-[var(--color-line)] bg-[var(--color-surface-2)] text-xs uppercase tracking-wide text-[var(--color-text-dim)]">
              <tr>
                <th className="px-4 py-3 font-semibold">Nom</th>
                <th className="px-4 py-3 font-semibold">Contact</th>
                <th className="px-4 py-3 font-semibold">Origine</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((c) => (
                <tr key={c.id} className="border-b border-[var(--color-line)] last:border-0">
                  <td className="px-4 py-3 font-medium">{c.name}</td>
                  <td className="px-4 py-3 text-[var(--color-text-dim)]">{c.email || c.phone || "—"}</td>
                  <td className="px-4 py-3 text-[var(--color-text-dim)]">
                    {c.converted_from_prospect_id ? "Prospect converti" : "Ajouté directement"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-[var(--color-text-dim)]">
        La gestion complète des clients (fiche détail, édition) arrive avec les projets et factures.
      </p>
    </div>
  );
}
