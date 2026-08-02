export function MetricCard({ eyebrow, value, detail, tone = "default" }: { eyebrow: string; value: string; detail: string; tone?: "default" | "good" | "warning" }) {
  return (
    <article className={`metric-card metric-${tone}`}>
      <span>{eyebrow}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

