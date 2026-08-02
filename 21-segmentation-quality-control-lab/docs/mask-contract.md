# Mask contract

- Source masks are two-dimensional and binary: `0`, `1` or `255` on disk.
- Images and masks have identical height and width before transformation.
- Images use bilinear resize; labels use nearest-neighbor resize only.
- Spatial augmentation is paired for image and mask.
- Probabilities restore to original size with bilinear interpolation; binary masks use nearest.
- Pixel threshold selection uses validation data only; official test data cannot influence it.

Violations raise `MaskContractError`; labels are never interpolated as continuous values.
