import { formatRelativeTime, type ActivityItem } from "@/lib/activity";
import { EmptyWidget } from "./EmptyWidget";

export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  if (items.length === 0) {
    return <EmptyWidget message="Aucune activité pour l'instant." />;
  }

  return (
    <ul className="flex flex-col divide-y divide-[var(--color-line)]">
      {items.map((item) => (
        <li key={item.id} className="flex items-center justify-between gap-4 py-2.5 text-sm">
          <div>
            <div className="font-medium">{item.label}</div>
            <div className="text-xs text-[var(--color-text-dim)]">{item.meta}</div>
          </div>
          <span className="font-data shrink-0 text-xs text-[var(--color-text-dim)]">
            {formatRelativeTime(item.timestamp)}
          </span>
        </li>
      ))}
    </ul>
  );
}
