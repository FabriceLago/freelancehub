"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/Button";

export default function OnboardingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-full items-center justify-center">
        <span className="text-sm text-[var(--color-text-dim)]">Chargement...</span>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-col items-center justify-center px-6 py-16 text-center">
      <span className="font-data mb-3 block text-xs uppercase tracking-wider text-[var(--color-accent)]">
        Compte créé
      </span>
      <h1 className="font-display max-w-md text-3xl font-extrabold text-balance">
        Bienvenue, {user.full_name.split(" ")[0]}.
      </h1>
      <p className="mt-3 max-w-sm text-[15px] leading-relaxed text-[var(--color-text-dim)]">
        Votre espace est prêt. Ajoutez votre premier prospect ou explorez le dashboard pour commencer.
      </p>
      <Button className="mt-8" onClick={() => router.push("/dashboard")}>
        Accéder à mon dashboard
      </Button>
    </div>
  );
}
