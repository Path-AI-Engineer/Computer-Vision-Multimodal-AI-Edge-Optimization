# Metrics guide

## Detection quality

- **AP50 / AP75:** average precision at fixed IoU thresholds.
- **mAP@[.50:.95]:** mean AP over IoU 0.50 through 0.95 in 0.05 steps.
- **Precision / recall:** reported at IoU 0.50 for the persisted operating point.

## Operational count quality

- **Count MAE:** average absolute difference between predicted and visible truth count.
- **Count RMSE:** emphasizes scenes with larger count error.
- **Mean bias:** signed error; positive means systematic overcounting.

AP and count error answer different questions. A detector can localize imperfectly while producing a useful count, or produce plausible boxes while systematically miscounting. Both are required, alongside density slices and overlays.

The current 0.97815 qualification mAP and zero count MAE belong only to controlled procedural scenes. They are not SKU-110K benchmark claims.
