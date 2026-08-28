import type { ClientOut, ProspectOut } from "./types";

export type ActivityItem = {
  id: string;
  label: string;
  meta: string;
  timestamp: string;
};

// Dérivée des données prospects/clients déjà chargées par ailleurs — pas
// besoin d'un flux d'événements dédié tant qu'on n'a que ces deux sources.
// Le jour où projets/devis/factures existent, ajouter leurs événements ici
// plutôt que de construire un système de log générique par anticipation.
export function buildActivityFeed(prospects: ProspectOut[], clients: ClientOut[], limit = 6): ActivityItem[] {
  const items: ActivityItem[] = [
    ...prospects.map((p) => ({
      id: `prospect-${p.id}`,
      label: `Nouveau prospect — ${p.name}`,
      meta: p.source || "Source inconnue",
      timestamp: p.created_at,
    })),
    ...clients.map((c) => ({
      id: `client-${c.id}`,
      label: c.converted_from_prospect_id ? `Converti en client — ${c.name}` : `Nouveau client — ${c.name}`,
      meta: c.converted_from_prospect_id ? "Prospect converti" : "Ajouté directement",
      timestamp: c.created_at,
    })),
  ];

  return items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, limit);
}

export function formatRelativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.round(diffMs / 60000);
  if (minutes < 1) return "à l'instant";
  if (minutes < 60) return `il y a ${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `il y a ${hours} h`;
  const days = Math.round(hours / 24);
  return `il y a ${days} j`;
}
