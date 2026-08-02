import type { Decision } from "../api/types";

export function DecisionBadge({ decision }: { decision: Decision }) {
  return <span className={`decision decision-${decision.toLowerCase()}`}>{decision}</span>;
}

