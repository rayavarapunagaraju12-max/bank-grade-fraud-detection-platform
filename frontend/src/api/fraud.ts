import { api } from "./client";
import type { Alert, DashboardSummary, DlqMessage, ModelVersion, Role, Session } from "../types";

export const emptySummary: DashboardSummary = {
  totalTransactions: 0,
  fraudRate: 0,
  avgRiskScore: 0,
  blockedToday: 0,
  trend: [],
  liveTransactions: []
};

export async function getHealth() {
  const response = await api.get("/health");
  return response.data;
}

export async function getAlerts(): Promise<Alert[]> {
  const response = await api.get("/alerts", { params: { min_score: 0, sort: "recent", _: Date.now() } });
  return response.data;
}

export async function transitionAlert(alertId: string, payload: {
  status: string;
  assigned_to?: string;
  decision?: string;
  notes?: string;
}): Promise<Alert> {
  const response = await api.patch(`/alerts/${encodeURIComponent(alertId)}/decision`, payload);
  return response.data;
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  try {
    const response = await api.get("/dashboard/summary", { params: { _: Date.now() } });
    return response.data;
  } catch (error: any) {
    if (error?.response?.status !== 404) {
      throw error;
    }
    const [transactionsResponse, alerts] = await Promise.all([
      api.get("/transactions/recent", { params: { _: Date.now() } }),
      getAlerts()
    ]);
    const transactions = transactionsResponse.data as Array<{
      transaction_id: string;
      amount: number;
      payload?: { merchant_id?: string };
      created_at: string;
    }>;
    const liveTransactions = transactions.slice(0, 25).map((txn) => {
      const alert = alerts.find((item) => item.transaction_id === txn.transaction_id);
      const riskScore = alert ? Math.round(Number(alert.score) * 100) : 0;
      return {
        id: txn.transaction_id,
        amount: txn.amount,
        merchant: txn.payload?.merchant_id ?? "unknown",
        risk_score: riskScore,
        status: alert ? "flagged" as const : "approved" as const,
        timestamp: txn.created_at
      };
    });
    const scores = alerts.map((alert) => Number(alert.score)).filter(Number.isFinite);
    return {
      totalTransactions: transactions.length,
      fraudRate: transactions.length ? Number(((alerts.length / transactions.length) * 100).toFixed(2)) : 0,
      avgRiskScore: scores.length ? Number(((scores.reduce((sum, score) => sum + score, 0) / scores.length) * 100).toFixed(1)) : 0,
      blockedToday: alerts.filter((alert) => alert.status === "open").length,
      trend: alerts.slice(0, 18).reverse().map((alert) => ({
        t: new Date(alert.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        score: Number((Number(alert.score) * 100).toFixed(1)),
        alerts: 1
      })),
      liveTransactions
    };
  }
}

export async function generateFraudCase() {
  const response = await api.post("/demo/generate?fraud_ring=true");
  return response.data;
}

export async function generateStreamTransaction() {
  const response = await api.post("/demo/stream/generate", null, {
    params: { count: 1, fraud_ratio: 0.35, _: Date.now() }
  });
  return response.data;
}

export async function login(username: string, password: string): Promise<Session> {
  const response = await api.post("/auth/token", { username, password });
  return {
    username,
    token: response.data.access_token,
    roles: response.data.roles as Role[]
  };
}

export async function getWatchlistStatus() {
  const response = await api.get("/compliance/watchlists/status");
  return response.data;
}

export async function refreshDemoWatchlists() {
  const response = await api.post("/compliance/watchlists/refresh", {});
  return response.data;
}

export async function refreshOfficialWatchlists() {
  const response = await api.post("/compliance/watchlists/refresh-official");
  return response.data;
}

export async function getDlqMessages(): Promise<DlqMessage[]> {
  const response = await api.get("/dlq/messages");
  return response.data;
}

export async function retryDlqMessage(eventId: string) {
  const response = await api.post(`/dlq/messages/${eventId}/retry`);
  return response.data;
}

export async function getModelVersions(): Promise<ModelVersion[]> {
  const response = await api.get("/models/governance");
  return response.data;
}

export async function registerModelVersion(payload: {
  model_name: string;
  version: string;
  artifact_path: string;
  metrics: Record<string, number | string>;
}) {
  const response = await api.post("/models/governance", payload);
  return response.data;
}

export async function transitionModelVersion(modelId: string, status: string) {
  const response = await api.post(`/models/governance/${modelId}/transition`, { status });
  return response.data;
}

export async function getGraph(accountId: string) {
  const response = await api.get(`/graph/${encodeURIComponent(accountId)}`);
  return response.data;
}
