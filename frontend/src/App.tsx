import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Bot,
  DatabaseZap,
  FileCheck2,
  FileSearch,
  Flame,
  GitBranch,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Search,
  ShieldAlert,
  ShieldCheck,
  TriangleAlert,
  Zap
} from "lucide-react";
import { setAuthToken } from "./api/client";
import { useFraudData } from "./hooks/useFraudData";
import { AlertQueue } from "./pages/AlertQueue";
import { ComplianceWorkspace } from "./pages/ComplianceWorkspace";
import { Dashboard } from "./pages/Dashboard";
import { DlqMonitor } from "./pages/DlqMonitor";
import { GraphView } from "./pages/GraphView";
import { Investigation } from "./pages/Investigation";
import { Login } from "./pages/Login";
import { LiveStream } from "./pages/LiveStream";
import { ModelGovernance } from "./pages/ModelGovernance";
import { Monitoring } from "./pages/Monitoring";
import { PilotReadiness } from "./pages/PilotReadiness";
import type { Role, Session } from "./types";

export function App() {
  const [session, setSession] = useState<Session | null>(() => {
    const raw = window.localStorage.getItem("fraudops-session");
    if (!raw) {
      return null;
    }
    try {
      const parsed = JSON.parse(raw) as Session;
      setAuthToken(parsed.token);
      return parsed;
    } catch {
      window.localStorage.removeItem("fraudops-session");
      return null;
    }
  });

  const onLogin = (nextSession: Session) => {
    setAuthToken(nextSession.token);
    window.localStorage.setItem("fraudops-session", JSON.stringify(nextSession));
    setSession(nextSession);
  };

  const logout = () => {
    setAuthToken(null);
    window.localStorage.removeItem("fraudops-session");
    setSession(null);
  };

  if (!session) {
    return <Login onLogin={onLogin} />;
  }

  return <FraudOpsConsole session={session} logout={logout} />;
}

function FraudOpsConsole({ session, logout }: { session: Session; logout: () => void }) {
  const [page, setPage] = useState(() => window.localStorage.getItem("fraudops-page") ?? "dashboard");
  const [query, setQuery] = useState("");
  const { alerts, summary, apiStatus, selected, setSelected, refresh } = useFraudData();
  const roleSet = useMemo(() => new Set<Role>(session.roles), [session.roles]);
  const canAccess = (roles: Role[]) => roles.some((role) => roleSet.has(role) || roleSet.has("admin"));

  useEffect(() => {
    window.localStorage.setItem("fraudops-page", page);
  }, [page]);

  const filtered = useMemo(
    () =>
      alerts.filter((alert) =>
        `${alert.alert_id} ${alert.transaction_id} ${alert.risk_band}`.toLowerCase().includes(query.toLowerCase())
      ),
    [alerts, query]
  );

  const generateCase = () => refresh(true).then(() => setPage("alerts"));
  const activeAlert = selected ?? filtered[0] ?? null;
  const nav = [
    { id: "dashboard", icon: LayoutDashboard, label: "Executive Dashboard", roles: ["analyst", "supervisor", "auditor", "admin"] },
    { id: "alerts", icon: ShieldAlert, label: "Fraud Alert Queue", roles: ["analyst", "supervisor", "admin"] },
    { id: "investigate", icon: FileSearch, label: "Investigation Workspace", roles: ["analyst", "supervisor", "admin"] },
    { id: "graph", icon: GitBranch, label: "Graph Visualization", roles: ["analyst", "supervisor", "admin"] },
    { id: "stream", icon: Zap, label: "Live Stream", roles: ["analyst", "supervisor", "admin"] },
    { id: "compliance", icon: FileCheck2, label: "Compliance Reports", roles: ["auditor", "supervisor", "admin"] },
    { id: "governance", icon: ShieldCheck, label: "Model Governance", roles: ["supervisor", "auditor", "admin"] },
    { id: "dlq", icon: TriangleAlert, label: "DLQ Monitoring", roles: ["supervisor", "auditor", "admin"] },
    { id: "monitoring", icon: BarChart3, label: "Model Monitoring", roles: ["supervisor", "auditor", "admin"] },
    { id: "readiness", icon: ListChecks, label: "Pilot Readiness", roles: ["supervisor", "auditor", "admin"] }
  ] satisfies Array<{ id: string; icon: typeof LayoutDashboard; label: string; roles: Role[] }>;
  const visibleNav = nav.filter((item) => canAccess(item.roles));

  useEffect(() => {
    if (!visibleNav.some((item) => item.id === page)) {
      setPage(visibleNav[0]?.id ?? "dashboard");
    }
  }, [page, visibleNav]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <Flame size={24} className="flame" /> FraudOps AI
        </div>
        <div className="online-badge">Live</div>
        <div className="role-card">
          <span>{session.username}</span>
          <strong>{session.roles.join(" · ")}</strong>
        </div>
        {visibleNav.map(({ id, icon: Icon, label }) => (
          <button className={page === id ? "nav active" : "nav"} onClick={() => setPage(id)} key={id}>
            <Icon size={18} />
            {label}
          </button>
        ))}
        <button className="nav logout" onClick={logout}>
          <LogOut size={18} />
          Sign out
        </button>
      </aside>
      <main className="main">
        <header className="topbar">
          <div className="search">
            <Search size={18} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search alerts, transactions, risk bands"
            />
          </div>
          <button className="action" onClick={generateCase}>
            <Bot size={16} />
            Generate AI Fraud Case
          </button>
          <span className="pill user-pill"><DatabaseZap size={14} />{session.roles[0]}</span>
          <span className={apiStatus.connected ? "pill connected" : "pill offline"}>{apiStatus.label}</span>
        </header>
        {page === "dashboard" && <Dashboard alerts={alerts} summary={summary} generateCase={generateCase} />}
        {page === "alerts" && (
          <AlertQueue alerts={filtered} select={setSelected} refresh={() => refresh(true)} />
        )}
        {page === "investigate" && <Investigation alert={activeAlert} refresh={() => refresh(false)} />}
        {page === "graph" && <GraphView alert={activeAlert} />}
        {page === "compliance" && <ComplianceWorkspace alert={activeAlert} />}
        {page === "governance" && <ModelGovernance />}
        {page === "dlq" && <DlqMonitor />}
        {page === "monitoring" && <Monitoring />}
        {page === "readiness" && <PilotReadiness />}
        {page === "stream" && <LiveStream transactions={summary.liveTransactions} refresh={refresh} />}
      </main>
    </div>
  );
}
