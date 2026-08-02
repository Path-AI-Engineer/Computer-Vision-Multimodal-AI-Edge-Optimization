export type FieldName = "company" | "date" | "address" | "total";

export interface Sample {
  sample_id: string;
  image_url: string;
  width: number;
  height: number;
  locale: string;
}

export interface OcrToken {
  token_id: string;
  text: string;
  confidence: number;
  box: [number, number, number, number];
  line_index: number;
}

export interface FieldEvidence {
  field: FieldName;
  raw_value: string | null;
  normalized_value: string | null;
  confidence: number;
  review_required: boolean;
  reason_codes: string[];
  token_ids: string[];
  boxes: Array<[number, number, number, number]>;
}

export interface Extraction {
  request_id: string;
  sample_id: string | null;
  source_name: string;
  source_kind: string;
  created_at: string;
  pipeline_version: string;
  preprocessing_profile: string;
  ocr_adapter: string;
  width: number;
  height: number;
  image_url: string | null;
  tokens: OcrToken[];
  fields: FieldEvidence[];
  warnings: string[];
  expires_in_seconds: number;
}

export interface EvaluationSummary {
  evidence_scope: string;
  documents: number;
  ocr: {
    cer: number;
    wer: number;
    line_exact_match: number;
    localization_precision_iou_0_5: number;
    localization_recall_iou_0_5: number;
  };
  end_to_end: {
    normalized_field_exact_match: number;
    document_exact_match: number;
    review_rate: number;
    mean_field_confidence: number;
  };
  oracle_ocr: { normalized_field_exact_match: number; document_exact_match: number };
  interpretation: string;
}

export interface ErrorEntry {
  sample_id: string;
  field: FieldName;
  expected: string;
  predicted: string | null;
  confidence: number;
  review_required: boolean;
  reason_codes: string[];
}

export interface ModelRecord {
  bundle_id: string;
  release: string;
  status: string;
  ocr: string;
  upload_ocr: string;
  extractor: string;
  evaluation_protocol: string;
  official_benchmark: boolean;
  evidence_boundary: Record<string, string>;
}
