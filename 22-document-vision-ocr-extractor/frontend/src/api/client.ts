import type { ErrorEntry, EvaluationSummary, Extraction, ModelRecord, Sample } from "./types";

const apiBase = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "";

export function resolveApiUrl(path: string) {
  return path.startsWith("http") ? path : `${apiBase}${path}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(resolveApiUrl(path), init);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? body.title ?? `Request failed with ${response.status}.`);
  }
  return response.json() as Promise<T>;
}

export async function loadWorkspace() {
  const [samples, model, summary, errors] = await Promise.all([
    request<{ samples: Sample[] }>("/v1/documents/samples"),
    request<ModelRecord>("/v1/models/current"),
    request<EvaluationSummary>("/v1/evaluation/summary"),
    request<{ errors: ErrorEntry[] }>("/v1/evaluation/errors")
  ]);
  return { samples: samples.samples, model, summary, errors: errors.errors };
}

export async function extractSample(sampleId: string, profile: string) {
  return request<Extraction>("/v1/documents/extract", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sample_id: sampleId, preprocessing_profile: profile })
  });
}

export async function extractUpload(file: File, profile: string) {
  return request<Extraction>("/v1/documents/extract", {
    method: "POST",
    headers: {
      "Content-Type": file.type,
      "X-Document-Name": file.name,
      "X-Preprocessing-Profile": profile
    },
    body: file
  });
}

export async function exportExtraction(
  requestId: string,
  format: "json" | "csv",
  edits: Array<{ field: string; value: string }>
) {
  const response = await fetch(resolveApiUrl(`/v1/extractions/${requestId}/export`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ format, edits })
  });
  if (!response.ok) throw new Error("Export could not be generated.");
  const blob = await response.blob();
  const href = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.download = `extraction-${requestId}.${format}`;
  anchor.click();
  URL.revokeObjectURL(href);
}
