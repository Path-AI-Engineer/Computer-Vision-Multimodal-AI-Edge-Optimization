import type {
  CorpusItem,
  ErrorItem,
  EvaluationSummary,
  IndexBenchmark,
  IndexManifest,
  IndexMode,
  ModelBundle,
  SearchMode,
  SearchResponse,
  SearchState,
  SessionReply
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as { detail?: string; reason_code?: string };
    throw new Error(payload.detail ?? payload.reason_code ?? `Request failed (${response.status}).`);
  }
  return (await response.json()) as T;
}

export const api = {
  ready: () => request<{ status: string; corpus_images: number }>("/ready"),
  corpus: async () => (await request<{ items: CorpusItem[] }>("/v1/corpus")).items,
  searchText: (payload: {
    query: string;
    mode: SearchMode;
    index_mode: IndexMode;
    top_k: number;
    alpha: number;
    negative_terms?: string[];
    category?: string;
    color?: string;
    has_people?: boolean;
  }) => request<SearchResponse>("/v1/search/text", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  }),
  searchImage: (imageId: string, indexMode: IndexMode) =>
    request<SearchResponse>("/v1/search/image", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ image_id: imageId, index_mode: indexMode, top_k: 6 })
    }),
  uploadImage: (file: File) => request<SearchResponse>("/v1/search/image-upload", {
    method: "POST",
    headers: { "content-type": file.type },
    body: file
  }),
  createSession: async (mode: SearchMode, indexMode: IndexMode) => {
    const payload = await request<{ state: SearchState }>("/v1/sessions", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ top_k: 6, mode, index_mode: indexMode })
    });
    return payload.state;
  },
  sendMessage: (sessionId: string, message: string) =>
    request<SessionReply>(`/v1/sessions/${sessionId}/messages`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ message })
    }),
  deleteSession: (sessionId: string) => fetch(`/v1/sessions/${sessionId}`, { method: "DELETE" }),
  evaluation: () => request<EvaluationSummary>("/v1/evaluation/summary"),
  indexBenchmark: () => request<IndexBenchmark>("/v1/evaluation/index"),
  errors: async () => (await request<{ items: ErrorItem[] }>("/v1/evaluation/errors")).items,
  model: () => request<ModelBundle>("/v1/models/current"),
  index: () => request<IndexManifest>("/v1/indexes/current")
};

