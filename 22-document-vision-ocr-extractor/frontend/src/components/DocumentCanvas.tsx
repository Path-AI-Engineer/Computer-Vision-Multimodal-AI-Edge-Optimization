import type { Extraction, FieldName } from "../api/types";
import { resolveApiUrl } from "../api/client";

const colors: Record<FieldName, string> = {
  company: "#ec4899",
  date: "#8b5cf6",
  address: "#0ea5e9",
  total: "#f97316"
};

export function DocumentCanvas({ extraction, activeField, onField }: { extraction: Extraction; activeField: FieldName | null; onField: (field: FieldName) => void }) {
  if (!extraction.image_url) {
    return <div className="no-preview"><span>UP</span><strong>Upload preview is ephemeral</strong><p>The server does not persist private document bytes in this release.</p></div>;
  }
  return (
    <div className="document-canvas">
      <img src={resolveApiUrl(extraction.image_url)} alt={`Receipt ${extraction.source_name}`} />
      <svg viewBox={`0 0 ${extraction.width} ${extraction.height}`} role="img" aria-label="Document with extraction evidence regions">
        {extraction.fields.flatMap((field) => field.boxes.map((box, index) => {
          const [x1, y1, x2, y2] = box;
          return <g key={`${field.field}-${index}`} className={activeField === field.field ? "box-active" : ""} onClick={() => onField(field.field)}>
            <rect x={x1} y={y1} width={x2 - x1} height={y2 - y1} style={{ "--box-color": colors[field.field] } as React.CSSProperties} />
            <text x={x1 + 6} y={Math.max(18, y1 - 6)} style={{ "--box-color": colors[field.field] } as React.CSSProperties}>{field.field}</text>
          </g>;
        }))}
      </svg>
    </div>
  );
}
