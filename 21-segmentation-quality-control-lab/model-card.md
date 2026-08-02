# Model card — Small U-Net qualification bundle

## Status

`QUALIFICATION_ONLY`. The served checkpoint is a real Small U-Net trained on deterministic
procedural surfaces. It is not a KSDD2 benchmark result and the official test remains
`LOCKED_NOT_ACQUIRED`.

## Architecture and training

- Model: Small U-Net with two encoder/decoder levels and skip connections.
- Trainable parameters: 29481.
- Selected loss: bce_dice.
- Best epoch: 8.
- Best validation loss: 0.756044.
- Threshold selection: qualification validation only.

## Qualification evidence

- Macro Dice: 0.947943.
- Macro IoU: 0.911008.
- Pixel recall: 0.971197.
- Pixel PR AUC: 0.929261.
- Defective-piece recall: 1.0.
- False accept rate: 0.0.
- Local p50/p95 latency: 11.084 / 11.906 ms.

## Intended use

Education, software qualification and controlled demonstration of how pixel masks become an
auditable ACCEPT, REVIEW or REJECT decision.

## Limitations

- KSDD2 was not acquired or opened.
- Transfer U-Net and DeepLabV3 are protocol-ready but not executed.
- Procedural textures do not represent industrial variability.
- This model must not control a production line or support a safety guarantee.
