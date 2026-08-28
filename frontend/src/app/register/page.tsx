"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { AuthCard } from "@/components/layout/AuthCard";

export default function RegisterPage() {
  const { register } = useAuth();
  const { notify } = useToast();
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  function validate() {
    const next: Record<string, string> = {};
    if (!fullName.trim()) next.fullName = "Votre nom est requis";
    if (!organizationName.trim()) next.organizationName = "Le nom de votre activité est requis";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) next.email = "Email invalide";
    if (password.length < 8) next.password = "8 caractères minimum";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await register({ email, password, full_name: fullName, organization_name: organizationName });
      router.push("/onboarding");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setErrors({ email: "Cet email est déjà utilisé" });
      } else {
        notify(err instanceof Error ? err.message : "Impossible de créer le compte", "error");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard title="Créer votre espace" subtitle="Opérationnel en moins de deux minutes.">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <Field
          label="Nom complet"
          name="fullName"
          autoComplete="name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          error={errors.fullName}
        />
        <Field
          label="Nom de votre activité"
          name="organizationName"
          placeholder="ex : Studio Lumen"
          value={organizationName}
          onChange={(e) => setOrganizationName(e.target.value)}
          error={errors.organizationName}
        />
        <Field
          label="Email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
        />
        <Field
          label="Mot de passe"
          name="password"
          type="password"
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
        />
        <Button type="submit" loading={loading} className="mt-2 w-full">
          Créer mon compte
        </Button>
      </form>
      <p className="mt-5 text-center text-sm text-[var(--color-text-dim)]">
        Déjà un compte ?{" "}
        <Link href="/login" className="font-medium text-[var(--color-accent)]">
          Se connecter
        </Link>
      </p>
    </AuthCard>
  );
}
