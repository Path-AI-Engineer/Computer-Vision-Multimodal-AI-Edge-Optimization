export type VariantStatus = "APPROVED_QUALIFICATION" | "EXPERIMENTAL_QUALIFICATION" | "NOT_RUN";

export interface QualityMetrics { macro_f1: number; top1_accuracy: number; top5_accuracy: number }
export interface LatencyMetrics { p50_ms: number; p90_ms: number; p95_ms: number; mean_ms: number; throughput_per_second: number; samples: number }
export interface Variant {
  variant_id: string; display_name: string; runtime: string; precision: string; optimization: string;
  status: VariantStatus; artifact_path: string | null; artifact_size_mb: number | null; parameters: number | null;
  effective_sparsity: number | null; quality: QualityMetrics | null; latency: LatencyMetrics | null;
  model_version: string; preprocessing_version: string; environment_id: string; claim_boundary: string;
}
export interface BenchmarkRow extends QualityMetrics { variant_id: string; display_name: string; runtime: string; precision: string; status: VariantStatus; p50_ms: number; p90_ms: number; p95_ms: number; throughput_per_second: number; size_mb: number; parameters: number; effective_sparsity: number; environment_id: string }
export interface BenchmarkSummary { benchmark_id: string; profile: string; batch_size: number; variants: BenchmarkRow[]; status: string; claim_boundary: string }
export interface ParetoReport { frontier: BenchmarkRow[]; recommendations: Record<string, string>; policy: string; status: string }
export interface Environment { environment_id: string; profile: string; hardware_model: string; architecture: string; os: string; python: string; numpy: string; execution_provider: string; threads: number; power_mode: string; batch_size: number; input_size: number[]; input_dtype: string; warmup_iterations: number; measured_iterations: number; energy: string; claim_boundary: string }
export interface ParityComparison { reference_variant: string; candidate_variant: string; samples: number; max_absolute_error: number; mean_absolute_error: number; top1_agreement: number; absolute_tolerance: number; passed: boolean }
export interface Sample { sample_id: string; label: string; class_id: number; split: string; image_url: string; checksum: string; source: string }
export interface Prediction { variant_id: string; sample_id: string; predictions: { label: string; probability: number }[]; observed_latency_ms: number; model_version: string; status: string }
export interface Readiness { status: string; bundle_id: string; approved_variants: number; sample_count: number; claim_boundary: string }
export interface PruningReport { variant_id: string; target_sparsity: number; effective_sparsity: number; observed_speedup: number; interpretation: string; status: string }
