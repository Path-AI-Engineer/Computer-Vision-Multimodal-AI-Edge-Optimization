# OCR contract

Each OCR line contains:

- stable `token_id`;
- raw `text` exactly as recognized;
- confidence in `[0, 1]`;
- pixel box `[x1, y1, x2, y2]`;
- zero-based `line_index`.

The sealed `annotated-fixture-v1` adapter provides reproducible qualification predictions.
It is not callable for arbitrary files. `paddleocr-v3` is the optional real upload adapter;
its dependencies are isolated in `requirements-ocr.txt` because the lightweight portfolio
runtime does not claim that capability.

Reading order sorts lines by vertical then horizontal position. Raw OCR remains immutable
through normalization and operator review.
