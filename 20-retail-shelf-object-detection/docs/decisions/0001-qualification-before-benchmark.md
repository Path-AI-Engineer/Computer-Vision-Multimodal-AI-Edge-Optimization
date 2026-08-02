# 0001 - Qualification before benchmark

Status: Accepted

## Context

The product architecture, API and UI need executable evidence before a licensed retail dataset and trained weights are available. Inventing model results or silently downloading assets would break traceability.

## Decision

Ship a deterministic procedural qualification profile with a real connected-component detector. Persist its predictions, metrics, overlays and bundle hash. Keep SKU-110K, YOLO and Faster R-CNN states explicit and unexecuted.

## Consequences

- The full product workflow can be tested end to end now.
- Qualification metrics cannot be used as retail benchmark evidence.
- Version 1.0.0 remains a release candidate until the official benchmark path is completed.
