import type { ReactNode } from "react";

export function MetricCard({ eyebrow, value, detail, accent, children }: { eyebrow: string; value: string; detail: string; accent?: string; children?: ReactNode }) {
  return (
    <article className="metric-card" style={{ "--metric-accent": accent ?? "#65e6d4" } as React.CSSProperties}>
      <span>{eyebrow}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
      {children}
    </article>
  );
}

