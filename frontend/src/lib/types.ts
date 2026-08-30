export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type UserOut = {
  id: string;
  email: string;
  full_name: string;
  is_verified: boolean;
};

export type Role = "owner" | "admin" | "member";
export type PlanCode = "free" | "starter" | "pro" | "business";
export type SubscriptionStatus = "trialing" | "active" | "past_due" | "canceled" | "incomplete";

export type OrganizationOut = {
  id: string;
  name: string;
  currency: string;
  role: Role;
  plan: PlanCode;
  subscription_status: SubscriptionStatus;
};

export type RegisterInput = {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
};

export type LoginInput = {
  email: string;
  password: string;
};

export type ProspectStatus = "contacted" | "discussing" | "converted" | "lost";

export type ProspectOut = {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  status: ProspectStatus;
  source: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ProspectCreateInput = {
  name: string;
  email?: string;
  phone?: string;
  source?: string;
  notes?: string;
};

export type ProspectUpdateInput = Partial<ProspectCreateInput> & {
  status?: ProspectStatus;
};

export type ClientOut = {
  id: string;
  name: string;
  company: string | null;
  email: string | null;
  phone: string | null;
  converted_from_prospect_id: string | null;
  created_at: string;
  updated_at: string;
};

export type ClientCreateInput = {
  name: string;
  company?: string;
  email?: string;
  phone?: string;
};

export type ClientUpdateInput = Partial<ClientCreateInput>;

export type ProjectStatus = "active" | "completed" | "archived";

export type ProjectOut = {
  id: string;
  client_id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  start_date: string | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
};

export type TaskOut = {
  id: string;
  title: string;
  is_done: boolean;
  due_date: string | null;
  created_at: string;
};

export type ProjectDetailOut = ProjectOut & {
  tasks: TaskOut[];
};

export type ProjectCreateInput = {
  client_id: string;
  name: string;
  description?: string;
  start_date?: string;
  due_date?: string;
};

export type ProjectUpdateInput = Partial<Omit<ProjectCreateInput, "client_id">> & {
  status?: ProjectStatus;
};

export type TaskCreateInput = {
  title: string;
  due_date?: string;
};

export type TaskUpdateInput = {
  title?: string;
  due_date?: string;
  is_done?: boolean;
};

export type TaskWithProjectOut = TaskOut & {
  project_id: string;
  project_name: string;
};

// tax_rate et quantity sont des Decimal côté backend — Pydantic les sérialise
// en chaînes (pas des number JS) pour ne jamais perdre de précision.
export type QuoteStatus = "draft" | "sent" | "accepted" | "declined" | "expired";
export type InvoiceStatus = "draft" | "sent" | "paid" | "overdue" | "cancelled";

export type LineItemInput = {
  description: string;
  quantity?: string;
  unit_price_cents: number;
};

export type LineItemOut = {
  id: string;
  description: string;
  quantity: string;
  unit_price_cents: number;
  position: number;
};

export type QuoteOut = {
  id: string;
  number: string;
  status: QuoteStatus;
  currency: string;
  client_id: string;
  project_id: string | null;
  subtotal_cents: number;
  tax_rate: string;
  total_cents: number;
  valid_until: string | null;
  sent_at: string | null;
  accepted_at: string | null;
  created_at: string;
  updated_at: string;
};

export type QuoteDetailOut = QuoteOut & {
  line_items: LineItemOut[];
};

export type QuoteCreateInput = {
  client_id: string;
  project_id?: string;
  tax_rate?: string;
  valid_until?: string;
  line_items: LineItemInput[];
};

export type QuoteUpdateInput = {
  project_id?: string;
  tax_rate?: string;
  valid_until?: string;
  line_items?: LineItemInput[];
};

export type PaymentOut = {
  id: string;
  amount_cents: number;
  method: string;
  paid_at: string;
};

export type InvoiceOut = {
  id: string;
  number: string;
  status: InvoiceStatus;
  currency: string;
  client_id: string;
  project_id: string | null;
  quote_id: string | null;
  subtotal_cents: number;
  tax_rate: string;
  total_cents: number;
  paid_cents: number;
  balance_cents: number;
  due_date: string | null;
  sent_at: string | null;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
};

export type InvoiceDetailOut = InvoiceOut & {
  line_items: LineItemOut[];
  payments: PaymentOut[];
};

export type InvoiceCreateInput = {
  client_id: string;
  project_id?: string;
  tax_rate?: string;
  due_date?: string;
  line_items: LineItemInput[];
};

export type InvoiceUpdateInput = {
  project_id?: string;
  tax_rate?: string;
  due_date?: string;
  line_items?: LineItemInput[];
};

export type QuoteDraftLineItem = {
  description: string;
  quantity: number;
  unit_price_cents: number;
};

export type QuoteDraftResponse = {
  line_items: QuoteDraftLineItem[];
  suggested_tax_rate: number;
};

export type ReminderDraftResponse = {
  subject: string;
  body: string;
};

export type PlanOut = {
  id: string;
  code: PlanCode;
  name: string;
  price_cents: number;
  max_prospects: number | null;
  max_documents_per_month: number | null;
  ai_generations_per_month: number | null;
};

export type SessionUrlResponse = {
  url: string;
};
