import { useEffect, useMemo, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import { GitBranch, Network, RadioTower, Route } from "lucide-react";
import { getGraph } from "../api/fraud";
import type { Alert } from "../types";

export function GraphView({ alert }: { alert?: Alert | null }) {
  const [remoteGraph, setRemoteGraph] = useState<any>(null);
  const account = alert?.payload?.transaction?.account_id ?? "no_account_selected";
  const transaction = alert?.payload?.transaction ?? {};
  const score = alert?.payload?.score ?? {};
  const localElements = [
    { data: { id: account, label: account } },
    { data: { id: transaction.device_id ?? "device", label: transaction.device_id ?? "device" } },
    { data: { id: transaction.ip_address ?? "ip", label: transaction.ip_address ?? "ip" } },
    { data: { id: transaction.merchant_id ?? "merchant", label: transaction.merchant_id ?? "merchant" } },
    { data: { source: account, target: transaction.device_id ?? "device", label: "USED_DEVICE" } },
    { data: { source: account, target: transaction.ip_address ?? "ip", label: "USED_IP" } },
    { data: { source: account, target: transaction.merchant_id ?? "merchant", label: "PAID_MERCHANT" } }
  ];
  useEffect(() => {
    if (account !== "no_account_selected") {
      getGraph(account).then(setRemoteGraph).catch(() => setRemoteGraph(null));
    }
  }, [account]);
  const elements = useMemo(() => {
    if (!remoteGraph?.nodes?.length) {
      return localElements;
    }
    return [
      ...remoteGraph.nodes.map((node: any) => ({ data: { id: node.id, label: node.label ?? node.id } })),
      ...remoteGraph.edges.map((edge: any, index: number) => ({
        data: { id: `edge_${index}`, source: edge.source, target: edge.target, label: edge.label }
      }))
    ];
  }, [remoteGraph, account, transaction.device_id, transaction.ip_address, transaction.merchant_id]);
  return (
    <section className="graph-layout">
      <div className="panel graph-risk-panel">
        <h2>Fraud Ring Signals</h2>
        <div className="model-signal-grid compact">
          <div className="model-signal-card tone-watch"><div className="model-signal-icon"><GitBranch size={18} /></div><span>Graph score</span><strong>{Math.round((score.graph_score ?? 0) * 100)}%</strong><p>Shared entity risk</p></div>
          <div className="model-signal-card tone-good"><div className="model-signal-icon"><Network size={18} /></div><span>Nodes</span><strong>{remoteGraph?.nodes?.length ?? elements.filter((item: any) => !item.data.source).length}</strong><p>Current account neighborhood</p></div>
          <div className="model-signal-card tone-watch"><div className="model-signal-icon"><RadioTower size={18} /></div><span>Device/IP</span><strong>{transaction.device_id ? "linked" : "-"}</strong><p>{transaction.ip_address ?? "No IP selected"}</p></div>
          <div className="model-signal-card tone-good"><div className="model-signal-icon"><Route size={18} /></div><span>Band</span><strong>{alert?.risk_band ?? "-"}</strong><p>{account}</p></div>
        </div>
      </div>
      <div className="panel full-width">
        <h2>Entity Graph Exploration</h2>
        <CytoscapeComponent
          elements={elements}
          style={{ width: "100%", height: "560px" }}
          layout={{ name: "cose" }}
          stylesheet={[
            { selector: "node", style: { label: "data(label)", "background-color": "#116a7b", color: "#ffffff", "font-size": "12px" } },
            { selector: "edge", style: { label: "data(label)", width: 2, "line-color": "#b54708", "font-size": "10px" } }
          ]}
        />
      </div>
    </section>
  );
}
