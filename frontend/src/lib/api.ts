import type {
  ClientOut,
  LoginInput,
  OrganizationOut,
  ProspectCreateInput,
  ProspectOut,
  ProspectStatus,
  ProspectUpdateInput,
  RegisterInput,
  TokenResponse,
  UserOut,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// L'AuthProvider s'enregistre ici pour être notifié d'un 401 n'importe où
// dans l'app (token expiré pendant que l'utilisateur navigue) — évite de
// faire remonter cette logique dans chaque appel API individuel.
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(handler: (() => void) | null) {
  onUnauthorized = handler;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (res.status === 401 && onUnauthorized) {
    onUnauthorized();
  }

  if (!res.ok) {
    let detail = res.statusText || "Une erreur est survenue";
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // pas de corps JSON exploitable — on garde le message par défaut
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  register: (data: RegisterInput) =>
    request<TokenResponse>("/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (data: LoginInput) =>
    request<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify(data) }),

  forgotPassword: (email: string) =>
    request<void>("/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),

  resetPassword: (token: string, new_password: string) =>
    request<void>("/auth/reset-password", { method: "POST", body: JSON.stringify({ token, new_password }) }),

  me: (token: string) => request<UserOut>("/users/me", {}, token),

  myOrganization: (token: string) => request<OrganizationOut>("/organizations/me", {}, token),

  listProspects: (token: string, status?: ProspectStatus) =>
    request<ProspectOut[]>(`/prospects${status ? `?status_filter=${status}` : ""}`, {}, token),

  createProspect: (token: string, data: ProspectCreateInput) =>
    request<ProspectOut>("/prospects", { method: "POST", body: JSON.stringify(data) }, token),

  updateProspect: (token: string, id: string, data: ProspectUpdateInput) =>
    request<ProspectOut>(`/prospects/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token),

  convertProspect: (token: string, id: string) =>
    request<ClientOut>(`/prospects/${id}/convert`, { method: "POST" }, token),

  deleteProspect: (token: string, id: string) =>
    request<void>(`/prospects/${id}`, { method: "DELETE" }, token),

  listClients: (token: string) => request<ClientOut[]>("/clients", {}, token),
};
