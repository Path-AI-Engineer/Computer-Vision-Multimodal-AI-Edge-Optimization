export type Sample = { sample_id: string; image_url: string; label: string; scope: string };
export type PredictionItem = {
  class_id: number;
  class_name: string;
  species: string;
  probability: number;
};
export type Prediction = {
  request_id: string;
  model_version: string;
  class_name: string;
  species: string;
  top_k: PredictionItem[];
  confidence: number;
  abstained: boolean;
  threshold: number;
  preprocessing_version: string;
  latency_ms: number;
  warnings: string[];
  input: { width: number; height: number; format: string; sha256_prefix: string };
};

const configured = import.meta.env.VITE_API_URL as string | undefined;
export const API_URL = configured?.replace(/\/$/, "") ?? "";

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(payload.detail ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getJson<T>(path: string): Promise<T> {
  return parse<T>(await fetch(`${API_URL}${path}`));
}

export async function classify(file: Blob, filename: string): Promise<Prediction> {
  const body = new FormData();
  body.append("image", file, filename);
  return parse<Prediction>(
    await fetch(`${API_URL}/v1/predictions?top_k=5`, { method: "POST", body })
  );
}

export async function classifySample(sample: Sample): Promise<Prediction> {
  const response = await fetch(`${API_URL}${sample.image_url}`);
  if (!response.ok) throw new Error("The selected evidence image could not be loaded.");
  return classify(await response.blob(), `${sample.sample_id}.png`);
}

export function assetUrl(path: string): string {
  return `${API_URL}${path}`;
}
