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

export type OrganizationOut = {
  id: string;
  name: string;
  currency: string;
  role: Role;
  plan: PlanCode;
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
