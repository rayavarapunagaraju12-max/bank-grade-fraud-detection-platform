import { useEffect, useState } from "react";
import { CheckCircle2, Rocket, Save, ShieldCheck } from "lucide-react";
import { getModelVersions, registerModelVersion, transitionModelVersion } from "../api/fraud";
import type { ModelVersion } from "../types";

export function ModelGovernance() {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [status, setStatus] = useState("Loading");
  const [version, setVersion] = useState(() => new Date().toISOString().slice(0, 10));

  const refresh = () =>
    getModelVersions()
      .then((items) => {
        setModels(items);
        setStatus(`${items.length} versions`);
      })
      .catch(() => setStatus("Unavailable"));

  useEffect(() => {
    refresh();
  }, []);

  const register = () =>
    registerModelVersion({
      model_name: "xgboost",
      version,
      artifact_path: "training/model_registry/xgboost.joblib",
      metrics: { auc: 0.91, precision: 0.84 }
    }).then(refresh);

  const transition = (modelId: string, next: string) =>
    transitionModelVersion(modelId, next)
      .then(refresh)
      .catch(() => setStatus("Transition rejected"));

  return (
    <section className="panel full-width">
      <div className="section-header">
        <div>
          <h2>Model Governance</h2>
          <p className="muted">Register, validate, approve, and deploy model versions with audit history.</p>
        </div>
        <div className="inline-form">
          <input value={version} onChange={(event) => setVersion(event.target.value)} />
          <button className="panelAction" onClick={register}><Save size={16} />Register</button>
        </div>
      </div>
      <div className="compliance-stat"><span>Registry</span><strong>{status}</strong></div>
      <table className="alerts-table">
        <thead>
          <tr><th>Model</th><th>Version</th><th>Status</th><th>Metrics</th><th>Approved by</th><th>Actions</th></tr>
        </thead>
        <tbody>
          {models.map((model) => (
            <tr key={model.model_id}>
              <td>{model.model_name}</td>
              <td className="alert-id">{model.version}</td>
              <td><span className={`band ${model.status === "deployed" ? "low" : model.status === "approved" ? "medium" : "high"}`}>{model.status}</span></td>
              <td>{Object.entries(model.metrics || {}).map(([key, value]) => `${key}: ${value}`).join(", ") || "-"}</td>
              <td>{model.approved_by ?? "-"}</td>
              <td className="button-row">
                {model.status === "draft" && <button className="icon-action" onClick={() => transition(model.model_id, "validated")} title="Validate"><CheckCircle2 size={15} /></button>}
                {model.status === "validated" && <button className="icon-action" onClick={() => transition(model.model_id, "approved")} title="Approve"><ShieldCheck size={15} /></button>}
                {model.status === "approved" && <button className="icon-action" onClick={() => transition(model.model_id, "deployed")} title="Deploy"><Rocket size={15} /></button>}
              </td>
            </tr>
          ))}
          {!models.length && <tr><td colSpan={6}>No model versions registered.</td></tr>}
        </tbody>
      </table>
    </section>
  );
}
