# Experiment protocol

## Selection question

What quality and calibration gain do transfer learning and a pretrained Vision Transformer
provide over majority, HOG-linear and SmallCNN candidates under a controlled compute budget?

## Immutable rules

- primary selection metric: macro F1 on validation;
- secondary evidence: Top-1, Top-5, NLL, ECE, per-class recall, latency and artifact size;
- seed, manifests, resolution, augmentation and hardware are persisted per run;
- calibration is fit only on validation after candidate training;
- official test is evaluated once for an approved candidate and calibrator;
- unavailable execution produces an explicit status, never a fabricated metric.

## Candidate states in the qualification release

| Candidate | State | Evidence |
|---|---|---|
| Majority | Executed | Minimum reference in `model_comparison.json` |
| HOG + linear | Executed | Bundle, metrics, calibration and latency |
| SmallCNN | Implemented, not qualified | Shape-safe architecture and training loop |
| ResNet-18 frozen/fine-tuned | Protocol-ready, not executed | Adapter with declared weight enum |
| ViT-B/16 frozen | Protocol-ready, not executed | Adapter with declared weight enum |

The transfer-learning design follows the frozen-backbone and fine-tuning patterns documented in
the official PyTorch tutorial: <https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html>.
