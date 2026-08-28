"use client";

import { useEffect, useState } from "react";
import type { LineItemInput } from "@/lib/types";
import { formatCents } from "@/lib/money";
import { Button } from "./Button";

type Row = { description: string; quantity: string; unitPriceEuros: string };

const emptyRow = (): Row => ({ description: "", quantity: "1", unitPriceEuros: "" });

function rowsToLineItems(rows: Row[]): LineItemInput[] {
  return rows
    .filter((r) => r.description.trim())
    .map((r) => ({
      description: r.description,
      quantity: r.quantity || "1",
      unit_price_cents: Math.round(parseFloat(r.unitPriceEuros || "0") * 100),
    }));
}

export function LineItemsEditor({
  initialItems,
  taxRate,
  onTaxRateChange,
  onChange,
}: {
  initialItems?: LineItemInput[];
  taxRate: string;
  onTaxRateChange: (value: string) => void;
  onChange: (items: LineItemInput[]) => void;
}) {
  const [rows, setRows] = useState<Row[]>(
    initialItems && initialItems.length > 0
      ? initialItems.map((li) => ({
          description: li.description,
          quantity: li.quantity ?? "1",
          unitPriceEuros: (li.unit_price_cents / 100).toString(),
        }))
      : [emptyRow()],
  );

  useEffect(() => {
    onChange(rowsToLineItems(rows));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rows]);

  function updateRow(index: number, field: keyof Row, value: string) {
    setRows((prev) => prev.map((r, i) => (i === index ? { ...r, [field]: value } : r)));
  }

  function removeRow(index: number) {
    setRows((prev) => (prev.length > 1 ? prev.filter((_, i) => i !== index) : prev));
  }

  const subtotalCents = rowsToLineItems(rows).reduce(
    (sum, li) => sum + Math.round(parseFloat(li.quantity ?? "1") * li.unit_price_cents),
    0,
  );
  const rate = parseFloat(taxRate || "0");
  const totalCents = subtotalCents + Math.round((subtotalCents * rate) / 100);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-2">
        {rows.map((row, i) => (
          <div key={i} className="flex items-end gap-2">
            <div className="flex-1">
              {i === 0 && <label className="mb-1 block text-xs text-[var(--color-text-dim)]">Description</label>}
              <input
                value={row.description}
                onChange={(e) => updateRow(i, "description", e.target.value)}
                placeholder="ex : Design maquette"
                className="w-full rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-3 py-2 text-sm outline-none focus:border-[var(--color-accent)]"
              />
            </div>
            <div className="w-20">
              {i === 0 && <label className="mb-1 block text-xs text-[var(--color-text-dim)]">Qté</label>}
              <input
                type="number"
                min="0"
                step="0.01"
                value={row.quantity}
                onChange={(e) => updateRow(i, "quantity", e.target.value)}
                className="w-full rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-2 py-2 text-sm outline-none focus:border-[var(--color-accent)]"
              />
            </div>
            <div className="w-28">
              {i === 0 && <label className="mb-1 block text-xs text-[var(--color-text-dim)]">Prix unit. €</label>}
              <input
                type="number"
                min="0"
                step="0.01"
                value={row.unitPriceEuros}
                onChange={(e) => updateRow(i, "unitPriceEuros", e.target.value)}
                className="w-full rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-2 py-2 text-sm outline-none focus:border-[var(--color-accent)]"
              />
            </div>
            <button
              type="button"
              onClick={() => removeRow(i)}
              className="mb-0.5 shrink-0 px-1 text-[var(--color-text-dim)] hover:text-[var(--color-danger)]"
              aria-label="Supprimer la ligne"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <Button type="button" variant="secondary" onClick={() => setRows((prev) => [...prev, emptyRow()])} className="self-start">
        + Ligne
      </Button>

      <div className="flex items-center justify-between border-t border-[var(--color-line)] pt-3">
        <div className="flex items-center gap-2">
          <label htmlFor="tax_rate" className="text-sm text-[var(--color-text-dim)]">
            TVA %
          </label>
          <input
            id="tax_rate"
            type="number"
            min="0"
            max="100"
            step="0.01"
            value={taxRate}
            onChange={(e) => onTaxRateChange(e.target.value)}
            className="w-20 rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] px-2 py-1.5 text-sm outline-none focus:border-[var(--color-accent)]"
          />
        </div>
        <div className="text-right text-sm">
          <div className="text-[var(--color-text-dim)]">Sous-total : {formatCents(subtotalCents)}</div>
          <div className="font-data font-semibold">Total : {formatCents(totalCents)}</div>
        </div>
      </div>
    </div>
  );
}
