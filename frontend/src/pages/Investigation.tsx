import { useState } from "react";
import { CheckCircle2, FileCheck2, SearchCheck, ShieldAlert, XCircle } from "lucide-react";
import { transitionAlert } from "../api/fraud";
import type { Alert } from "../types";

export function Investigation({ alert, refresh }: { alert?: Alert | null; refresh: () => Promise<void> }) {
  const [notes, setNotes] = useState("");
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  if (!alert) {
    return <div className="panel full-width"><h2>Investigation Workspace</h2><p className="muted">Select or generate an alert.</p></div>;
  }
  const scorePayload = alert.payload?.score ?? {};
  const transaction = alert.payload?.transaction ?? {};
  const features = scorePayload.explanation?.features ?? [
    { feature: "fraud_score", value: alert.score, contribution: alert.score },
    { feature: "graph_score", value: scorePayload.graph_score ?? 0, contribution: scorePayload.graph_score ?? 0 },
    { feature: "tabular_score", value: scorePayload.tabular_score ?? 0, contribution: scorePayload.tabular_score ?? 0 },
    { feature: "anomaly_score", value: scorePayload.anomaly_score ?? 0, contribution: scorePayload.anomaly_score ?? 0 }
  ];
  const narrative =
    scorePayload.narrative ??
    `This alert is marked ${alert.risk_band} because the transaction risk score is ${(alert.score * 100).toFixed(1)}%. Review account ${transaction.account_id ?? "unknown"}, amount ${transaction.amount ?? "-"}, device ${transaction.device_id ?? "-"}, and IP ${transaction.ip_address ?? "-"} before making a case decision.`;
  const runWorkflow = async (status: string, decision?: string) => {
    setBusyAction(status);
    setError(null);
    try {
      await transitionAlert(alert.alert_id, {
        status,
        assigned_to: status === "investigating" ? "analyst" : undefined,
        decision,
        notes
      });
      setNotes("");
      await refresh();
    } catch (workflowError: any) {
      setError(workflowError?.response?.data?.detail ?? "Unable to update alert workflow");
    } finally {
      setBusyAction(null);
    }
  };
  return (
    <section className="investigation-grid">
      <div className="panel">
        <h2>Transaction Details</h2>
        <div className="txn-details">
          <div className="detail-row"><span className="detail-label">Transaction ID:</span><span className="detail-value">{alert.transaction_id}</span></div>
          <div className="detail-row"><span className="detail-label">Amount:</span><span className="detail-value">${alert.payload?.transaction?.amount}</span></div>
          <div className="detail-row"><span className="detail-label">Risk Score:</span><span className="detail-value risk-high">{alert.score.toFixed(3)}</span></div>
          <div className="detail-row"><span className="detail-label">Status:</span><span className={`detail-value status-${alert.status}`}>{alert.status.toUpperCase()}</span></div>
          <div className="detail-row"><span className="detail-label">Assigned:</span><span className="detail-value">{alert.assigned_to ?? "Unassigned"}</span></div>
          <div className="detail-row"><span className="detail-label">Reviewed By:</span><span className="detail-value">{alert.reviewed_by ?? "-"}</span></div>
          <div className="detail-row"><span className="detail-label">Decision:</span><span className="detail-value">{alert.decision ?? "-"}</span></div>
        </div>
      </div>
      <div className="panel">
        <h2>Alert Workflow</h2>
        <p className="muted">Move the alert through an audited analyst and supervisor lifecycle.</p>
        <textarea
          className="workflow-notes"
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Decision notes"
          rows={4}
        />
        <div className="workflow-actions">
          <button className="panelAction secondary" disabled={!!busyAction} onClick={() => runWorkflow("investigating")}>
            <SearchCheck size={16} /> Investigate
          </button>
          <button className="panelAction secondary" disabled={!!busyAction} onClick={() => runWorkflow("escalated")}>
            <ShieldAlert size={16} /> Escalate
          </button>
          <button className="panelAction success" disabled={!!busyAction} onClick={() => runWorkflow("closed_confirmed_fraud", "confirmed_fraud")}>
            <CheckCircle2 size={16} /> Confirm Fraud
          </button>
          <button className="panelAction warning" disabled={!!busyAction} onClick={() => runWorkflow("closed_false_positive", "false_positive")}>
            <XCircle size={16} /> False Positive
          </button>
          <button className="panelAction" disabled={!!busyAction} onClick={() => runWorkflow("sar_filed", "sar_filed")}>
            <FileCheck2 size={16} /> SAR Filed
          </button>
        </div>
        {busyAction && <p className="muted">Updating workflow...</p>}
        {error && <p className="form-error">{error}</p>}
      </div>
      <div className="panel">
        <h2>Model Explanation</h2>
        <div className="features-list">
          {features.map((feature: any) => (
            <div className="feature-item" key={feature.feature}>
              <div className="feature-name">{feature.feature}</div>
              <div className="feature-bar"><div className="feature-contribution" style={{ width: `${Math.min(Math.abs(feature.contribution) * 100, 100)}%` }} /></div>
              <div className="feature-value">{Number(feature.value ?? feature.contribution ?? 0).toFixed(3)}</div>
            </div>
          ))}
        </div>
        <div className="narrative"><h3>AI Fraud Narrative</h3><p>{narrative}</p></div>
      </div>
    </section>
  );
}
