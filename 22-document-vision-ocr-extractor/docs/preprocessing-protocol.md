# Preprocessing protocol

Three immutable profiles are exposed:

- `original-v1`: decoded image only; comparison baseline.
- `deskew-clahe-v1`: compatibility profile name for grayscale, median denoise, global
  histogram equalization and deskew check. It does not claim an OpenCV CLAHE implementation.
- `adaptive-threshold-v1`: grayscale, denoise and adaptive threshold.

The qualification fixture OCR intentionally keeps its sealed predictions across profiles;
therefore the current report does not claim a measured preprocessing improvement. A real
PaddleOCR qualification run must evaluate each profile on the same held-out documents before
one is promoted.
