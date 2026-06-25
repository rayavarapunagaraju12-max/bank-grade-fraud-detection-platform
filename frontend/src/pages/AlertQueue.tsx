import { useState } from "react";
import { RefreshCw } from "lucide-react";
import type { Alert } from "../types";

export function AlertQueue({
  alerts,
  select,
  refresh
}: {
  alerts: Alert[];
  select: (alert: Alert) => void;
  refresh: () => Promise<void>;
}) {
  const [refreshing, setRefreshing] = useState(false);
  const handleRefresh = () => {
    setRefreshing(true);
    refresh().finally(() => setRefreshing(false));
  };

  return (
    <div className="panel full-width">
      <h2>Risk-Ranked Alert Queue</h2>
      <button className="panelAction" onClick={handleRefresh} disabled={refreshing}>
        <RefreshCw size={16} />
        {refreshing ? "Generating transaction..." : "Generate & refresh alerts"}
      </button>
      <table className="alerts-table">
        <thead>
          <tr>
            <th>Alert ID</th>
            <th>Transaction</th>
            <th>Risk Level</th>
            <th>Score</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.alert_id} onClick={() => select(alert)} className={`alert-row risk-${alert.risk_band}`}>
              <td className="alert-id">{alert.alert_id}</td>
              <td>{alert.transaction_id}</td>
              <td>
                <span className={`band ${alert.risk_band}`}>{alert.risk_band.toUpperCase()}</span>
              </td>
              <td className="score-value">{alert.score.toFixed(3)}</td>
              <td>
                <span className="status-badge">{alert.status}</span>
              </td>
              <td className="timestamp">{new Date(alert.created_at).toLocaleTimeString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!alerts.length && <p className="muted">No alerts yet. Generate a fraud case to populate the queue.</p>}
    </div>
  );
}
