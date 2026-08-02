# Model Card — Pet Breed Classification Studio

## Model

- Version: `hog-linear-qualification-v1.0.0`
- Artifact: `pet-studio-qualification-v1`
- Input: JPEG, PNG or WebP converted to RGB and fitted to 160 × 160.
- Output: 37 Oxford-IIIT Pet breed labels with calibrated qualification probabilities.

## Evidence boundary

This is a **qualification bundle**, trained on deterministic procedural images. It proves
the data, feature, calibration, API and product path. It is not an Oxford-IIIT Pet model
and its metric values must not be presented as breed-recognition performance.

The official Oxford test split remains `LOCKED_NOT_ACQUIRED`.

## Qualification metrics

- Macro F1: 1.0
- Top-1 accuracy: 1.0
- Top-5 accuracy: 1.0
- ECE: 0.03538
- Local p50 latency: 4.006 ms
- Local p95 latency: 4.541 ms

## Intended use

Engineering validation, portfolio demonstration and controlled study of inference
contracts. It is not intended for veterinary, health, identity or safety decisions.

## Limitations

- Procedural qualification imagery does not represent real pet photography.
- Confidence is not a correctness guarantee.
- HOG has no Grad-CAM surface.
- Species and breed may be wrong under background, crop or lighting shifts.
- ResNet-18 and ViT-B/16 remain protocol-ready but unexecuted in this bundle.
