"use client";

import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  loading?: boolean;
};

const base =
  "inline-flex items-center justify-center gap-2 rounded-md px-5 py-2.5 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-accent)]";

const variants: Record<Variant, string> = {
  primary: "bg-[var(--color-accent)] text-[var(--color-accent-text)] hover:brightness-110",
  secondary:
    "bg-transparent text-[var(--color-text)] border border-[var(--color-line)] hover:bg-[var(--color-surface-2)]",
  ghost: "bg-transparent text-[var(--color-text-dim)] hover:text-[var(--color-text)]",
};

export function Button({ variant = "primary", loading, disabled, children, className = "", ...props }: ButtonProps) {
  return (
    <button
      className={`${base} ${variants[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span
          className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"
          aria-hidden="true"
        />
      )}
      {children}
    </button>
  );
}
