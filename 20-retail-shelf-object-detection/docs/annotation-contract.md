# Annotation contract

- Internal box format: absolute `XYXY` in pixels as `[x1, y1, x2, y2]`.
- Origin: upper-left of the oriented RGB image.
- Valid bounds: `0 <= x1 < x2 <= width`, `0 <= y1 < y2 <= height`.
- One class only: `class_id=0`, `class_name=object`.
- YOLO conversion uses normalized center-x, center-y, width and height.
- Degenerate boxes are rejected; out-of-frame boxes must be clipped and revalidated.
- Inference responses return XYXY, class, confidence and stable detection index.

NMS is class-agnostic because the task has one class. Scores are sorted descending and candidates with IoU above the selected threshold are suppressed.
