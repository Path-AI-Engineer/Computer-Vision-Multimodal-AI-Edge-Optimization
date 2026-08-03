import { Icon, type IconName } from "./Icon";

export function MetricCard({ label, value, detail, icon, tone = "blue" }: { label: string; value: string; detail: string; icon: IconName; tone?: "blue" | "green" | "amber" | "violet" }) {
  return <article className={`metric-card tone-${tone}`}><div className="metric-icon"><Icon name={icon}/></div><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}
