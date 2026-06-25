import { useEffect, useState } from "react";
import { RefreshCw, RotateCcw, TriangleAlert } from "lucide-react";
import { getDlqMessages, retryDlqMessage } from "../api/fraud";
import type { DlqMessage } from "../types";

export function DlqMonitor() {
  const [messages, setMessages] = useState<DlqMessage[]>([]);
  const [status, setStatus] = useState("Loading");

  const refresh = () => {
    setStatus("Loading");
    getDlqMessages()
      .then((items) => {
        setMessages(items);
        setStatus(`${items.length} messages`);
      })
      .catch(() => setStatus("Unavailable"));
  };

  useEffect(refresh, []);

  const retry = (eventId: string) =>
    retryDlqMessage(eventId)
      .then(refresh)
      .catch(() => setStatus("Retry failed"));

  return (
    <section className="panel full-width">
      <div className="section-header">
        <div>
          <h2>Kafka Dead-Letter Queue</h2>
          <p className="muted">Failed stream messages are captured here for audit and replay.</p>
        </div>
        <button className="panelAction" onClick={refresh}><RefreshCw size={16} />Refresh</button>
      </div>
      <div className="compliance-stat"><span>Status</span><strong>{status}</strong></div>
      <table className="alerts-table">
        <thead>
          <tr><th>Event</th><th>Topic</th><th>Error</th><th>Status</th><th>Time</th><th>Action</th></tr>
        </thead>
        <tbody>
          {messages.map((message) => (
            <tr key={message.event_id}>
              <td className="alert-id">{message.event_id}</td>
              <td>{message.source_topic}</td>
              <td>{message.error}</td>
              <td><span className="status-badge">{message.status}</span></td>
              <td className="timestamp">{new Date(message.created_at).toLocaleString()}</td>
              <td>
                <button className="icon-action" onClick={() => retry(message.event_id)} title="Replay message">
                  <RotateCcw size={15} />
                </button>
              </td>
            </tr>
          ))}
          {!messages.length && (
            <tr><td colSpan={6}><TriangleAlert size={15} /> No failed messages found.</td></tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
