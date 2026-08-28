import Link from "next/link";
import { Button } from "@/components/ui/Button";

const FEATURES = [
  {
    num: "01",
    title: "Pipeline clair",
    body: "Suivez chaque prospect du premier contact à la facture payée, sans tableur.",
  },
  {
    num: "02",
    title: "Devis en 2 minutes",
    body: "Décrivez le projet, l'IA rédige la première version — vous ajustez et envoyez.",
  },
  {
    num: "03",
    title: "Relances automatiques",
    body: "Les factures en retard se rappellent à vos clients toutes seules.",
  },
  {
    num: "04",
    title: "Vue d'ensemble",
    body: "Un dashboard qui dit où en est votre activité, sans ouvrir quatre outils.",
  },
];

const PLANS = [
  { name: "Free", price: "0 €", items: ["3 prospects actifs", "2 devis/factures / mois", "Pas d'IA"] },
  {
    name: "Starter",
    price: "9 €",
    period: "/mois",
    items: ["Prospects illimités", "15 devis/factures / mois", "IA — 5 générations/mois"],
  },
  {
    name: "Pro",
    price: "19 €",
    period: "/mois",
    items: ["Tout illimité", "IA illimitée", "Relances automatiques"],
    featured: true,
  },
  {
    name: "Business",
    price: "39 €",
    period: "/mois",
    items: ["Tout Pro", "Jusqu'à 5 utilisateurs", "Marque blanche"],
  },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-[var(--color-line)]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="font-display text-lg font-extrabold">FreelanceHub</span>
          <nav className="flex items-center gap-3">
            <Link href="/login" className="text-sm font-medium text-[var(--color-text-dim)] hover:text-[var(--color-text)]">
              Connexion
            </Link>
            <Link href="/register">
              <Button>Démarrer gratuitement</Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-10 px-6 py-16 md:grid-cols-[1.15fr_0.85fr] md:py-24">
          <div>
            <span className="font-data mb-3 block text-xs uppercase tracking-wider text-[var(--color-accent)]">
              Pour freelances UX/UI &amp; Front-End
            </span>
            <h1 className="font-display text-4xl font-extrabold leading-[1.05] text-balance md:text-5xl">
              Le studio administratif de votre activité freelance.
            </h1>
            <p className="mt-5 max-w-[46ch] text-[17px] leading-relaxed text-[var(--color-text-dim)]">
              Prospects, devis, factures et projets, gérés au même endroit — avec un assistant IA qui rédige vos
              devis et relance vos impayés pendant que vous designez.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/register">
                <Button>Démarrer gratuitement</Button>
              </Link>
              <Link href="/login">
                <Button variant="secondary">Se connecter</Button>
              </Link>
            </div>
          </div>

          <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] p-4">
            <div className="flex flex-col gap-3">
              <MiniStat label="CA du mois" value="3 240 €" pct={64} />
              <MiniStat label="Prospects actifs" value="7" pct={40} />
              <MiniStat label="Factures payées" value="12 / 14" pct={86} />
            </div>
          </div>
        </section>

        <section className="border-t border-[var(--color-line)]">
          <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 px-6 py-14 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f) => (
              <div key={f.num}>
                <span className="font-data mb-2 block text-xs text-[var(--color-accent)]">{f.num}</span>
                <h3 className="mb-1.5 text-base font-semibold">{f.title}</h3>
                <p className="text-sm leading-relaxed text-[var(--color-text-dim)]">{f.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="border-t border-[var(--color-line)]">
          <div className="mx-auto max-w-6xl px-6 py-14">
            <h2 className="font-data mb-5 text-xs font-semibold uppercase tracking-wider text-[var(--color-text-dim)]">
              Tarifs
            </h2>
            <div className="overflow-x-auto">
              <div className="grid min-w-[640px] grid-cols-4 gap-3.5">
                {PLANS.map((p) => (
                  <div
                    key={p.name}
                    className={`rounded-lg border px-4 py-4.5 ${
                      p.featured
                        ? "border-[var(--color-accent)] shadow-[0_0_0_1px_var(--color-accent)_inset]"
                        : "border-[var(--color-line)]"
                    }`}
                  >
                    <div className="text-sm font-semibold">{p.name}</div>
                    <div className="font-data mt-2 mb-1 text-[22px]">
                      {p.price}
                      {p.period && (
                        <small className="text-xs font-normal text-[var(--color-text-dim)]">{p.period}</small>
                      )}
                    </div>
                    <ul className="mt-3 flex flex-col gap-1.5">
                      {p.items.map((item) => (
                        <li key={item} className="text-xs text-[var(--color-text-dim)]">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="font-data border-t border-[var(--color-line)] py-6 text-center text-xs text-[var(--color-text-dim)]">
        freelancehub
      </footer>
    </div>
  );
}

function MiniStat({ label, value, pct }: { label: string; value: string; pct: number }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-[13px]">
        <span className="text-[var(--color-text-dim)]">{label}</span>
        <span className="font-data">{value}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-sm bg-[var(--color-line)]">
        <div className="h-full bg-[var(--color-accent)]" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
