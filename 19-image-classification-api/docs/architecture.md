# Architecture

Pet Breed Classification Studio is split into five explicit paths:

1. `ml/data` owns labels, safe decoding, preprocessing contracts and dataset fixtures.
2. `ml/features`, `ml/models` and `ml/training` own classical and deep-learning candidates.
3. `ml/evaluation` generates metrics and calibration evidence from persisted arrays.
4. `ml/inference` loads an immutable artifact and returns a traceable prediction resource.
5. `backend` and `frontend` expose the product without reimplementing model logic.

The FastAPI process loads the approved bundle once during application lifespan. The React
application consumes HTTP responses and persisted evidence; it does not contain metric or
prediction fixtures. Docker sets `PET_STUDIO_ROOT=/app` so artifact resolution is independent
from the current working directory.

## Runtime flow

```text
image bytes
  -> safe decode and EXIF normalization
  -> RGB fit to 160 x 160
  -> HOG and channel statistics
  -> linear logits
  -> temperature scaling
  -> top-k and abstention
  -> versioned HTTP resource
```

## Deep candidate boundary

`SmallCNN`, `ResNet-18` and `ViT-B/16` adapters are implemented. Their benchmark states are
not `executed`, because the official dataset and declared ImageNet weights have not been run in
this qualification release. Grad-CAM is therefore unavailable for the selected HOG artifact.
