import { FormEvent, useState } from "react";
import { Flame, LockKeyhole, ShieldCheck } from "lucide-react";
import { login } from "../api/fraud";
import type { Session } from "../types";

export function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    login(username, password)
      .then(onLogin)
      .catch(() => setError("Invalid credentials or API unavailable"))
      .finally(() => setLoading(false));
  };

  return (
    <main className="login-shell">
      <form className="login-panel" onSubmit={submit}>
        <div className="login-brand"><Flame size={26} /> FraudOps AI</div>
        <div className="login-title">
          <ShieldCheck size={24} />
          <h1>Secure Console</h1>
        </div>
        <label>
          <span>Username</span>
          <input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
        </label>
        <label>
          <span>Password</span>
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            autoComplete="current-password"
          />
        </label>
        {error && <div className="form-error">{error}</div>}
        <button className="action login-action" disabled={loading}>
          <LockKeyhole size={16} />
          {loading ? "Signing in" : "Sign in"}
        </button>
        <div className="login-roles">
          <span>admin/admin123</span>
          <span>analyst/analyst123</span>
          <span>auditor/auditor123</span>
        </div>
      </form>
    </main>
  );
}
