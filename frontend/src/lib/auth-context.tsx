"use client";

import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";
import { api, setUnauthorizedHandler } from "./api";
import { useToast } from "./toast-context";
import type { LoginInput, RegisterInput, UserOut } from "./types";

const TOKEN_KEY = "fh_token";

type AuthContextValue = {
  user: UserOut | null;
  loading: boolean;
  login: (data: LoginInput) => Promise<void>;
  register: (data: RegisterInput) => Promise<void>;
  logout: (reason?: "expired") => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { notify } = useToast();

  function logout(reason?: "expired") {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
    if (reason === "expired") notify("Session expirée, reconnectez-vous.", "info");
    router.push("/login");
  }

  useEffect(() => {
    // Un 401 n'importe où dans l'app (token expiré en cours de navigation)
    // doit déconnecter proprement plutôt que de laisser l'UI dans un état
    // incohérent avec des données à moitié chargées.
    setUnauthorizedHandler(() => logout("expired"));
    return () => setUnauthorizedHandler(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    // Toute mise à jour d'état passe par une continuation de promesse (pas
    // d'appel synchrone dans le corps de l'effet) pour rester dans le
    // pattern recommandé par eslint-plugin-react-hooks.
    Promise.resolve()
      .then(() => (token ? api.me(token) : null))
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        return null;
      })
      .then((me) => setUser(me))
      .finally(() => setLoading(false));
  }, []);

  async function login(data: LoginInput) {
    const { access_token } = await api.login(data);
    localStorage.setItem(TOKEN_KEY, access_token);
    const me = await api.me(access_token);
    setUser(me);
  }

  async function register(data: RegisterInput) {
    const { access_token } = await api.register(data);
    localStorage.setItem(TOKEN_KEY, access_token);
    const me = await api.me(access_token);
    setUser(me);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function getStoredToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}
