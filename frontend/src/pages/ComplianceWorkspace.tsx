import { useState } from "react";
import { Database, FileCheck2, RefreshCw, ShieldAlert } from "lucide-react";
import { api } from "../api/client";
import { getWatchlistStatus, refreshDemoWatchlists, refreshOfficialWatchlists } from "../api/fraud";
import type { Alert, ComplianceState } from "../types";

export function ComplianceWorkspace({ alert }: { alert?: Alert | null }) {
  const [state, setState] = useState<ComplianceState>({});
  const sampleCase = {
    case_id: alert?.alert_id ?? "case_demo_india",
    account_id: alert?.payload?.transaction?.account_id ?? "acct_42",
    customer_name: "Demo Customer",
    country: "IN",
    pan: "ABCDE1234F",
    risk_score: alert?.score ?? 0.91,
    risk_band: alert?.risk_band ?? "critical",
    reason: "High risk transaction pattern with possible watchlist exposure.",
    transactions: [alert?.payload?.transaction ?? { transaction_id: "txn_demo_001", account_id: "acct_42", amount: 9250 }]
  };
  const refresh = () =>
    refreshDemoWatchlists().then((res) =>
      getWatchlistStatus().then((status) => setState({ ...state, status, screening: res, error: undefined }))
    );
  const refreshOfficial = () =>
    refreshOfficialWatchlists()
      .then((res) => getWatchlistStatus().then((status) => setState({ ...state, status, screening: res, error: undefined })))
      .catch((error) => setState({ ...state, error: error?.response?.data?.detail ?? "Official feed refresh unavailable" }));
  const screen = () =>
    api.post("/compliance/sanctions/screen", { name: "North Korea Trading Corp", country: "KP" }).then((res) =>
      setState({ ...state, screening: res.data })
    );
  const report = () =>
    api.post("/compliance/reports/india-str", sampleCase).then((res) =>
      setState({ ...state, report: res.data.report, validation: res.data.validation })
    );
  return (
    <section className="compliance-grid">
      <div className="panel">
        <h2>Watchlist Ingestion</h2>
        <div className="button-row">
          <button className="panelAction" onClick={refresh}><RefreshCw size={16} />Demo feeds</button>
          <button className="panelAction secondary" onClick={refreshOfficial}><Database size={16} />Official feeds</button>
        </div>
        <div className="compliance-stat"><span>Loaded entries</span><strong>{state.status?.entries ?? "Not loaded"}</strong></div>
        {state.error && <div className="form-error">{state.error}</div>}
        <div className="feed-list">
          {(state.status?.recent_ingestions ?? []).slice(0, 5).map((item: any) => (
            <div key={item.ingestion_id}>
              <span>{item.source}</span>
              <strong>{item.status} · {item.records_loaded}/{item.records_seen}</strong>
            </div>
          ))}
        </div>
      </div>
      <div className="panel">
        <h2>Sanctions Screening</h2>
        <button className="panelAction" onClick={screen}><ShieldAlert size={16} />Screen sample party</button>
        <div className="compliance-stat"><span>Confidence</span><strong>{state.screening?.confidence ?? "-"}</strong></div>
        <div className="compliance-detail">{state.screening?.rule_triggered ?? "No screening result yet"}</div>
      </div>
      <div className="panel full-width">
        <h2>India STR-Style Report</h2>
        <button className="panelAction" onClick={report}><FileCheck2 size={16} />Generate India STR draft</button>
        <div className="report-summary">
          <div><span>Report ID</span><strong>{state.report?.report_id ?? "-"}</strong></div>
          <div><span>Status</span><strong>{state.report?.status ?? "-"}</strong></div>
          <div><span>Validation</span><strong>{state.validation?.valid === true ? "Valid" : state.validation?.valid === false ? "Needs review" : "-"}</strong></div>
        </div>
      </div>
    </section>
  );
}
