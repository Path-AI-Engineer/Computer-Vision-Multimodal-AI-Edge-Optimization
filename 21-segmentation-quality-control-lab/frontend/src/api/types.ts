export type Decision = "ACCEPT" | "REVIEW" | "REJECT";

export interface Sample {
  sample_id: string;
  image_url: string;
  ground_truth_mask_url: string;
  defective: boolean;
  defect_area_px: number;
  defect_area_ratio: number;
}

export interface Inspection {
  request_id: string;
  model_version: string;
  mask_probability_uri: string;
  binary_mask_uri: string;
  baseline_mask_uri: string;
  image_uri: string;
  overlay_uri: string;
  baseline_overlay_uri: string;
  defect_detected: boolean;
  defect_area_px: number;
  defect_area_ratio: number;
  component_count: number;
  largest_component_px: number;
  pixel_threshold: number;
  piece_threshold: number;
  decision: Decision;
  baseline_decision: Decision;
  latency_ms: number;
  warnings: string[];
}

export interface PixelMetrics {
  macro_dice: number;
  macro_iou: number;
  macro_precision: number;
  macro_recall: number;
  pr_auc?: number;
}

export interface PieceMetrics {
  defect_precision: number;
  defect_recall: number;
  defect_f1: number;
  false_accept_rate: number;
  false_reject_rate: number;
}

export interface EvaluationSummary {
  profile: string;
  selected_model: string;
  selected_model_version: string;
  selection_split: string;
  official_test_status: string;
  images: number;
  defective_images: number;
  clean_images: number;
  pixel_threshold: number;
  piece_threshold: number;
  pixel_metrics: PixelMetrics;
  piece_metrics: PieceMetrics;
  latency: { p50_ms: number; p95_ms: number; environment: string; warning: string };
  warning: string;
}

export interface ThresholdPoint extends PixelMetrics {
  threshold: number;
}

export interface Candidate {
  model_id: string;
  status: string;
  selected?: boolean;
  reason?: string;
  pixel_metrics?: PixelMetrics;
  piece_metrics?: PieceMetrics;
}

export interface ModelComparison {
  selection_scope: string;
  candidates: Candidate[];
}

export interface ErrorGallery {
  errors: Array<{
    sample_id: string;
    actual_defect: boolean;
    predicted_defect: boolean;
    decision: Decision;
    error_type: string;
  }>;
  false_accepts: number;
  false_rejects: number;
  scope: string;
}

export interface CurrentModel {
  model_id: string;
  model_version: string;
  architecture: string;
  checkpoint_sha256: string;
  input_size: number[];
  pixel_threshold: number;
  inspection_policy: {
    review_area_ratio: number;
    reject_area_ratio: number;
    minimum_component_area_px: number;
  };
  evidence_profile: string;
  official_test_status: string;
  limitations: string[];
  training: {
    best_epoch: number;
    best_validation_loss: number;
    parameters: number;
    training_seconds: number;
    history: Array<{ epoch: number; train_loss: number; validation_loss: number }>;
  };
}

