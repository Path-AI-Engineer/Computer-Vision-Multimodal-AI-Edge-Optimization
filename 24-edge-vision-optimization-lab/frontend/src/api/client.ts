import type { BenchmarkSummary, Environment, ParetoReport, ParityComparison, Prediction, PruningReport, Readiness, Sample, Variant } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: `Request failed with ${response.status}.` }));
    throw new Error(payload.detail ?? "Request failed.");
  }
  return response.json() as Promise<T>;
}

export const api = {
  ready: () => request<Readiness>("/ready"),
  variants: async () => (await request<{ data: Variant[] }>("/v1/variants")).data,
  samples: async () => (await request<{ data: Sample[] }>("/v1/samples")).data,
  benchmark: () => request<BenchmarkSummary>("/v1/benchmarks/summary"),
  pareto: () => request<ParetoReport>("/v1/benchmarks/pareto"),
  environment: () => request<Environment>("/v1/benchmarks/environment"),
  parity: async () => (await request<{ comparisons: ParityComparison[] }>("/v1/parity/summary")).comparisons,
  pruning: () => request<PruningReport>("/v1/pruning/summary"),
  predict: (variantId: string, sampleId: string) => request<Prediction>(`/v1/predictions?variant_id=${encodeURIComponent(variantId)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ sample_id: sampleId, top_k: 3 }) })
};
