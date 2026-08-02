import type {
  CurrentModel,
  ErrorGallery,
  EvaluationSummary,
  Inspection,
  ModelComparison,
  Sample,
  ThresholdPoint
} from "./types";

const API_URL = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

export function resolveApiUrl(path: string): string {
  return path.startsWith("http") ? path : `${API_URL}${path}`;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Request failed." }));
    throw new Error(payload.detail ?? `Request failed with status ${response.status}.`);
  }
  return response.json() as Promise<T>;
}

export async function loadWorkspace() {
  const [model, summary, thresholds, errors, comparison, samples] = await Promise.all([
    requestJson<CurrentModel>("/v1/models/current"),
    requestJson<EvaluationSummary>("/v1/evaluation/summary"),
    requestJson<ThresholdPoint[]>("/v1/evaluation/thresholds"),
    requestJson<ErrorGallery>("/v1/evaluation/errors"),
    requestJson<ModelComparison>("/v1/evaluation/models"),
    requestJson<Sample[]>("/v1/samples")
  ]);
  return { model, summary, thresholds, errors, comparison, samples };
}

export async function runInspection(input: {
  sampleId?: string;
  file?: File;
  pixelThreshold: number;
}): Promise<Inspection> {
  const form = new FormData();
  if (input.sampleId) form.append("sample_id", input.sampleId);
  if (input.file) form.append("image", input.file);
  form.append("pixel_threshold", input.pixelThreshold.toFixed(2));
  return requestJson<Inspection>("/v1/inspections", { method: "POST", body: form });
}
