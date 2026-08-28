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
