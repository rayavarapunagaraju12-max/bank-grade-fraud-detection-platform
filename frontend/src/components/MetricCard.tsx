import type { LucideIcon } from "lucide-react";

export function MetricCard({
  label,
  value,
  icon: Icon,
  trend,
  color
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend: string;
  color: "red" | "amber" | "blue" | "green";
}) {
  return (
    <div className={`metric-card ${color}`}>
      <div className="metric-header">
        <Icon size={20} className="metric-icon" />
        <span className="metric-trend">{trend}</span>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );
}
