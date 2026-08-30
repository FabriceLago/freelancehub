import type {
  ClientCreateInput,
  ClientOut,
  ClientUpdateInput,
  InvoiceCreateInput,
  InvoiceDetailOut,
  InvoiceOut,
  InvoiceStatus,
  InvoiceUpdateInput,
  LoginInput,
  OrganizationOut,
  ProjectCreateInput,
  ProjectDetailOut,
  ProjectOut,
  ProjectStatus,
  ProjectUpdateInput,
  ProspectCreateInput,
  ProspectOut,
  ProspectStatus,
  ProspectUpdateInput,
  QuoteCreateInput,
  QuoteDetailOut,
  QuoteDraftResponse,
  QuoteOut,
  QuoteStatus,
  QuoteUpdateInput,
  RegisterInput,
  ReminderDraftResponse,
  TaskCreateInput,
  TaskOut,
  TaskUpdateInput,
  TaskWithProjectOut,
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

  createClient: (token: string, data: ClientCreateInput) =>
    request<ClientOut>("/clients", { method: "POST", body: JSON.stringify(data) }, token),

  updateClient: (token: string, id: string, data: ClientUpdateInput) =>
    request<ClientOut>(`/clients/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token),

  deleteClient: (token: string, id: string) =>
    request<void>(`/clients/${id}`, { method: "DELETE" }, token),

  listProjects: (token: string, status?: ProjectStatus) =>
    request<ProjectOut[]>(`/projects${status ? `?status_filter=${status}` : ""}`, {}, token),

  createProject: (token: string, data: ProjectCreateInput) =>
    request<ProjectOut>("/projects", { method: "POST", body: JSON.stringify(data) }, token),

  getProject: (token: string, id: string) => request<ProjectDetailOut>(`/projects/${id}`, {}, token),

  updateProject: (token: string, id: string, data: ProjectUpdateInput) =>
    request<ProjectOut>(`/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token),

  deleteProject: (token: string, id: string) =>
    request<void>(`/projects/${id}`, { method: "DELETE" }, token),

  createTask: (token: string, projectId: string, data: TaskCreateInput) =>
    request<TaskOut>(`/projects/${projectId}/tasks`, { method: "POST", body: JSON.stringify(data) }, token),

  updateTask: (token: string, taskId: string, data: TaskUpdateInput) =>
    request<TaskOut>(`/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify(data) }, token),

  deleteTask: (token: string, taskId: string) =>
    request<void>(`/tasks/${taskId}`, { method: "DELETE" }, token),

  listIncompleteTasks: (token: string) => request<TaskWithProjectOut[]>("/tasks", {}, token),

  listQuotes: (token: string, status?: QuoteStatus) =>
    request<QuoteOut[]>(`/quotes${status ? `?status_filter=${status}` : ""}`, {}, token),

  createQuote: (token: string, data: QuoteCreateInput) =>
    request<QuoteOut>("/quotes", { method: "POST", body: JSON.stringify(data) }, token),

  getQuote: (token: string, id: string) => request<QuoteDetailOut>(`/quotes/${id}`, {}, token),

  updateQuote: (token: string, id: string, data: QuoteUpdateInput) =>
    request<QuoteDetailOut>(`/quotes/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token),

  transitionQuote: (token: string, id: string, status: QuoteStatus) =>
    request<QuoteOut>(`/quotes/${id}/transition`, { method: "POST", body: JSON.stringify({ status }) }, token),

  convertQuoteToInvoice: (token: string, id: string) =>
    request<InvoiceOut>(`/quotes/${id}/convert-to-invoice`, { method: "POST" }, token),

  deleteQuote: (token: string, id: string) => request<void>(`/quotes/${id}`, { method: "DELETE" }, token),

  listInvoices: (token: string, status?: InvoiceStatus) =>
    request<InvoiceOut[]>(`/invoices${status ? `?status_filter=${status}` : ""}`, {}, token),

  createInvoice: (token: string, data: InvoiceCreateInput) =>
    request<InvoiceOut>("/invoices", { method: "POST", body: JSON.stringify(data) }, token),

  getInvoice: (token: string, id: string) => request<InvoiceDetailOut>(`/invoices/${id}`, {}, token),

  updateInvoice: (token: string, id: string, data: InvoiceUpdateInput) =>
    request<InvoiceDetailOut>(`/invoices/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token),

  transitionInvoice: (token: string, id: string, status: InvoiceStatus) =>
    request<InvoiceOut>(`/invoices/${id}/transition`, { method: "POST", body: JSON.stringify({ status }) }, token),

  markInvoicePaid: (token: string, id: string) =>
    request<InvoiceOut>(`/invoices/${id}/mark-paid`, { method: "POST" }, token),

  deleteInvoice: (token: string, id: string) => request<void>(`/invoices/${id}`, { method: "DELETE" }, token),

  generateQuoteDraft: (token: string, clientId: string, prompt: string) =>
    request<QuoteDraftResponse>(
      "/ai/quote-draft",
      { method: "POST", body: JSON.stringify({ client_id: clientId, prompt }) },
      token,
    ),

  generateReminderDraft: (token: string, invoiceId: string) =>
    request<ReminderDraftResponse>(`/ai/invoices/${invoiceId}/reminder-draft`, { method: "POST" }, token),
};
