import { useCallback, useEffect, useState } from "react";
import { emptySummary, generateFraudCase, getAlerts, getDashboardSummary, getHealth } from "../api/fraud";
import type { Alert, ApiStatus, DashboardSummary } from "../types";

export function useFraudData() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [apiStatus, setApiStatus] = useState<ApiStatus>({ connected: false, label: "Connecting" });
  const [selected, setSelected] = useState<Alert | null>(null);

  const refresh = useCallback(async (generateNew = false) => {
    const generated = generateNew ? await generateFraudCase() : null;
    const [freshAlerts, freshSummary] = await Promise.all([getAlerts(), getDashboardSummary()]);
    const generatedTransactionId = generated?.transaction?.transaction_id;
    const generatedAlert = freshAlerts.find((alert) => alert.transaction_id === generatedTransactionId);
    setAlerts(freshAlerts);
    setSummary(freshSummary);
    setSelected(generatedAlert ?? freshAlerts[0] ?? null);
    setApiStatus({ connected: true, label: "API ok" });
  }, []);

  useEffect(() => {
    let active = true;
    getHealth()
      .then((health) => active && setApiStatus({ connected: true, label: `API ${health.status}` }))
      .catch(() => active && setApiStatus({ connected: false, label: "API offline" }));
    refresh().catch(() => active && setApiStatus({ connected: false, label: "API offline" }));
    const timer = window.setInterval(() => {
      refresh().catch(() => active && setApiStatus({ connected: false, label: "API offline" }));
    }, 5000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [refresh]);

  return { alerts, summary, apiStatus, selected, setSelected, refresh };
}
