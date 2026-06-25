export type Alert = {
  alert_id: string;
  transaction_id: string;
  score: number;
  risk_band: string;
  status: string;
  assigned_to?: string | null;
  decision?: string | null;
  decision_notes?: string | null;
  reviewed_by?: string | null;
  resolved_at?: string | null;
  payload: any;
  updated_at?: string;
  created_at: string;
};

export type ApiStatus = {
  connected: boolean;
  label: string;
};

export type LiveTransaction = {
  id: string;
  amount: number;
  merchant: string;
  risk_score: number;
  status: "processing" | "flagged" | "approved";
  timestamp: string;
};

export type DashboardSummary = {
  totalTransactions: number;
  fraudRate: number;
  avgRiskScore: number;
  blockedToday: number;
  trend: Array<{ t: string; score: number; alerts: number }>;
  liveTransactions: LiveTransaction[];
};

export type ComplianceState = {
  status?: any;
  screening?: any;
  report?: any;
  validation?: any;
  error?: string;
};

export type Role = "analyst" | "supervisor" | "auditor" | "admin";

export type Session = {
  username: string;
  roles: Role[];
  token: string;
};

export type DlqMessage = {
  event_id: string;
  source_topic: string;
  error: string;
  payload: any;
  metadata: any;
  status: string;
  created_at: string;
};

export type ModelVersion = {
  model_id: string;
  model_name: string;
  version: string;
  artifact_path: string;
  status: string;
  metrics: Record<string, number | string>;
  approved_by?: string | null;
  approved_at?: string | null;
  deployed_at?: string | null;
  created_at: string;
};
