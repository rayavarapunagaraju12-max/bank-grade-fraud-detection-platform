import { CheckCircle2, Clock } from "lucide-react";

export function PilotReadiness() {
  const readiness = [
    ["Transaction ingestion and scoring", "Bank-Grade Portfolio"],
    ["RBAC and API protection", "Bank-Grade Portfolio"],
    ["Audited alert investigation workflow", "Bank-Grade Portfolio"],
    ["DLQ replay and model governance", "Bank-Grade Portfolio"],
    ["Cloud scaling validation", "Planned"]
  ];
  return (
    <section className="readiness-grid">
      <div className="panel full-width readiness-hero"><div><h2>Bank-Grade Portfolio Readiness</h2><p>End-to-end workflow includes audited investigation, governance, DLQ handling, and compliance evidence.</p></div><div className="readiness-score"><span>Bank Grade</span><strong>65-75%</strong></div></div>
      <div className="readiness-list">
        {readiness.map(([label, status]) => (
          <div className="readiness-item" key={label}>
            <div className={status === "Bank-Grade Portfolio" ? "readiness-icon ready" : "readiness-icon planned"}>{status === "Bank-Grade Portfolio" ? <CheckCircle2 size={18} /> : <Clock size={18} />}</div>
            <div><div className="readiness-title">{label}</div><div className="readiness-status">{status}</div></div>
          </div>
        ))}
      </div>
    </section>
  );
}
