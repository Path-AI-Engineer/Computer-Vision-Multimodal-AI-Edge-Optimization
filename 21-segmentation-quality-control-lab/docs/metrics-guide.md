# Metrics guide

- **Dice and IoU** measure spatial agreement; clean/clean pairs score 1.
- **Pixel precision and recall** separate false alarms from missed defect pixels.
- **PR AUC** summarizes the imbalanced pixel-ranking problem.
- **Piece recall** measures defective pieces routed away from acceptance.
- **False-accept rate** is the share of defective pieces incorrectly accepted.
- **False-reject rate** is the share of clean pieces unnecessarily held or rejected.
- **Latency p50/p95** describes qualification hardware and is not a service SLA.

Pixel metrics cannot replace piece metrics: localization and operational risk are distinct.
