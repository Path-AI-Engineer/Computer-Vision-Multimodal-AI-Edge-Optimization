# Model Card - Retail Shelf Detection Console

## Active artifact

- Model: `component-detector-qualification-v1.0.0`
- Profile: `qualification_smoke`
- Class: `object`
- Input: safe RGB JPEG, PNG or WebP.
- Output: XYXY boxes, confidence, visible count, thresholds and latency.

## Evidence boundary

The active detector is a deterministic connected-component qualification model trained on no
private or official data. It validates geometry, evaluation, API and UI behavior. It is not a
YOLO model and is not evidence of SKU-110K performance.

- Qualification mAP@[.50:.95]: 0.97815
- Qualification count MAE: 0.0
- Official test: `LOCKED_NOT_ACQUIRED`

## Responsible use

The visible count covers detections in one image. It does not identify SKUs, infer hidden stock,
estimate inventory, guarantee planogram compliance or support consequential retail decisions.
