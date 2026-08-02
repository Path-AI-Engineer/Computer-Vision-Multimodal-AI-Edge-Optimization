# Inspection policy

Segmentation and operational disposition are separate:

1. Small U-Net emits a probability per pixel.
2. Pixel threshold `0.80` creates the qualification mask.
3. Components smaller than six pixels are removed.
4. Retained area is divided by original image area.
5. The piece becomes `ACCEPT` below `0.001`, `REVIEW` below `0.012`, or `REJECT` otherwise.

These are demonstration values, not an industrial safety specification. A production owner
must calibrate them against defect costs, throughput and measurement capability.
