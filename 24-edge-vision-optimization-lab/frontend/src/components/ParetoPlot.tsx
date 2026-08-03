import type { BenchmarkRow } from "../api/types";

const colors: Record<string, string> = { "pytorch-fp32": "#6fb7ff", "pytorch-pruned-unstructured": "#f3a34c", "structured-channel-experimental": "#af8cff", "onnx-fp32": "#52d6b4", "onnx-int8-ptq": "#ff7285" };

export function ParetoPlot({ rows, frontierIds }: { rows: BenchmarkRow[]; frontierIds: Set<string> }) {
  const maxLatency = Math.max(...rows.map((item) => item.p50_ms), 0.001);
  const minF1 = Math.min(...rows.map((item) => item.macro_f1), 0.8);
  const x = (value: number) => 56 + (value / maxLatency) * 420;
  const y = (value: number) => 225 - ((value - minF1) / Math.max(1 - minF1, 0.01)) * 170;
  return <div className="pareto-plot" role="img" aria-label="Macro F1 versus median latency Pareto plot">
    <svg viewBox="0 0 520 260">
      <defs><linearGradient id="plotFill" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#6fb7ff" stopOpacity=".13"/><stop offset="1" stopColor="#52d6b4" stopOpacity="0"/></linearGradient></defs>
      <rect x="48" y="28" width="440" height="205" rx="12" fill="url(#plotFill)"/>
      {[0, 1, 2, 3].map((tick) => <line key={`h${tick}`} x1="48" x2="488" y1={55 + tick * 52} y2={55 + tick * 52} className="gridline"/>)}
      {[0, 1, 2, 3, 4].map((tick) => <line key={`v${tick}`} y1="28" y2="233" x1={56 + tick * 105} x2={56 + tick * 105} className="gridline"/>)}
      <text x="255" y="254" className="axis-label">median latency · lower is better</text>
      <text x="12" y="152" transform="rotate(-90 12 152)" className="axis-label">macro F1 · higher is better</text>
      {rows.map((row) => <g key={row.variant_id} className={frontierIds.has(row.variant_id) ? "frontier-point" : "plot-point"}>
        <circle cx={x(row.p50_ms)} cy={y(row.macro_f1)} r={5 + Math.max(0, Math.min(8, row.size_mb * 2000))} fill={colors[row.variant_id] ?? "#fff"}/>
        <text x={x(row.p50_ms) + 12} y={y(row.macro_f1) - 10}>{row.display_name}</text>
      </g>)}
    </svg>
  </div>;
}
