import { useEffect, useState } from "react";
import { Pause, Play, Radio, Wifi, Zap } from "lucide-react";
import { generateStreamTransaction } from "../api/fraud";
import type { LiveTransaction } from "../types";

export function LiveStream({
  transactions,
  refresh
}: {
  transactions: LiveTransaction[];
  refresh: () => Promise<void>;
}) {
  const [generatedCount, setGeneratedCount] = useState(0);
  const [activeStream, setActiveStream] = useState(true);
  const [rate, setRate] = useState(1);

  useEffect(() => {
    let active = true;
    setGeneratedCount(0);
    const timer = window.setInterval(() => {
      if (!active || !activeStream) {
        return;
      }
      setGeneratedCount((current) => {
        generateStreamTransaction()
          .then(() => refresh())
          .catch(() => undefined);
        return current + 1;
      });
    }, Math.max(1000 / rate, 250));
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [refresh, activeStream, rate]);

  return (
    <section className="live-stream">
      <div className="stream-header"><h2>Live Transaction Stream</h2><div className="stream-indicator"><Wifi size={16} className="pulse" /><span>{transactions.length} backend transactions - replay {generatedCount}/25</span></div></div>
      <div className="stream-controls">
        <button className="panelAction" onClick={() => setActiveStream((value) => !value)}>
          {activeStream ? <Pause size={16} /> : <Play size={16} />}
          {activeStream ? "Pause" : "Resume"}
        </button>
        <button className="panelAction secondary" onClick={() => generateStreamTransaction().then(() => refresh())}>
          <Zap size={16} />Generate one
        </button>
        <label className="segmented-control">
          <Radio size={15} />
          <select value={rate} onChange={(event) => setRate(Number(event.target.value))}>
            <option value={1}>1 TPS demo</option>
            <option value={2}>2 TPS demo</option>
            <option value={4}>4 TPS demo</option>
          </select>
        </label>
        <span className={activeStream ? "pill connected" : "pill offline"}>{activeStream ? "stream active" : "stream paused"}</span>
      </div>
      <div className="stream-container">
        {transactions.map((txn) => (
          <div key={txn.id} className={`stream-card status-${txn.status}`}>
            <div className="card-header"><div className="card-title">{txn.merchant}</div><div className={`card-status ${txn.status}`}>{txn.status.toUpperCase()}</div></div>
            <div className="card-body">
              <div className="row"><span className="label">Transaction:</span><span className="value mono">{txn.id}</span></div>
              <div className="row"><span className="label">Amount:</span><span className="value highlight">${txn.amount.toFixed(2)}</span></div>
              <div className="row"><span className="label">AI Risk Score:</span><div className="risk-meter"><div className="meter-fill" style={{ width: `${txn.risk_score}%`, background: txn.risk_score > 70 ? "#b42318" : txn.risk_score > 40 ? "#b54708" : "#027a48" }} /><span className="meter-text">{txn.risk_score}%</span></div></div>
            </div>
          </div>
        ))}
        {!transactions.length && <p className="muted">No backend stream records yet.</p>}
      </div>
    </section>
  );
}
