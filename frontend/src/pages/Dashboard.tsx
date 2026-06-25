import { AlertTriangle, ShieldAlert, TrendingUp, Zap } from "lucide-react";
import { Area, AreaChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MetricCard } from "../components/MetricCard";
import type { Alert, DashboardSummary } from "../types";

export function Dashboard({
  alerts,
  summary
}: {
  alerts: Alert[];
  summary: DashboardSummary;
  generateCase: () => void;
}) {
  const critical = alerts.filter((alert) => alert.risk_band === "critical").length;
  const high = alerts.filter((alert) => alert.risk_band === "high").length;
  const medium = alerts.filter((alert) => alert.risk_band === "medium").length;
  const riskDistribution = [
    { name: "Critical", value: critical, color: "#b42318" },
    { name: "High", value: high, color: "#b54708" },
    { name: "Medium", value: medium, color: "#116a7b" },
    { name: "Low", value: Math.max(0, alerts.length - critical - high - medium), color: "#027a48" }
  ];

  return (
    <section className="dashboard-grid">
      <div className="kpi-row">
        <MetricCard label="Open Alerts" value={alerts.length} icon={ShieldAlert} trend="backend" color="red" />
        <MetricCard label="Fraud Rate" value={`${summary.fraudRate}%`} icon={TrendingUp} trend="backend" color="amber" />
        <MetricCard label="Avg Risk Score" value={summary.avgRiskScore} icon={Zap} trend="backend" color="blue" />
        <MetricCard label="Blocked Today" value={summary.blockedToday} icon={AlertTriangle} trend="backend" color="green" />
      </div>
      <div className="charts-row">
        <div className="panel full-height">
          <h2>Real-Time Alert Trend</h2>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={summary.trend}>
              <XAxis dataKey="t" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }} />
              <Area type="monotone" dataKey="score" stroke="#b42318" fill="#b42318" fillOpacity={0.25} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="panel">
          <h2>Risk Distribution</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={riskDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value">
                {riskDistribution.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="panel full-width transaction-panel">
        <div className="transaction-panel-header">
          <div>
            <h2>Live Transaction Feed (Top 10)</h2>
            <p className="muted">Latest scored payments from the backend decision stream.</p>
          </div>
          <span className="feed-count">{summary.liveTransactions.slice(0, 10).length} visible</span>
        </div>
        <div className="transaction-feed">
          <div className="transaction-feed-head">
            <span>Transaction</span>
            <span>Merchant</span>
            <span>Amount</span>
            <span>Risk</span>
            <span>Status</span>
            <span>Time</span>
          </div>
          {summary.liveTransactions.slice(0, 10).map((txn) => (
            <div key={txn.id} className={`transaction-item status-${txn.status}`}>
              <div className="txn-pulse" />
              <div className="txn-info">
                <div className="txn-id">{txn.id}</div>
                <div className="txn-merchant">{txn.merchant}</div>
              </div>
              <div className="txn-amount">${txn.amount.toFixed(2)}</div>
              <div className="txn-score">
                <span className={`score-badge score-${txn.risk_score > 70 ? "high" : txn.risk_score > 40 ? "medium" : "low"}`}>
                  {txn.risk_score}%
                </span>
              </div>
              <div className={`txn-status status-pill ${txn.status}`}>{txn.status.toUpperCase()}</div>
              <div className="txn-time">{new Date(txn.timestamp).toLocaleTimeString()}</div>
            </div>
          ))}
          {!summary.liveTransactions.length && <p className="muted">No backend transactions yet.</p>}
        </div>
      </div>
    </section>
  );
}
