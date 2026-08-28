"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { AuthCard } from "@/components/layout/AuthCard";

export default function LoginPage() {
  const { login } = useAuth();
  const { notify } = useToast();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login({ email, password });
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Email ou mot de passe incorrect");
      } else {
        notify(err instanceof Error ? err.message : "Connexion impossible", "error");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleForgotPassword() {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Entrez votre email ci-dessus d'abord");
      return;
    }
    setResetLoading(true);
    try {
      await api.forgotPassword(email);
      notify("Si ce compte existe, un email de réinitialisation a été envoyé.", "success");
    } catch {
      notify("Impossible d'envoyer l'email pour le moment", "error");
    } finally {
      setResetLoading(false);
    }
  }

  return (
    <AuthCard title="Se connecter" subtitle="Retrouvez votre activité.">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        <Field
          label="Email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Field
          label="Mot de passe"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={error}
        />
        <button
          type="button"
          onClick={handleForgotPassword}
          disabled={resetLoading}
          className="self-end text-xs font-medium text-[var(--color-text-dim)] hover:text-[var(--color-accent)] disabled:opacity-60"
        >
          {resetLoading ? "Envoi..." : "Mot de passe oublié ?"}
        </button>
        <Button type="submit" loading={loading} className="mt-1 w-full">
          Se connecter
        </Button>
      </form>
      <p className="mt-5 text-center text-sm text-[var(--color-text-dim)]">
        Pas encore de compte ?{" "}
        <Link href="/register" className="font-medium text-[var(--color-accent)]">
          Créer un compte
        </Link>
      </p>
    </AuthCard>
  );
}
