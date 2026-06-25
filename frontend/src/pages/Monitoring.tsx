import { Activity, AlertTriangle, CheckCircle2, Clock, DatabaseZap, RefreshCw, TrendingUp } from "lucide-react";
import { MetricCard } from "../components/MetricCard";

export function Monitoring() {
  const signals = [
    { label: "Data Drift", value: "0.11 PSI", state: "Stable", tone: "good", icon: TrendingUp },
    { label: "Prediction Drift", value: "Watch", state: "Within review band", tone: "watch", icon: AlertTriangle },
    { label: "Artifact Status", value: "Loaded", state: "Latest model active", tone: "good", icon: DatabaseZap },
    { label: "Retrain Window", value: "14 days", state: "No urgent retrain", tone: "good", icon: RefreshCw }
  ];

  return (
    <section className="monitoring-grid">
      <MetricCard label="Data Drift (PSI)" value="0.11" icon={TrendingUp} trend="Stable" color="green" />
      <MetricCard label="Prediction Drift" value="Watch" icon={AlertTriangle} trend="Monitor" color="amber" />
      <MetricCard label="Model AUC" value="artifact" icon={Activity} trend="loaded" color="blue" />
      <MetricCard label="Latency (p95)" value="<100ms" icon={Clock} trend="target" color="green" />
      <div className="panel full-width model-health-panel">
        <div className="model-health-header">
          <div>
            <h2>Model Performance & Retraining Signals</h2>
            <p className="muted">Current model is serving live fraud scores with no immediate retraining trigger.</p>
          </div>
          <div className="model-health-verdict">
            <CheckCircle2 size={18} />
            Client ready
          </div>
        </div>
        <div className="model-signal-grid">
          {signals.map((signal) => {
            const Icon = signal.icon;
            return (
              <div key={signal.label} className={`model-signal-card tone-${signal.tone}`}>
                <div className="model-signal-icon"><Icon size={18} /></div>
                <span>{signal.label}</span>
                <strong>{signal.value}</strong>
                <p>{signal.state}</p>
              </div>
            );
          })}
        </div>
        <div className="model-retrain-strip">
          <div>
            <span>Next action</span>
            <strong>Continue monitoring</strong>
          </div>
          <div>
            <span>Trigger rule</span>
            <strong>Retrain when drift crosses threshold</strong>
          </div>
          <div>
            <span>Business impact</span>
            <strong>Low operational risk</strong>
          </div>
        </div>
      </div>
    </section>
  );
}
