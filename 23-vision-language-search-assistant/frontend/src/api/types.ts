export type View = "search" | "assistant" | "benchmark" | "errors" | "model";
export type SearchMode = "bm25" | "semantic" | "hybrid";
export type IndexMode = "exact" | "approximate";

export interface Caption {
  caption_id: string;
  text: string;
}

export interface CorpusItem {
  image_id: string;
  filename: string;
  image_url: string;
  split: string;
  category: string;
  colors: string[];
  has_people: boolean;
  captions: Caption[];
}

export interface ScoreBreakdown {
  semantic: number;
  lexical: number;
  hybrid: number;
  alpha: number;
}

export interface SearchResult {
  rank: number;
  image_id: string;
  image_url: string;
  category: string;
  colors: string[];
  score: number;
  evidence_captions: Caption[];
  score_breakdown: ScoreBreakdown;
  reason_codes: string[];
}

export interface SearchResponse {
  status: "COMPLETED" | "INSUFFICIENT_RESULTS";
  query: string;
  mode: SearchMode;
  index_mode: IndexMode;
  model_version: string;
  index_version: string;
  latency_ms: number;
  results: SearchResult[];
  explanation: string;
  citations: string[];
  evidence_boundary: string;
  upload_boundary?: string;
}

export interface SearchState {
  session_id: string;
  positive_query: string;
  negative_terms: string[];
  filters: Record<string, string | boolean>;
  previous_result_ids: string[];
  selected_image_id: string | null;
  model_version: string;
  index_version: string;
  top_k: number;
  mode: SearchMode;
  index_mode: IndexMode;
}

export interface SessionReply {
  intent: string;
  reason_code: string;
  state: SearchState;
  answer: string;
  search: SearchResponse | null;
}

export interface MetricSet {
  recall_at_1: number;
  recall_at_5: number;
  recall_at_10: number;
  mrr: number;
  median_rank: number;
  mean_rank: number;
}

export interface EvaluationSummary {
  status: string;
  dataset: string;
  images: number;
  captions: number;
  queries: number;
  methods: Record<SearchMode, MetricSet>;
  random_reference: Record<string, number>;
  claim_boundary: string;
}

export interface IndexBenchmark {
  status: string;
  exact_index: string;
  approximate_index: string;
  recall_at_5_vs_exact: number;
  exact_latency_ms_mean: number;
  approximate_latency_ms_mean: number;
  embedding_memory_bytes: number;
  claim_boundary: string;
}

export interface ErrorItem {
  query_id: string;
  query: string;
  risk: string;
  finding: string;
  mitigation: string;
}

export interface ModelBundle {
  bundle_id: string;
  status: string;
  model_version: string;
  index_version: string;
  dataset: string;
  capabilities: string[];
  official_benchmarks: Record<string, string>;
  evidence_boundary: string;
}

export interface IndexManifest {
  index_version: string;
  model_version: string;
  dimension: number;
  dtype: string;
  metric: string;
  available_indexes: string[];
  approximate_is_proxy: boolean;
  item_ids: string[];
}

